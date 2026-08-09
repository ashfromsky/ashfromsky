"""
Unit and Integration tests for GitHub Profile Terminal generator.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest

from src.ascii_converter import image_to_ascii
from src.stats_calculator import calculate_uptime, CacheManager
from src.svg_renderer import SVGRenderer, adjust_dots, format_number
from scripts.update_profile import validate_svg

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_uptime_calculation():
    uptime = calculate_uptime("2023-03-01T12:00:00Z")
    assert "year" in uptime or "month" in uptime or "day" in uptime


def test_adjust_dots():
    dots = adjust_dots(10, 3)
    assert dots == "....... "
    assert len(dots) == 8


def test_format_number():
    assert format_number(1234567) == "1,234,567"
    assert format_number(0) == "0"


def test_ascii_conversion(tmp_path):
    img_path = PROJECT_ROOT / "input" / "profile.jpg"
    if img_path.exists():
        dark_lines = image_to_ascii(img_path, target_width=30, target_height=20, dark_theme=True)
        assert len(dark_lines) == 20
        # Check XML escaping
        for line in dark_lines:
            assert "<" not in line
            assert ">" not in line


def test_svg_rendering_and_validation(tmp_path):
    template_dark = PROJECT_ROOT / "templates" / "dark_mode.template.svg"
    template_light = PROJECT_ROOT / "templates" / "light_mode.template.svg"
    config_path = PROJECT_ROOT / "config" / "profile.json"
    fixture_path = PROJECT_ROOT / "tests" / "fixtures" / "github_stats.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    with open(fixture_path, "r", encoding="utf-8") as f:
        stats = json.load(f)

    dummy_ascii = ["." * 40] * 25

    dark_out = tmp_path / "dark_test.svg"
    light_out = tmp_path / "light_test.svg"

    renderer_dark = SVGRenderer(template_dark)
    renderer_dark.render(stats, config, dummy_ascii, dark_out)
    validate_svg(dark_out)

    renderer_light = SVGRenderer(template_light)
    renderer_light.render(stats, config, dummy_ascii, light_out)
    validate_svg(light_out)


def test_cache_manager(tmp_path):
    cache_file = tmp_path / "test_cache.json"
    cm = CacheManager(cache_file)
    cm.update_repo_cache("ashfromsky/test", "oid123", 5, 100, 20)
    cm.save()

    cm2 = CacheManager(cache_file)
    entry = cm2.get_repo_cache("ashfromsky/test")
    assert entry is not None
    assert entry["head_oid"] == "oid123"
    assert entry["my_commits"] == 5
