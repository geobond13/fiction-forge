#!/usr/bin/env python3
"""
Compile markdown chapters into publishable book formats.

Usage: python tools/publish.py [--epub] [--pdf] [--html] [--all] [--count]

Produces properly formatted books with:
  - Cover image
  - Half-title, title page, copyright page
  - Part divider pages
  - Chapter page breaks
  - Table of contents
  - Scene break styling

Requires pandoc for EPUB/PDF/HTML generation.
"""

import re
import subprocess
import sys
from pathlib import Path

from config import ROOT_DIR, load_config, get_project, get_structure

# Ensure Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG = load_config()
PROJECT = get_project(CONFIG)
STRUCTURE = get_structure(CONFIG)

BOOK_DIR = STRUCTURE["book_dir"]
OUTPUT_DIR = STRUCTURE["output_dir"]
TEMPLATE_DIR = STRUCTURE["templates_dir"]
COVER_IMAGE = STRUCTURE["cover_image"]
ILLUSTRATIONS_SRC = STRUCTURE["illustrations_src"]
ILLUSTRATIONS_BUILD = OUTPUT_DIR / "images"

TITLE = PROJECT["title"]
SUBTITLE = PROJECT["subtitle"]
AUTHOR = PROJECT["author"]
PUBLISHER = PROJECT["publisher"]
YEAR = PROJECT["year"]

PART_BREAKS = STRUCTURE["parts"]
FRONT_MATTER_FILES = STRUCTURE["front_matter"]


def title_slug() -> str:
    """Create a filename-safe slug from the title."""
    return re.sub(r'[^\w]+', '_', TITLE).strip('_')


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def get_chapters():
    """Return sorted list of chapter files."""
    if not BOOK_DIR.exists():
        return []
    chapters = [c for c in BOOK_DIR.glob("*.md") if not c.name.startswith("Notes")]

    def sort_key(p):
        m = re.match(r'(\d+)', p.name)
        num = int(m.group(1)) if m else 999
        suffix = re.match(r'\d+([a-z]?)', p.name).group(1) or ''
        return (num, suffix)

    return sorted(chapters, key=sort_key)


def strip_comments(text):
    """Remove HTML comments (metadata blocks, revision notes)."""
    lines = text.split('\n')
    filtered = []
    in_comment = False
    for line in lines:
        if line.strip().startswith('<!--'):
            if '-->' in line:
                continue
            in_comment = True
            continue
        if in_comment and '-->' in line:
            in_comment = False
            continue
        if not in_comment:
            filtered.append(line)
    return '\n'.join(filtered)


def get_chapter_number(filename):
    """Extract the numeric chapter number from a filename."""
    m = re.match(r'(\d+)', filename)
    return int(m.group(1)) if m else -1


def get_chapter_slug(filename):
    """Convert a chapter filename to its illustration slug."""
    return Path(filename).stem.lower()


def prepare_illustrations():
    """Convert WebP chapter illustrations to PNG for pandoc/xelatex compatibility.

    Returns the build directory path, or None if no illustrations are available.
    """
    if ILLUSTRATIONS_SRC is None or not ILLUSTRATIONS_SRC.exists():
        return None

    webp_files = list(ILLUSTRATIONS_SRC.glob("*.webp"))
    if not webp_files:
        return None

    try:
        from PIL import Image
    except ImportError:
        print("  Warning: Pillow not installed, skipping illustrations.")
        return None

    ILLUSTRATIONS_BUILD.mkdir(parents=True, exist_ok=True)
    converted = 0

    for webp_path in webp_files:
        png_path = ILLUSTRATIONS_BUILD / (webp_path.stem + ".png")
        if png_path.exists() and png_path.stat().st_mtime >= webp_path.stat().st_mtime:
            converted += 1
            continue
        img = Image.open(webp_path)
        img = img.resize((256, 256), Image.LANCZOS)
        img.save(png_path, "PNG", optimize=True)
        converted += 1

    if converted:
        print(f"  Illustrations: {converted} images ready")
    return ILLUSTRATIONS_BUILD


def make_illustration_block(slug, illustrations_dir):
    """Return markdown for a centered chapter illustration, or empty string."""
    if illustrations_dir is None:
        return ""
    png_path = illustrations_dir / f"{slug}.png"
    if not png_path.exists():
        return ""
    abs_path = str(png_path.resolve()).replace('\\', '/')
    return f'\n\n![]({abs_path}){{ .chapter-illustration }}\n'


# ---------------------------------------------------------------------------
# Front matter generators
# ---------------------------------------------------------------------------

def make_half_title():
    return f"""# {TITLE.upper()} {{.half-title .unnumbered}}
"""


def make_title_page():
    parts = [f"# {TITLE} {{.title-page .unnumbered}}"]
    if SUBTITLE:
        parts.append(f"\n*{SUBTITLE}*")
    parts.append(f"\n\\\n\n\\\n\n{AUTHOR}")
    if PUBLISHER:
        parts.append(f"\n\\\n\n\\\n\n\\\n\n{PUBLISHER}")
    return "\n".join(parts) + "\n"


def make_copyright_page():
    parts = [f"# Copyright {{.copyright-page .unnumbered}}"]
    parts.append(f"\nCopyright \u00a9 {YEAR} {AUTHOR}. All rights reserved.")
    parts.append(
        "\nNo part of this publication may be reproduced, distributed, or transmitted "
        "in any form or by any means without prior written permission of the author, "
        "except for brief quotations in reviews and certain noncommercial uses "
        "permitted by fair use."
    )
    if PUBLISHER:
        parts.append(f"\nPublished by {PUBLISHER}")
    parts.append(f"\nFirst edition, {YEAR}")
    return "\n".join(parts) + "\n"


def make_part_divider(number, name):
    return f"""# Part {number}: {name} {{.part-divider .unnumbered}}
"""


# ---------------------------------------------------------------------------
# Markdown assembly
# ---------------------------------------------------------------------------

def combine_markdown(illustrations_dir=None, suffix=""):
    """Combine all chapters into a single markdown file with proper book structure."""
    sections = []

    sections.append(make_half_title())
    sections.append(make_title_page())
    sections.append(make_copyright_page())

    chapters = get_chapters()

    for chapter in chapters:
        filename = chapter.name
        ch_num = get_chapter_number(filename)
        content = strip_comments(chapter.read_text(encoding='utf-8'))

        if ch_num in PART_BREAKS and filename not in FRONT_MATTER_FILES:
            info = PART_BREAKS[ch_num]
            sections.append(make_part_divider(info["number"], info["name"]))

        slug = get_chapter_slug(filename)
        illustration = make_illustration_block(slug, illustrations_dir)
        sections.append(content + illustration)

    combined = '\n\n'.join(sections)

    slug = title_slug()
    output_path = OUTPUT_DIR / f"{slug}{suffix}.md"
    output_path.write_text(combined, encoding='utf-8')
    print(f"  Markdown: {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# Format generators
# ---------------------------------------------------------------------------

def generate_epub(md_path, suffix=""):
    slug = title_slug()
    output = OUTPUT_DIR / f"{slug}{suffix}.epub"
    css_path = TEMPLATE_DIR / "epub.css"

    cmd = [
        "pandoc", str(md_path),
        "-o", str(output),
        "--toc",
        "--toc-depth=1",
        "--split-level=1",
        "--metadata", f"title={TITLE}",
        "--metadata", f"creator={AUTHOR}",
        "--metadata", "language=en-US",
    ]

    if css_path.exists():
        cmd += ["--css", str(css_path)]

    if COVER_IMAGE and COVER_IMAGE.exists():
        cmd += ["--epub-cover-image", str(COVER_IMAGE)]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"  EPUB:     {output} ({size_mb:.1f} MB)")
    except FileNotFoundError:
        print("  Error: pandoc not found. Install pandoc.")
    except subprocess.CalledProcessError as e:
        print(f"  Error generating EPUB: {e.stderr}")


def generate_pdf(md_path, suffix=""):
    slug = title_slug()
    output = OUTPUT_DIR / f"{slug}{suffix}.pdf"

    cmd = [
        "pandoc", str(md_path),
        "-o", str(output),
        "--pdf-engine=xelatex",
        "--toc",
        "--toc-depth=1",
        "-V", "geometry:papersize={6in,9in}",
        "-V", "geometry:margin=0.75in",
        "-V", "geometry:top=1in",
        "-V", "geometry:bottom=0.75in",
        "-V", "mainfont:Palatino Linotype",
        "-V", "fontsize=11pt",
        "-V", "linestretch=1.3",
        "-V", "documentclass=book",
        "-V", "classoption=openany",
        "--metadata", f"title={TITLE}",
    ]

    if COVER_IMAGE and COVER_IMAGE.exists():
        cover_path_escaped = str(COVER_IMAGE).replace('\\', '/')
        cover_latex = (
            r"\usepackage{pdfpages}"
            r"\AtBeginDocument{"
            rf"\includepdf[fitpaper]{{{cover_path_escaped}}}"
            r"}"
        )
        cmd += ["-V", f"header-includes={cover_latex}"]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"  PDF:      {output} ({size_mb:.1f} MB)")
    except FileNotFoundError:
        print("  Error: xelatex not found. Install MiKTeX or TeX Live.")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        error_lines = [l for l in stderr.split('\n') if l.startswith('!') or 'Error' in l]
        if error_lines:
            print(f"  PDF error: {error_lines[0]}")
        else:
            print(f"  Error generating PDF. Run with --verbose for details.")
            if "--verbose" in sys.argv:
                print(stderr[-2000:])


def generate_html(md_path, suffix=""):
    slug = title_slug()
    output = OUTPUT_DIR / f"{slug}{suffix}.html"
    css_path = TEMPLATE_DIR / "epub.css"

    cmd = [
        "pandoc", str(md_path),
        "-o", str(output),
        "--standalone",
        "--toc",
        "--toc-depth=1",
        "--metadata", f"title={TITLE}",
    ]

    if css_path.exists():
        cmd += ["--css", str(css_path)]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"  HTML:     {output} ({size_mb:.1f} MB)")
    except FileNotFoundError:
        print("  Error: pandoc not found. Install pandoc.")
    except subprocess.CalledProcessError as e:
        print(f"  Error generating HTML: {e.stderr}")


# ---------------------------------------------------------------------------
# Word count
# ---------------------------------------------------------------------------

def word_count():
    """Count words across all chapters."""
    total = 0
    part_totals = {}
    current_part = "Front Matter"

    print(f"\n{'─' * 55}")
    print(f"  {TITLE} — Word Count")
    print(f"{'─' * 55}")

    for chapter in get_chapters():
        ch_num = get_chapter_number(chapter.name)

        if ch_num in PART_BREAKS:
            if current_part != "Front Matter":
                print(f"  {'':40s} {part_totals[current_part]:>8,}")
                print()
            info = PART_BREAKS[ch_num]
            current_part = f"Part {info['number']}"
            part_totals[current_part] = 0
            print(f"  Part {info['number']}: {info['name']}")
            print(f"  {'─' * 50}")

        content = strip_comments(chapter.read_text(encoding='utf-8'))
        words = len(content.split())
        total += words

        if current_part not in part_totals:
            part_totals[current_part] = 0
        part_totals[current_part] += words

        print(f"    {chapter.stem:40s} {words:>6,}")

    if current_part in part_totals:
        print(f"  {'':40s} {part_totals[current_part]:>8,}")

    print(f"\n{'─' * 55}")
    print(f"  {'TOTAL':40s} {total:>8,}")
    print(f"{'─' * 55}\n")

    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_edition(formats, illustrations_dir=None, suffix="", label=""):
    if label:
        print(f"\n  [{label}]")

    md_path = combine_markdown(illustrations_dir, suffix=suffix)

    if "epub" in formats:
        generate_epub(md_path, suffix=suffix)
    if "pdf" in formats:
        generate_pdf(md_path, suffix=suffix)
    if "html" in formats:
        generate_html(md_path, suffix=suffix)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    if len(sys.argv) == 1:
        print(f"\n  {TITLE} — Publishing Toolkit")
        print(f"  {'=' * 40}")
        print(f"\n  Usage: python tools/publish.py [options]\n")
        print(f"  Options:")
        print(f"    --epub              Generate EPUB")
        print(f"    --pdf               Generate PDF (6x9 book)")
        print(f"    --html              Generate single-page HTML")
        print(f"    --all               Generate all formats")
        print(f"    --no-illustrations  Plain text only (no images)")
        print(f"    --both              Generate illustrated + plain editions")
        print(f"    --count             Word count by chapter and part")
        print(f"    --verbose           Show detailed error output")
        print(f"\n  Examples:")
        print(f"    publish.py --all                   # illustrated EPUB/PDF/HTML")
        print(f"    publish.py --all --no-illustrations # plain EPUB/PDF/HTML")
        print(f"    publish.py --all --both             # both editions, all formats")
        print(f"\n  Requires: pandoc, xelatex (for PDF)")
        return

    if "--count" in sys.argv:
        word_count()
        return

    print(f"\n  Building {TITLE}...")
    print(f"  {'─' * 40}")

    formats = set()
    if "--epub" in sys.argv or "--all" in sys.argv:
        formats.add("epub")
    if "--pdf" in sys.argv or "--all" in sys.argv:
        formats.add("pdf")
    if "--html" in sys.argv or "--all" in sys.argv:
        formats.add("html")

    no_illus = "--no-illustrations" in sys.argv
    both = "--both" in sys.argv

    illustrations_dir = None
    if not no_illus or both:
        illustrations_dir = prepare_illustrations()

    if both:
        build_edition(formats, illustrations_dir=illustrations_dir,
                      suffix="_Illustrated", label="Illustrated edition")
        build_edition(formats, illustrations_dir=None,
                      suffix="", label="Plain edition")
    elif no_illus:
        build_edition(formats, illustrations_dir=None, label="Plain edition")
    else:
        build_edition(formats, illustrations_dir=illustrations_dir,
                      label="Illustrated edition")

    print(f"\n  {'─' * 40}")
    print(f"  Done.\n")


if __name__ == "__main__":
    main()
