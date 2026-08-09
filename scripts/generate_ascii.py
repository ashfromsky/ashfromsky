#!/usr/bin/env python3
"""
CLI script to generate ASCII portrait assets from input/profile.jpg.
Usage:
    python scripts/generate_ascii.py [--input input/profile.jpg] [--width 40] [--height 25]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ascii_converter import generate_ascii_assets


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ASCII portrait assets for GitHub Profile SVG.")
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "input" / "profile.jpg", help="Path to profile image")
    parser.add_argument("--dark-out", type=Path, default=PROJECT_ROOT / "assets" / "ascii_dark.txt", help="Output dark ASCII path")
    parser.add_argument("--light-out", type=Path, default=PROJECT_ROOT / "assets" / "ascii_light.txt", help="Output light ASCII path")
    parser.add_argument("--width", type=int, default=40, help="ASCII target column width (default 40)")
    parser.add_argument("--height", type=int, default=25, help="ASCII target line height (default 25)")

    args = parser.parse_args()

    print(f"Generating ASCII portrait from {args.input}...")
    dark_lines, light_lines = generate_ascii_assets(
        image_path=args.input,
        dark_out_path=args.dark_out,
        light_out_path=args.light_out,
        target_width=args.width,
        target_height=args.height
    )
    print(f"Successfully generated ASCII assets ({len(dark_lines)} lines x ~{args.width} cols)")
    print(f"Dark mode asset saved to: {args.dark_out}")
    print(f"Light mode asset saved to: {args.light_out}")


if __name__ == "__main__":
    main()
