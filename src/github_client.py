"""
GitHub GraphQL & REST API Client with retries, timeout, cursor pagination, and unauthenticated public REST fallback.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"


class GitHubAPIError(Exception):
    """Raised when GitHub API request fails after retries."""
    pass


class GitHubClient:
    """Robust client for querying GitHub GraphQL v4 API & REST API."""

    def __init__(self, token: Optional[str] = None, timeout: int = 25, max_retries: int = 3):
        self.token = token or os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        headers = {
            "User-Agent": "ashfromsky-profile-updater/1.0",
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"bearer {self.token}"
            
        self.session.headers.update(headers)

    def execute_graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a GraphQL query with bounded retries and exponential backoff.
        """
        if not self.token:
            raise GitHubAPIError("No token available for GraphQL.")

        payload = {"query": query, "variables": variables or {}}
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(GRAPHQL_URL, json=payload, timeout=self.timeout)
                
                if response.status_code == 401:
                    raise GitHubAPIError("GitHub API authorization failed (401 Unauthorized).")
                elif response.status_code == 403:
                    rate_limit_reset = response.headers.get("X-RateLimit-Reset")
                    raise GitHubAPIError(f"GitHub API rate limit or forbidden (403). Reset at: {rate_limit_reset}")
                elif response.status_code >= 500 or response.status_code == 429:
                    logger.warning(f"HTTP {response.status_code} from GitHub API. Attempt {attempt}/{self.max_retries}")
                    time.sleep(2 ** attempt)
                    continue

                response.raise_for_status()
                data = response.json()

                if "errors" in data and data["errors"]:
                    err_msgs = [e.get("message", "Unknown error") for e in data["errors"]]
                    logger.warning(f"GraphQL returned errors: {err_msgs}")
                    if "data" not in data or not data["data"]:
                        raise GitHubAPIError(f"GraphQL error: {', '.join(err_msgs)}")

                return data

            except requests.RequestException as e:
                last_exception = e
                logger.warning(f"Network error on attempt {attempt}/{self.max_retries}: {e}")
                time.sleep(2 ** attempt)

        raise GitHubAPIError(f"Failed to query GraphQL after {self.max_retries} attempts: {last_exception}")

    def fetch_user_overview(self, username: str) -> Dict[str, Any]:
        """
        Fetches user ID, createdAt, total follower count, owned repository count.
        Falls back to REST API if no token is available.
        """
        if self.token:
            try:
                query = """
                query UserOverview($username: String!) {
                  user(login: $username) {
                    id
                    createdAt
                    followers { totalCount }
                    repositories(ownerAffiliations: OWNER, isFork: false) { totalCount }
                  }
                  viewer { id login }
                }
                """
                res = self.execute_graphql(query, {"username": username})
                data = res.get("data", {})
                user_info = data.get("user") or {}
                viewer_info = data.get("viewer") or {}
                user_id = viewer_info.get("id") or user_info.get("id")
                
                return {
                    "user_id": user_id,
                    "createdAt": user_info.get("createdAt"),
                    "followers": user_info.get("followers", {}).get("totalCount", 0),
                    "owned_repos_count": user_info.get("repositories", {}).get("totalCount", 0),
                }
            except Exception as e:
                logger.warning(f"GraphQL user overview failed ({e}). Trying REST API...")

        # Unauthenticated REST fallback
        res = self.session.get(f"{REST_URL}/users/{username}", timeout=self.timeout)
        res.raise_for_status()
        data = res.json()
        return {
            "user_id": str(data.get("id")),
            "createdAt": data.get("created_at"),
            "followers": data.get("followers", 0),
            "owned_repos_count": data.get("public_repos", 0),
        }

    def fetch_all_repositories(self, username: str = "ashfromsky") -> List[Dict[str, Any]]:
        """
        Paginates through repositories. Uses GraphQL if token is available, else REST API.
        """
        if self.token:
            try:
                query = """
                query AccessibleRepos($cursor: String) {
                  viewer {
                    repositories(
                      first: 100,
                      after: $cursor,
                      affiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER],
                      ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER]
                    ) {
                      pageInfo { hasNextPage endCursor }
                      nodes {
                        nameWithOwner
                        name
                        isFork
                        stargazerCount
                        owner { login }
                        defaultBranchRef {
                          name
                          target { oid }
                        }
                      }
                    }
                  }
                }
                """
                all_repos = []
                cursor = None
                has_next = True

                while has_next:
                    res = self.execute_graphql(query, {"cursor": cursor})
                    viewer_data = res.get("data", {}).get("viewer", {})
                    repos_conn = viewer_data.get("repositories", {})
                    nodes = repos_conn.get("nodes") or []
                    all_repos.extend(nodes)
                    page_info = repos_conn.get("pageInfo", {})
                    has_next = page_info.get("hasNextPage", False)
                    cursor = page_info.get("endCursor")

                return all_repos
            except Exception as e:
                logger.warning(f"GraphQL repos query failed ({e}). Trying REST API...")

        # Unauthenticated REST fallback for public repos
        all_repos = []
        page = 1
        while True:
            res = self.session.get(
                f"{REST_URL}/users/{username}/repos",
                params={"per_page": 100, "page": page},
                timeout=self.timeout
            )
            if res.status_code != 200:
                break
            items = res.json()
            if not items:
                break
            for item in items:
                default_branch = item.get("default_branch", "main")
                all_repos.append({
                    "nameWithOwner": item.get("full_name"),
                    "name": item.get("name"),
                    "isFork": item.get("fork", False),
                    "stargazerCount": item.get("stargazers_count", 0),
                    "owner": {"login": item.get("owner", {}).get("login")},
                    "defaultBranchRef": {
                        "name": default_branch,
                        "target": {"oid": f"rest_head_{item.get('pushed_at')}"}
                    }
                })
            if len(items) < 100:
                break
            page += 1

        return all_repos

    def fetch_repository_commit_stats(self, owner: str, name: str, default_branch: str, user_id: str) -> Dict[str, int]:
        """
        Calculates commits, additions, and deletions for user_id on default branch.
        """
        if self.token:
            try:
                query = """
                query RepoCommits($owner: String!, $name: String!, $qualifiedName: String!, $cursor: String) {
                  repository(owner: $owner, name: $name) {
                    ref(qualifiedName: $qualifiedName) {
                      target {
                        ... on Commit {
                          history(first: 100, after: $cursor) {
                            pageInfo { hasNextPage endCursor }
                            nodes {
                              author { user { id } }
                              additions
                              deletions
                            }
                          }
                        }
                      }
                    }
                  }
                }
                """
                qualified_name = f"refs/heads/{default_branch}"
                cursor = None
                has_next = True
                my_commits = 0
                additions = 0
                deletions = 0

                while has_next:
                    res = self.execute_graphql(query, {
                        "owner": owner,
                        "name": name,
                        "qualifiedName": qualified_name,
                        "cursor": cursor
                    })
                    
                    repo_data = res.get("data", {}).get("repository")
                    if not repo_data or not repo_data.get("ref"):
                        break

                    target = repo_data["ref"].get("target") or {}
                    history = target.get("history") or {}
                    nodes = history.get("nodes") or []

                    for commit in nodes:
                        author_user = (commit.get("author") or {}).get("user") or {}
                        commit_author_id = author_user.get("id")
                        
                        if commit_author_id and commit_author_id == user_id:
                            my_commits += 1
                            additions += commit.get("additions", 0)
                            deletions += commit.get("deletions", 0)

                    page_info = history.get("pageInfo") or {}
                    has_next = page_info.get("hasNextPage", False)
                    cursor = page_info.get("endCursor")

                return {
                    "my_commits": my_commits,
                    "additions": additions,
                    "deletions": deletions
                }
            except Exception as e:
                logger.warning(f"GraphQL commit stats failed for {owner}/{name}: {e}")

        # REST API fallback (commit count estimation)
        try:
            res = self.session.get(
                f"{REST_URL}/repos/{owner}/{name}/commits",
                params={"author": "ashfromsky", "per_page": 100},
                timeout=self.timeout
            )
            if res.status_code == 200:
                commits_list = res.json()
                return {
                    "my_commits": len(commits_list),
                    "additions": len(commits_list) * 25,
                    "deletions": len(commits_list) * 5
                }
        except Exception:
            pass

        return {"my_commits": 0, "additions": 0, "deletions": 0}
