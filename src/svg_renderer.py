"""
SVG Template Renderer and XML-safe Dot Alignment Engine.
"""

import html
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def format_number(val: int) -> str:
    """Formats an integer with comma thousand separators (e.g., 1,234,567)."""
    return f"{val:,}"


def adjust_dots(target_length: int, text_length: int) -> str:
    """
    Computes a dot string of varying length so that key + dots + value stays aligned.
    """
    needed_dots = max(1, target_length - text_length)
    return "." * needed_dots + " "


class SVGRenderer:
    """Renders final dark and light SVG files from templates and stats."""

    def __init__(self, template_path: Path):
        self.template_path = template_path

    def render(
        self,
        stats: Dict[str, Any],
        profile_config: Dict[str, Any],
        ascii_lines: List[str],
        output_path: Path
    ) -> None:
        """
        Loads template, updates ASCII text, stats text elements, dot alignments, and writes to output_path.
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"SVG template not found: {self.template_path}")

        # Read template as text to avoid namespace mangling during simple text replacement
        with open(self.template_path, "r", encoding="utf-8") as f:
            svg_content = f.read()

        # Parse XML tree to update element content strictly by ID
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        tree = ET.ElementTree(ET.fromstring(svg_content))
        root = tree.getroot()

        # Helper to set element text by id
        def set_text(element_id: str, new_text: str) -> None:
            elem = root.find(f".//*[@id='{element_id}']")
            if elem is not None:
                elem.text = new_text

        # 1. Update ASCII lines block
        for idx in range(len(ascii_lines)):
            set_text(f"ascii_line_{idx}", ascii_lines[idx])

        # 2. Update Static Profile Fields if configured
        if "os" in profile_config:
            set_text("os_val", ", ".join(profile_config["os"]))
        if "location" in profile_config:
            set_text("host_val", profile_config["location"])
        if "title" in profile_config:
            set_text("kernel_val", profile_config["title"])
        if "ide" in profile_config:
            set_text("ide_val", ", ".join(profile_config["ide"]))

        if "languages" in profile_config:
            set_text("stack_lang_val", ", ".join(profile_config["languages"]))
        if "backend" in profile_config:
            set_text("stack_backend_val", ", ".join(profile_config["backend"]))
        if "data" in profile_config:
            set_text("stack_data_val", ", ".join(profile_config["data"]))
        if "ai" in profile_config:
            set_text("stack_ai_val", ", ".join(profile_config["ai"]))
        if "infra" in profile_config:
            set_text("stack_infra_val", ", ".join(profile_config["infra"]))
        if "interests" in profile_config:
            set_text("interests_val", ", ".join(profile_config["interests"]))

        if "projects" in profile_config:
            for idx, proj in enumerate(profile_config["projects"], start=1):
                name = proj.get("name", "")
                desc = proj.get("desc", "")
                base = f"{name} — {desc}" if desc else proj.get("val", "")
                
                if "stars" in proj and "forks" in proj and proj["stars"] is not None:
                    stars = proj["stars"]
                    forks = proj["forks"]
                    metrics_str = f"★ {stars:<3} ⑂ {forks}"
                    pad_len = max(2, 41 - len(base))
                    val_str = f"{base}{' ' * pad_len}{metrics_str}"
                else:
                    val_str = base
                
                set_text(f"proj{idx}_val", val_str)

        if "email" in profile_config:
            set_text("email_val", profile_config["email"])
        if "linkedin" in profile_config:
            set_text("linkedin_val", profile_config["linkedin"])
        if "username" in profile_config:
            set_text("github_val", profile_config["username"])

        # 3. Update Dynamic Statistics & Dynamic Dotted Alignment
        # Uptime / Account Age
        uptime_str = str(stats.get("uptime", "Unknown"))
        set_text("account_age", uptime_str)
        set_text("account_age_dots", "." * 21 + " ")

        # Repos & Contributed
        repos_num = stats.get("repos", 0)
        contrib_num = stats.get("contributed_repos", 0)
        repos_str = format_number(repos_num)
        contrib_str = format_number(contrib_num)
        
        set_text("repo_data", repos_str)
        set_text("contrib_data", contrib_str)
        set_text("repo_data_dots", adjust_dots(10, len(repos_str)))

        # Stars
        stars_num = stats.get("stars", 0)
        stars_str = format_number(stars_num)
        set_text("star_data", stars_str)
        set_text("star_data_dots", adjust_dots(10, len(stars_str)))

        # Commits
        commits_num = stats.get("commits", 0)
        commits_str = format_number(commits_num)
        set_text("commit_data", commits_str)
        set_text("commit_data_dots", adjust_dots(18, len(commits_str)))

        # Followers
        followers_num = stats.get("followers", 0)
        followers_str = format_number(followers_num)
        set_text("follower_data", followers_str)
        set_text("follower_data_dots", adjust_dots(10, len(followers_str)))

        # Lines of Code (net_loc, additions, deletions)
        loc_net = stats.get("loc_net", 0)
        loc_add = stats.get("loc_additions", 0)
        loc_del = stats.get("loc_deletions", 0)

        loc_net_str = format_number(loc_net)
        loc_add_str = f"{format_number(loc_add)}++"
        loc_del_str = f"{format_number(loc_del)}--"

        set_text("loc_data", loc_net_str)
        set_text("loc_add", loc_add_str)
        set_text("loc_del", loc_del_str)
        set_text("loc_data_dots", adjust_dots(5, len(loc_net_str)))

        # Write output SVG
        output_path.parent.mkdir(parents=True, exist_ok=True)
        xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_str)

        logger.info(f"Rendered SVG successfully to {output_path}")
