#!/usr/bin/env python3
"""
Main entry point script to update GitHub Profile SVGs.
Usage:
    python scripts/update_profile.py [--fixture tests/fixtures/github_stats.json]
"""

import argparse
import json
import logging
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ascii_converter import generate_ascii_assets
from src.github_client import GitHubClient, GitHubAPIError
from src.stats_calculator import fetch_and_calculate_stats
from src.svg_renderer import SVGRenderer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def validate_svg(svg_path: Path) -> None:
    """Ensures generated SVG is valid XML and contains essential element IDs."""
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG output does not exist: {svg_path}")

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Generated SVG {svg_path} is invalid XML: {e}")

    # Verify essential required IDs are present in the SVG
    required_ids = [
        "account_age", "repo_data", "contrib_data", "star_data",
        "commit_data", "follower_data", "loc_data", "loc_add", "loc_del"
    ]
    
    found_ids = {elem.attrib["id"] for elem in root.findall(".//*[@id]")}
    missing = [req_id for req_id in required_ids if req_id not in found_ids]

    if missing:
        raise ValueError(f"Generated SVG {svg_path} is missing required element IDs: {missing}")

    logger.info(f"SVG validation passed for {svg_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update GitHub Profile neofetch SVGs.")
    parser.add_argument("--fixture", type=Path, help="Path to deterministic stats JSON fixture (bypasses live API)")
    args = parser.parse_args()

    config_path = PROJECT_ROOT / "config" / "profile.json"
    archived_path = PROJECT_ROOT / "config" / "archived_stats.json"
    cache_path = PROJECT_ROOT / "cache" / "stats_cache.json"

    dark_ascii_path = PROJECT_ROOT / "assets" / "ascii_dark.txt"
    light_ascii_path = PROJECT_ROOT / "assets" / "ascii_light.txt"
    profile_img_path = PROJECT_ROOT / "input" / "profile.jpg"

    dark_template_path = PROJECT_ROOT / "templates" / "dark_mode.template.svg"
    light_template_path = PROJECT_ROOT / "templates" / "light_mode.template.svg"

    dark_output_path = PROJECT_ROOT / "dark_mode.svg"
    light_output_path = PROJECT_ROOT / "light_mode.svg"

    # 1. Load Profile Config
    with open(config_path, "r", encoding="utf-8") as f:
        profile_config = json.load(f)

    archived_stats = {}
    if archived_path.exists():
        with open(archived_path, "r", encoding="utf-8") as f:
            archived_stats = json.load(f)

    # 2. Ensure ASCII Assets exist
    if not dark_ascii_path.exists() or not light_ascii_path.exists():
        logger.info("ASCII assets missing. Generating from input/profile.jpg...")
        generate_ascii_assets(profile_img_path, dark_ascii_path, light_ascii_path)

    with open(dark_ascii_path, "r", encoding="utf-8") as f:
        dark_ascii_lines = [line.rstrip("\r\n") for line in f]

    with open(light_ascii_path, "r", encoding="utf-8") as f:
        light_ascii_lines = [line.rstrip("\r\n") for line in f]

    # 3. Obtain Statistics Data
    if args.fixture:
        logger.info(f"Loading stats from offline fixture: {args.fixture}")
        with open(args.fixture, "r", encoding="utf-8") as f:
            stats = json.load(f)
    else:
        username = profile_config.get("username", "ashfromsky")
        token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")
        
        if not token:
            logger.warning("No PROFILE_TOKEN or GITHUB_TOKEN set. Attempting public API request or fixture fallback...")

        try:
            client = GitHubClient(token=token)
            logger.info(f"Fetching live GitHub statistics for {username}...")
            stats = fetch_and_calculate_stats(
                github_client=client,
                username=username,
                cache_path=cache_path,
                profile_config=profile_config,
                archived_stats=archived_stats
            )
        except Exception as e:
            logger.error(f"Failed to fetch live GitHub stats: {e}")
            if dark_output_path.exists() and light_output_path.exists():
                logger.warning("Keeping existing valid SVG files rather than overwriting with bad data.")
                sys.exit(1)
            else:
                logger.warning("No existing SVGs found. Falling back to default fixture data...")
                fixture_fallback = PROJECT_ROOT / "tests" / "fixtures" / "github_stats.json"
                with open(fixture_fallback, "r", encoding="utf-8") as f:
                    stats = json.load(f)

    # 4. Render SVGs
    logger.info("Rendering dark mode SVG...")
    dark_renderer = SVGRenderer(dark_template_path)
    dark_renderer.render(stats, profile_config, dark_ascii_lines, dark_output_path)

    logger.info("Rendering light mode SVG...")
    light_renderer = SVGRenderer(light_template_path)
    light_renderer.render(stats, profile_config, light_ascii_lines, light_output_path)

    # 5. Validate output SVGs
    validate_svg(dark_output_path)
    validate_svg(light_output_path)

    logger.info("Profile update completed successfully!")


if __name__ == "__main__":
    main()
