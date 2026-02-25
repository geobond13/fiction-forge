"""
Shared configuration loader for fiction-forge tools.

All tools call load_config() to read project.yaml from the repo root.
"""

from pathlib import Path

import yaml


def find_root() -> Path:
    """Find the project root by walking up from this file's directory."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "project.yaml").exists():
            return current
        current = current.parent
    # Fallback: parent of tools/
    return Path(__file__).resolve().parent.parent


ROOT_DIR = find_root()


def load_config() -> dict:
    """Load project.yaml from the repo root. Returns empty dict if missing."""
    config_path = ROOT_DIR / "project.yaml"
    if config_path.exists():
        return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return {}


def get_project(config: dict) -> dict:
    """Get project metadata with defaults."""
    proj = config.get("project", {})
    return {
        "title": proj.get("title", "My Novel"),
        "subtitle": proj.get("subtitle", ""),
        "author": proj.get("author", "Author Name"),
        "publisher": proj.get("publisher", ""),
        "year": proj.get("year", 2026),
    }


def get_structure(config: dict) -> dict:
    """Get directory structure config with defaults."""
    s = config.get("structure", {})
    return {
        "book_dir": ROOT_DIR / s.get("book_dir", "book"),
        "reference_dir": ROOT_DIR / s.get("reference_dir", "reference"),
        "output_dir": ROOT_DIR / s.get("output_dir", "output"),
        "templates_dir": ROOT_DIR / s.get("templates_dir", "templates"),
        "cover_image": ROOT_DIR / s["cover_image"] if s.get("cover_image") else None,
        "illustrations_src": ROOT_DIR / s["illustrations_src"] if s.get("illustrations_src") else None,
        "front_matter": set(s.get("front_matter", [])),
        "parts": {int(k): v for k, v in s.get("parts", {}).items()},
    }


def get_characters(config: dict) -> dict:
    """Get character aliases map. Keys are canonical names, values are alias lists."""
    chars = config.get("characters") or {}
    return chars.get("aliases") or {}


def get_reference_sources(config: dict) -> dict[str, Path]:
    """Get reference source paths (resolved to absolute)."""
    sources = config.get("reference_sources") or {}
    return {k: ROOT_DIR / v for k, v in sources.items()}


def get_scanner_config(config: dict) -> dict:
    """Get scanner configuration."""
    s = config.get("scanner", {})
    return {
        "preset": s.get("preset", "literary_fiction"),
        "severity": {
            "critical": s.get("severity", {}).get("critical", 12.0),
            "high": s.get("severity", {}).get("high", 6.0),
            "medium": s.get("severity", {}).get("medium", 3.0),
        },
    }


def get_images_config(config: dict) -> dict:
    """Get image generation configuration."""
    img = config.get("images", {})
    return {
        "manifest": ROOT_DIR / img.get("manifest", "chapter-images.json"),
        "output_dir": ROOT_DIR / img.get("output_dir", "images"),
        "style": img.get("style", "oil painting, dramatic lighting"),
        "format": img.get("format", "webp"),
        "quality": img.get("quality", 85),
    }
