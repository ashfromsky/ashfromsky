# How It Works — Neofetch GitHub Profile Generator

This repository dynamically generates a terminal/neofetch-style SVG card for **ashfromsky** (Tymofii Shchur). It includes an original ASCII portrait, dynamic dot alignment, persistent commit caching, and theme auto-switching between dark and light modes.

---

## Architecture Overview

```
.
├── .github/workflows/profile.yml  # Daily GitHub Action workflow (04:00 UTC & dispatch)
├── assets/
│   ├── ascii_dark.txt             # ASCII portrait rendered for dark theme
│   └── ascii_light.txt            # ASCII portrait rendered for light theme
├── cache/
│   └── stats_cache.json           # Committed persistent repo commit & LOC cache
├── config/
│   ├── profile.json               # Personal identity & technology stack metadata
│   └── archived_stats.json        # Legacy / archived statistics configuration
├── input/
│   └── profile.jpg                # Source photograph used for ASCII converter
├── scripts/
│   ├── generate_ascii.py          # One-time build tool: Image -> ASCII
│   └── update_profile.py          # Core updater script: API fetch -> SVG render
├── src/
│   ├── ascii_converter.py         # Contrast normalization & monospace ASCII generator
│   ├── github_client.py           # GitHub GraphQL v4 & REST client with pagination
│   ├── stats_calculator.py        # Uptime, stargazer total, LOC & cache manager
│   └── svg_renderer.py            # XML parser, dot aligner & SVG template engine
├── templates/
│   ├── dark_mode.template.svg     # Dark mode SVG layout with element IDs
│   └── light_mode.template.svg    # Light mode SVG layout with element IDs
├── tests/
│   ├── fixtures/github_stats.json # Offline test fixture
│   └── test_profile.py            # Automated test suite
├── dark_mode.svg                  # Output SVG rendered for dark mode
├── light_mode.svg                 # Output SVG rendered for light mode
└── README.md                      # Minimal profile Markdown with theme-switching <picture>
```

---

## How Statistics Are Calculated

1. **Uptime (Account Age)**:
   - Calculated dynamically as `X years, Y months, Z days` from the user's GitHub account creation timestamp (`createdAt`). If `birth_date` is specified in `config/profile.json`, it overrides this behavior.

2. **Repositories**:
   - Total number of non-fork repositories owned by `ashfromsky`.

3. **Stars**:
   - Total stargazer count summed across all non-fork repositories owned by `ashfromsky`.

4. **Followers**:
   - Total follower count returned by GitHub.

5. **Contributed Repositories**:
   - Unique count of accessible repositories (owned, collaborator, organization member) where the scanner verified at least one commit authored by `ashfromsky`.

6. **Commits & Lines of Code (LOC)**:
   - Evaluated across the default branch history of scanned repositories.
   - Only commits whose GitHub author ID matches `ashfromsky`'s account ID are counted.
   - `added_lines` and `deleted_lines` are summed for authored commits.
   - Net LOC is rendered as: `net_LOC ( additions++, deletions-- )`.

---

## Caching Semantics & Default-Branch Limitation

- Commit history scanning can be computationally intensive. The system maintains a persistent cache in `cache/stats_cache.json` containing:
  ```json
  {
    "repositories": {
      "ashfromsky/acquiremock": {
        "head_oid": "4b825dc642cb6eb9a060e54bf8d69288fbee4904",
        "my_commits": 42,
        "additions": 14200,
        "deletions": 1800
      }
    }
  }
  ```
- **Cache Check**: For each repository, the script checks the default branch HEAD OID. If unchanged, cached figures are reused instantly. If the HEAD OID changes or a new repository is added, only that repository is rescanned.
- **Default Branch Limitation**: Metrics scan default branches (e.g. `main` or `master`) to ensure deterministic performance across runs.

---

## Required Environment Variables & Secrets

| Environment Variable | Where Used | Description |
| :--- | :--- | :--- |
| `PROFILE_TOKEN` | GitHub Secrets / Local CLI | Fine-grained PAT with read access to user data and private/collaborator repositories for complete LOC scanning. |
| `GITHUB_TOKEN` | GitHub Actions | Automatically provided by GitHub Actions for repository workflow execution and public API querying. |

### How to Create `PROFILE_TOKEN`

1. Go to **GitHub Settings** -> **Developer Settings** -> **Personal Access Tokens** -> **Fine-grained tokens**.
2. Click **Generate new token**.
3. Set **Repository access** to *All repositories* (or selected private repositories you wish to include in commit metrics).
4. Grant **Read-only** access to:
   - **Contents** (Read)
   - **Metadata** (Read)
5. Copy the generated token and go to your profile repository (`ashfromsky/ashfromsky`).
6. Navigate to **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**.
7. Name: `PROFILE_TOKEN` | Value: `<paste-token>`.

---

## Local Execution Commands

### 1. Regenerating Profile SVGs

- **Local Live Update** (uses `PROFILE_TOKEN` env var if available, or falls back to public REST API):
  ```bash
  python scripts/update_profile.py
  ```

- **Offline Fixture Update** (bypasses GitHub API completely):
  ```bash
  python scripts/update_profile.py --fixture tests/fixtures/github_stats.json
  ```

### 2. Regenerating ASCII Portrait

If you update `input/profile.jpg`, regenerate the ASCII text files by running:
```bash
python scripts/generate_ascii.py --width 40 --height 25
```

### 3. Running Automated Tests

```bash
pytest
```

---

## GitHub Actions Automation

The workflow `.github/workflows/profile.yml` runs automatically:
- **Daily** at `04:00 UTC`.
- **On Push** to the `main` branch when templates, config, or scripts change.
- **Manually** via `workflow_dispatch`.

### How to Manually Trigger the Workflow

1. Go to your repository on GitHub: `https://github.com/ashfromsky/ashfromsky`.
2. Click the **Actions** tab.
3. Select **Profile Refresh** from the left sidebar.
4. Click **Run workflow** -> **Run workflow**.
