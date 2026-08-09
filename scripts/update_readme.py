#!/usr/bin/env python3
"""
Updates live GitHub repository metrics (stars and forks) for featured projects.
Uses standard library urllib/json only for zero third-party dependencies.
Idempotent and resilient to network/API failures.
"""

import json
import logging
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

FEATURED_REPOS = [
    "ashfromsky/acquiremock",
    "ashfromsky/yaradb",
    "ashfromsky/helix",
]


def fetch_repo_metrics(repo_slug: str, token: Optional[str] = None) -> Optional[Dict[str, int]]:
    """Fetches stargazers_count and forks_count for a repo from GitHub REST API."""
    url = f"https://api.github.com/repos/{repo_slug}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Python-urllib/ashfromsky-profile")
    
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0)
                }
    except Exception as e:
        logger.warning(f"Could not fetch metrics for {repo_slug}: {e}. Retaining existing metrics.")
    
    return None


def update_profile_config(config_path: Path, token: Optional[str] = None) -> bool:
    """Fetches metrics for featured repositories and updates config/profile.json."""
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return False

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    changed = False
    projects = config.get("projects", [])

    for proj in projects:
        repo_slug = proj.get("repo")
        if not repo_slug:
            continue

        metrics = fetch_repo_metrics(repo_slug, token=token)
        if metrics is not None:
            old_stars = proj.get("stars")
            old_forks = proj.get("forks")
            new_stars = metrics["stars"]
            new_forks = metrics["forks"]

            if old_stars != new_stars or old_forks != new_forks:
                proj["stars"] = new_stars
                proj["forks"] = new_forks
                changed = True
                logger.info(f"Updated {repo_slug}: stars={new_stars} (was {old_stars}), forks={new_forks} (was {old_forks})")
            else:
                logger.info(f"No metric changes for {repo_slug}: stars={new_stars}, forks={new_forks}")

    if changed:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.write("\n")
        logger.info(f"Saved updated metrics to {config_path}")

    return changed


def update_readme_markers(readme_path: Path, config_path: Path) -> bool:
    """Updates README.md marker section if markers exist."""
    if not readme_path.exists():
        return False

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    metrics_summary_lines = []
    for proj in config.get("projects", []):
        if "stars" in proj and "forks" in proj:
            name = proj.get("name", "")
            stars = proj.get("stars", 0)
            forks = proj.get("forks", 0)
            metrics_summary_lines.append(f"<!-- {name}: ★ {stars} ⑂ {forks} -->")

    marker_content = "\n".join(metrics_summary_lines)

    with open(readme_path, "r", encoding="utf-8") as f:
        readme_text = f.read()

    start_marker = "<!-- REPO_METRICS_START -->"
    end_marker = "<!-- REPO_METRICS_END -->"

    if start_marker in readme_text and end_marker in readme_text:
        pattern = f"{start_marker}.*?{end_marker}"
        replacement = f"{start_marker}\n{marker_content}\n{end_marker}"
        import re
        new_readme = re.sub(pattern, replacement, readme_text, flags=re.DOTALL)
        if new_readme != readme_text:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(new_readme)
            logger.info(f"Updated marker section in {readme_path}")
            return True

    return False


def main() -> None:
    config_path = PROJECT_ROOT / "config" / "profile.json"
    readme_path = PROJECT_ROOT / "README.md"
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("PROFILE_TOKEN")

    config_changed = update_profile_config(config_path, token=token)
    readme_changed = update_readme_markers(readme_path, config_path)

    # Trigger profile update to re-render dark_mode.svg and light_mode.svg
    from scripts.update_profile import main as run_update_profile
    run_update_profile()

    logger.info("README and Profile SVG update completed successfully.")


if __name__ == "__main__":
    main()
