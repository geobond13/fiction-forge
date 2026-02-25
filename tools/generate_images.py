#!/usr/bin/env python3
"""
Batch chapter illustration generator using DALL-E 3.

Reads a chapter-images.json manifest and generates illustrations
for each chapter, saving them as WebP or PNG files.

Usage:
    python tools/generate_images.py              # Generate all missing images
    python tools/generate_images.py --dry-run    # List what would be generated
    python tools/generate_images.py --only 00a_Prologue  # Generate one image

Requires:
    - OPENAI_API_KEY environment variable
    - pip install openai Pillow
"""

import argparse
import json
import os
import sys
import time
from io import BytesIO
from pathlib import Path
import urllib.request

from config import ROOT_DIR, load_config, get_images_config

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow package not installed. Run: pip install Pillow")
    sys.exit(1)


CONFIG = load_config()
IMAGES_CONFIG = get_images_config(CONFIG)

MANIFEST_PATH = IMAGES_CONFIG["manifest"]
OUTPUT_DIR = IMAGES_CONFIG["output_dir"]
IMAGE_FORMAT = IMAGES_CONFIG["format"]
IMAGE_QUALITY = IMAGES_CONFIG["quality"]


def load_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_image(client, slug, entry, index, total):
    ext = IMAGE_FORMAT
    output_file = OUTPUT_DIR / f"{slug}.{ext}"

    if output_file.exists():
        print(f"  [{index}/{total}] Skipping {slug} (already exists)")
        return True

    print(f"  [{index}/{total}] Generating {slug}...")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=entry["prompt"],
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        with urllib.request.urlopen(image_url) as resp:
            image_data = resp.read()

        img = Image.open(BytesIO(image_data))

        if ext == "webp":
            img.save(output_file, "WEBP", quality=IMAGE_QUALITY)
        else:
            img.save(output_file, "PNG", optimize=True)

        size_kb = output_file.stat().st_size / 1024
        print(f"           Saved ({size_kb:.0f} KB)")
        return True

    except Exception as e:
        print(f"           ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate chapter illustrations")
    parser.add_argument("--dry-run", action="store_true", help="List what would be generated")
    parser.add_argument("--only", type=str, help="Generate only this slug")
    args = parser.parse_args()

    if not MANIFEST_PATH.exists():
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        print(f"Create a chapter-images.json with entries like:")
        print(f'  {{"00_Prologue": {{"title": "Prologue", "subject": "...", "prompt": "..."}}}}')
        sys.exit(1)

    manifest = load_manifest()
    print(f"Loaded manifest: {len(manifest)} chapters")

    if args.only:
        if args.only not in manifest:
            print(f"Error: Slug '{args.only}' not found in manifest.")
            print(f"Available slugs: {', '.join(list(manifest.keys())[:5])}...")
            sys.exit(1)
        manifest = {args.only: manifest[args.only]}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    to_generate = {}
    ext = IMAGE_FORMAT
    for slug, entry in manifest.items():
        output_file = OUTPUT_DIR / f"{slug}.{ext}"
        if not output_file.exists():
            to_generate[slug] = entry

    if args.dry_run:
        existing = len(manifest) - len(to_generate)
        print(f"\nDry run — {len(to_generate)} images to generate, {existing} already exist:\n")
        for i, (slug, entry) in enumerate(manifest.items(), 1):
            output_file = OUTPUT_DIR / f"{slug}.{ext}"
            status = "EXISTS" if output_file.exists() else "PENDING"
            print(f"  [{i:3d}/{len(manifest)}] [{status}] {slug} — {entry.get('title', '')}")
            print(f"           Subject: {entry.get('subject', entry.get('prompt', '')[:60])}")
        return

    if not to_generate:
        print("\nAll images already generated. Nothing to do.")
        return

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print(f"\nGenerating {len(to_generate)} images...\n")

    success = 0
    failed = 0
    total = len(manifest)

    for i, (slug, entry) in enumerate(manifest.items(), 1):
        if slug not in to_generate:
            continue

        if generate_image(client, slug, entry, i, total):
            success += 1
        else:
            failed += 1

        # Rate limiting — DALL-E 3 allows ~5 images/min on standard tier
        if slug in to_generate and i < total:
            time.sleep(13)

    print(f"\nDone. Generated: {success}, Failed: {failed}, Skipped: {total - success - failed}")


if __name__ == "__main__":
    main()
