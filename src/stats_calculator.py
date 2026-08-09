"""
Statistics calculator and persistent caching manager.
"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dateutil.relativedelta import relativedelta

from src.github_client import GitHubClient

logger = logging.getLogger(__name__)


def calculate_uptime(created_at_iso: str, birth_date_iso: Optional[str] = None) -> str:
    """
    Calculates Uptime as years, months, days relative to current UTC date.
    Uses birth_date_iso if provided, otherwise defaults to GitHub account age (created_at_iso).
    """
    start_date_str = birth_date_iso if birth_date_iso else created_at_iso
    if not start_date_str:
        return "Unknown"

    try:
        if "T" in start_date_str:
            start_dt = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
        else:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            
        now_dt = datetime.now(timezone.utc)
        diff = relativedelta(now_dt, start_dt)

        parts = []
        if diff.years > 0:
            parts.append(f"{diff.years} {'year' if diff.years == 1 else 'years'}")
        if diff.months > 0:
            parts.append(f"{diff.months} {'month' if diff.months == 1 else 'months'}")
        if diff.days > 0 or len(parts) == 0:
            parts.append(f"{diff.days} {'day' if diff.days == 1 else 'days'}")

        return ", ".join(parts)
    except Exception as e:
        logger.error(f"Error calculating uptime from {start_date_str}: {e}")
        return "Unknown"


class CacheManager:
    """Manages persistent JSON caching for repository statistics."""

    def __init__(self, cache_file_path: Path):
        self.cache_file_path = cache_file_path
        self.data: Dict[str, Any] = {"repositories": {}}
        self.load()

    def load(self) -> None:
        if self.cache_file_path.exists():
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    if "repositories" not in self.data:
                        self.data["repositories"] = {}
            except Exception as e:
                logger.warning(f"Failed to load cache file {self.cache_file_path}: {e}. Starting fresh cache.")
                self.data = {"repositories": {}}

    def save(self) -> None:
        self.cache_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_repo_cache(self, name_with_owner: str) -> Optional[Dict[str, Any]]:
        return self.data["repositories"].get(name_with_owner)

    def update_repo_cache(self, name_with_owner: str, head_oid: str, my_commits: int, additions: int, deletions: int) -> None:
        self.data["repositories"][name_with_owner] = {
            "head_oid": head_oid,
            "my_commits": my_commits,
            "additions": additions,
            "deletions": deletions
        }

    def prune(self, active_repo_names: List[str]) -> None:
        active_set = set(active_repo_names)
        cached_keys = list(self.data["repositories"].keys())
        for key in cached_keys:
            if key not in active_set:
                del self.data["repositories"][key]


def fetch_single_repo(repo: Dict[str, Any], user_id: str, github_client: GitHubClient, cache: CacheManager) -> Optional[Dict[str, Any]]:
    name_with_owner = repo.get("nameWithOwner")
    if not name_with_owner:
        return None

    default_branch_ref = repo.get("defaultBranchRef")
    if not default_branch_ref:
        return None

    branch_name = default_branch_ref.get("name")
    target_oid = (default_branch_ref.get("target") or {}).get("oid")
    
    if not branch_name or not target_oid:
        return None

    cached_entry = cache.get_repo_cache(name_with_owner)
    
    if cached_entry and cached_entry.get("head_oid") == target_oid:
        return {
            "name": name_with_owner,
            "head_oid": target_oid,
            "my_commits": cached_entry.get("my_commits", 0),
            "additions": cached_entry.get("additions", 0),
            "deletions": cached_entry.get("deletions", 0),
            "from_cache": True
        }

    owner, name = name_with_owner.split("/")
    stats = github_client.fetch_repository_commit_stats(owner, name, branch_name, user_id)
    return {
        "name": name_with_owner,
        "head_oid": target_oid,
        "my_commits": stats["my_commits"],
        "additions": stats["additions"],
        "deletions": stats["deletions"],
        "from_cache": False
    }


def fetch_and_calculate_stats(
    github_client: GitHubClient,
    username: str,
    cache_path: Path,
    profile_config: Dict[str, Any],
    archived_stats: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    archived = archived_stats or {}
    archived_commits = archived.get("archived_commits", 0)
    archived_additions = archived.get("archived_additions", 0)
    archived_deletions = archived.get("archived_deletions", 0)
    archived_repos = archived.get("archived_repos", 0)
    archived_stars = archived.get("archived_stars", 0)

    overview = github_client.fetch_user_overview(username)
    user_id = overview["user_id"]
    created_at = overview["createdAt"]
    followers = overview["followers"]

    uptime = calculate_uptime(created_at, profile_config.get("birth_date"))

    all_repos = github_client.fetch_all_repositories()

    owned_repos = [r for r in all_repos if r.get("owner", {}).get("login", "").lower() == username.lower() and not r.get("isFork")]
    owned_repos_count = len(owned_repos) + archived_repos
    total_stars = sum(r.get("stargazerCount", 0) for r in owned_repos) + archived_stars

    cache = CacheManager(cache_path)
    active_repo_names = [r["nameWithOwner"] for r in all_repos if "nameWithOwner" in r]
    
    total_commits = archived_commits
    total_additions = archived_additions
    total_deletions = archived_deletions
    contributed_repos_count = 0

    # Multi-threaded fetch for fast parallel scans
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_single_repo, repo, user_id, github_client, cache) for repo in all_repos]
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    for item in results:
        cache.update_repo_cache(item["name"], item["head_oid"], item["my_commits"], item["additions"], item["deletions"])
        if item["my_commits"] > 0:
            contributed_repos_count += 1
            total_commits += item["my_commits"]
            total_additions += item["additions"]
            total_deletions += item["deletions"]

    cache.prune(active_repo_names)
    cache.save()

    net_loc = total_additions - total_deletions

    return {
        "uptime": uptime,
        "repos": owned_repos_count,
        "contributed_repos": contributed_repos_count,
        "stars": total_stars,
        "followers": followers,
        "commits": total_commits,
        "loc_net": net_loc,
        "loc_additions": total_additions,
        "loc_deletions": total_deletions,
    }
