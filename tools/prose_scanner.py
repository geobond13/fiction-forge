#!/usr/bin/env python3
"""
Prose pattern scanner for fiction manuscripts.

Detects overused syntactic patterns (em-dashes, similes, hedging verbs, etc.)
and generates a severity-tiered report. Includes cluster detection for
3+ occurrences within a 150-word sliding window.

Usage:
    python tools/prose_scanner.py                  # Full scan
    python tools/prose_scanner.py --chapter 12     # Single chapter
    python tools/prose_scanner.py --summary        # Table only
    python tools/prose_scanner.py --preset genre_fiction  # Override preset
"""

import json
import re
import sys
from pathlib import Path

import yaml

from config import ROOT_DIR, load_config, get_structure, get_scanner_config

# Ensure Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG = load_config()
STRUCTURE = get_structure(CONFIG)
SCANNER_CONFIG = get_scanner_config(CONFIG)

BOOK_DIR = STRUCTURE["book_dir"]
OUTPUT_DIR = STRUCTURE["output_dir"]

# Severity thresholds (total weighted score)
SEVERITY_CRITICAL = SCANNER_CONFIG["severity"]["critical"]
SEVERITY_HIGH = SCANNER_CONFIG["severity"]["high"]
SEVERITY_MEDIUM = SCANNER_CONFIG["severity"]["medium"]

# Cluster detection settings
CLUSTER_THRESHOLD = 3
CLUSTER_WINDOW_WORDS = 150


# ---------------------------------------------------------------------------
# Pattern loading
# ---------------------------------------------------------------------------

def load_patterns(preset_name: str) -> list[dict]:
    """Load pattern definitions from a YAML preset file.

    Args:
        preset_name: Either a preset name (loads from presets/patterns/{name}.yaml)
                     or a file path to a custom YAML file.

    Returns:
        List of pattern dicts with keys: name, regex, target_density, weight, description
    """
    # Check if it's a direct path
    preset_path = Path(preset_name)
    if preset_path.exists():
        pass
    else:
        # Look in presets/patterns/
        preset_path = ROOT_DIR / "presets" / "patterns" / f"{preset_name}.yaml"

    if not preset_path.exists():
        print(f"  Error: Preset not found: {preset_path}")
        print(f"  Available presets in {ROOT_DIR / 'presets' / 'patterns'}:")
        presets_dir = ROOT_DIR / "presets" / "patterns"
        if presets_dir.exists():
            for f in presets_dir.glob("*.yaml"):
                if not f.name.endswith(".example"):
                    print(f"    - {f.stem}")
        sys.exit(1)

    data = yaml.safe_load(preset_path.read_text(encoding="utf-8"))
    patterns = data.get("patterns", [])

    # Validate and set defaults
    for p in patterns:
        p.setdefault("weight", 1.0)
        p.setdefault("description", "")
        if "name" not in p or "regex" not in p or "target_density" not in p:
            print(f"  Warning: Pattern missing required fields: {p}")

    return patterns


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def get_chapters() -> list[Path]:
    """Return sorted list of chapter files."""
    if not BOOK_DIR.exists():
        return []
    chapters = [c for c in BOOK_DIR.glob("*.md") if not c.name.startswith("Notes")]

    def sort_key(p):
        m = re.match(r'(\d+)', p.name)
        num = int(m.group(1)) if m else 999
        suffix_m = re.match(r'\d+([a-z]?)', p.name)
        suffix = suffix_m.group(1) if suffix_m else ''
        return (num, suffix)

    return sorted(chapters, key=sort_key)


def strip_comments(text: str) -> str:
    """Remove HTML comments."""
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


def get_chapter_number(filename: str) -> int:
    m = re.match(r'(\d+)', filename)
    return int(m.group(1)) if m else -1


# ---------------------------------------------------------------------------
# Pattern scanning
# ---------------------------------------------------------------------------

def find_pattern_matches(text: str, pattern_name: str, regex: str) -> list[dict]:
    """Find all matches of a pattern, returning line context."""
    matches = []
    lines = text.split("\n")

    line_offsets = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line) + 1

    for m in re.finditer(regex, text):
        pos = m.start()
        line_num = 0
        for i, lo in enumerate(line_offsets):
            if lo > pos:
                break
            line_num = i

        context_start = max(0, line_num - 1)
        context_end = min(len(lines), line_num + 2)
        context = "\n".join(lines[context_start:context_end])

        matches.append({
            "pattern": pattern_name,
            "line": line_num + 1,
            "match": m.group(0),
            "context": context[:300],
            "char_pos": pos,
        })

    return matches


def detect_clusters(text: str, all_matches: list[dict]) -> list[dict]:
    """Detect clusters of 3+ same-pattern occurrences within 150-word windows."""
    words = text.split()
    if not words:
        return []

    word_positions = []
    offset = 0
    for i, word in enumerate(words):
        idx = text.find(word, offset)
        word_positions.append(idx)
        offset = idx + len(word)

    def char_pos_to_word_idx(char_pos: int) -> int:
        for i, wp in enumerate(word_positions):
            if wp >= char_pos:
                return max(0, i - 1)
        return len(words) - 1

    clusters = []

    by_pattern: dict[str, list[dict]] = {}
    for m in all_matches:
        by_pattern.setdefault(m["pattern"], []).append(m)

    for pattern_name, matches in by_pattern.items():
        if len(matches) < CLUSTER_THRESHOLD:
            continue

        sorted_matches = sorted(matches, key=lambda x: x["char_pos"])

        for i in range(len(sorted_matches) - CLUSTER_THRESHOLD + 1):
            window_start = sorted_matches[i]
            window_end = sorted_matches[i + CLUSTER_THRESHOLD - 1]

            start_word = char_pos_to_word_idx(window_start["char_pos"])
            end_word = char_pos_to_word_idx(window_end["char_pos"])

            if end_word - start_word <= CLUSTER_WINDOW_WORDS:
                count = 0
                for m in sorted_matches[i:]:
                    mw = char_pos_to_word_idx(m["char_pos"])
                    if mw - start_word <= CLUSTER_WINDOW_WORDS:
                        count += 1
                    else:
                        break

                clusters.append({
                    "pattern": pattern_name,
                    "count": count,
                    "window_words": end_word - start_word,
                    "start_line": window_start["line"],
                    "end_line": window_end["line"],
                    "context": window_start["context"],
                })

    seen = set()
    unique_clusters = []
    for c in sorted(clusters, key=lambda x: -x["count"]):
        key = (c["pattern"], c["start_line"])
        if key not in seen:
            seen.add(key)
            unique_clusters.append(c)

    return unique_clusters


def detect_repeated_openings(text: str) -> list[dict]:
    """Detect paragraphs where 3+ sentences start the same way."""
    paragraphs = re.split(r'\n\s*\n', text)
    issues = []

    for para in paragraphs:
        para = para.strip()
        if not para or para.startswith('#'):
            continue

        sentences = re.split(r'[.!?]+\s+', para)
        if len(sentences) < 3:
            continue

        openers = []
        for s in sentences:
            s = s.strip()
            if s:
                words = s.split()[:3]
                opener = " ".join(words).lower()
                openers.append(opener)

        from collections import Counter
        counts = Counter(openers)
        for opener, count in counts.items():
            if count >= 3:
                line_num = text[:text.find(para)].count("\n") + 1
                issues.append({
                    "pattern": "repeated_opening",
                    "count": count,
                    "opener": opener,
                    "line": line_num,
                    "context": para[:200],
                })

    return issues


# ---------------------------------------------------------------------------
# Chapter analysis
# ---------------------------------------------------------------------------

def analyze_chapter(filepath: Path, patterns: list[dict]) -> dict:
    """Analyze a single chapter for all prose patterns."""
    text = strip_comments(filepath.read_text(encoding="utf-8"))
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return {
            "file": filepath.name,
            "chapter": get_chapter_number(filepath.name),
            "word_count": 0,
            "patterns": {},
            "clusters": [],
            "repeated_openings": [],
            "severity_score": 0,
            "tier": "LOW",
        }

    all_matches = []
    pattern_results = {}

    for p in patterns:
        name = p["name"]
        regex = p["regex"]
        target = p["target_density"]
        weight = p["weight"]

        matches = find_pattern_matches(text, name, regex)
        count = len(matches)
        density = (count / word_count) * 1000 if word_count > 0 else 0

        pattern_results[name] = {
            "count": count,
            "density": round(density, 2),
            "target_density": target,
            "over_target": density > target,
            "excess_ratio": round(density / target, 2) if target > 0 else 0,
            "weight": weight,
            "flagged_lines": [
                {"line": m["line"], "match": m["match"], "context": m["context"]}
                for m in matches
            ],
        }

        all_matches.extend(matches)

    clusters = detect_clusters(text, all_matches)
    repeated_openings = detect_repeated_openings(text)

    severity_score = 0
    for name, data in pattern_results.items():
        if data["over_target"]:
            excess = data["density"] - data["target_density"]
            severity_score += excess * data["weight"]

    severity_score += len(clusters) * 1.5
    severity_score += len(repeated_openings) * 1.0

    if severity_score >= SEVERITY_CRITICAL:
        tier = "CRITICAL"
    elif severity_score >= SEVERITY_HIGH:
        tier = "HIGH"
    elif severity_score >= SEVERITY_MEDIUM:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    return {
        "file": filepath.name,
        "chapter": get_chapter_number(filepath.name),
        "word_count": word_count,
        "patterns": pattern_results,
        "clusters": clusters,
        "repeated_openings": repeated_openings,
        "severity_score": round(severity_score, 2),
        "tier": tier,
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_summary(results: list[dict], patterns: list[dict]):
    """Print severity summary table."""
    results_sorted = sorted(results, key=lambda x: -x["severity_score"])

    tier_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        tier_counts[r["tier"]] += 1

    print(f"\n{'=' * 80}")
    print(f"  Prose Pattern Scan — {len(results)} chapters")
    print(f"{'=' * 80}")
    print(f"\n  Tiers: CRITICAL={tier_counts['CRITICAL']}  HIGH={tier_counts['HIGH']}  "
          f"MEDIUM={tier_counts['MEDIUM']}  LOW={tier_counts['LOW']}")
    print()

    total_words = sum(r["word_count"] for r in results)
    print(f"  Total words: {total_words:,}")
    print()

    pattern_totals: dict[str, int] = {}
    for r in results:
        for name, data in r["patterns"].items():
            pattern_totals[name] = pattern_totals.get(name, 0) + data["count"]

    print(f"  {'Pattern':<25} {'Count':>7} {'Density':>9} {'Target':>9}")
    print(f"  {'-' * 55}")
    for p in patterns:
        name = p["name"]
        target = p["target_density"]
        count = pattern_totals.get(name, 0)
        density = (count / total_words) * 1000 if total_words > 0 else 0
        flag = " **" if density > target else ""
        print(f"  {name:<25} {count:>7,} {density:>8.2f}/1k {target:>7.2f}/1k{flag}")

    print()

    print(f"  {'Ch':<5} {'File':<45} {'Words':>6} {'Score':>6} {'Tier':<8} {'Top issues'}")
    print(f"  {'-' * 100}")
    for r in results_sorted:
        if r["severity_score"] < 0.5:
            continue

        worst = sorted(
            [(name, data["density"], data["target_density"])
             for name, data in r["patterns"].items() if data["over_target"]],
            key=lambda x: -(x[1] / x[2]) if x[2] > 0 else 0
        )[:2]
        issues = ", ".join(f"{n}={d:.1f}/1k" for n, d, _ in worst)
        if r["clusters"]:
            issues += f", {len(r['clusters'])} clusters"

        tier_color = {
            "CRITICAL": "CRITICAL",
            "HIGH": "HIGH    ",
            "MEDIUM": "MEDIUM  ",
            "LOW": "LOW     ",
        }

        print(f"  {r['chapter']:<5} {r['file']:<45} {r['word_count']:>6,} "
              f"{r['severity_score']:>6.1f} {tier_color[r['tier']]} {issues}")

    print(f"\n{'=' * 80}\n")


def print_chapter_detail(result: dict):
    """Print detailed report for a single chapter."""
    print(f"\n{'=' * 70}")
    print(f"  Chapter {result['chapter']}: {result['file']}")
    print(f"  Words: {result['word_count']:,}  |  Score: {result['severity_score']:.1f}  |  Tier: {result['tier']}")
    print(f"{'=' * 70}")

    for name, data in result["patterns"].items():
        if data["count"] == 0:
            continue
        flag = " ** OVER TARGET" if data["over_target"] else ""
        print(f"\n  {name}: {data['count']} ({data['density']}/1k, target {data['target_density']}/1k){flag}")

        if data["over_target"] and data["flagged_lines"]:
            for fl in data["flagged_lines"][:10]:
                ctx = fl["context"].replace("\n", " \\n ")[:100]
                print(f"    L{fl['line']:>4}: ...{ctx}...")

    if result["clusters"]:
        print(f"\n  CLUSTERS ({len(result['clusters'])}):")
        for c in result["clusters"]:
            print(f"    {c['pattern']}: {c['count']}x in {c['window_words']} words "
                  f"(lines {c['start_line']}-{c['end_line']})")

    if result["repeated_openings"]:
        print(f"\n  REPEATED OPENINGS ({len(result['repeated_openings'])}):")
        for ro in result["repeated_openings"]:
            print(f"    \"{ro['opener']}\" x{ro['count']} at line {ro['line']}")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    single_chapter = None
    summary_only = False
    preset_override = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--chapter" and i + 1 < len(args):
            single_chapter = int(args[i + 1])
            i += 2
        elif args[i] == "--summary":
            summary_only = True
            i += 1
        elif args[i] == "--preset" and i + 1 < len(args):
            preset_override = args[i + 1]
            i += 2
        else:
            i += 1

    # Load patterns
    preset = preset_override or SCANNER_CONFIG["preset"]
    patterns = load_patterns(preset)
    print(f"  Preset: {preset} ({len(patterns)} patterns)")

    chapters = get_chapters()

    if single_chapter is not None:
        target = None
        for ch in chapters:
            if get_chapter_number(ch.name) == single_chapter:
                target = ch
                break
        if target is None:
            print(f"Chapter {single_chapter} not found.")
            sys.exit(1)

        result = analyze_chapter(target, patterns)
        print_chapter_detail(result)

        report_path = OUTPUT_DIR / f"prose_report_ch{single_chapter}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  Report: {report_path}")
        return

    print(f"\n  Scanning {len(chapters)} chapters...")
    results = []
    for ch in chapters:
        result = analyze_chapter(ch, patterns)
        results.append(result)
        tier_sym = {"CRITICAL": "!", "HIGH": "*", "MEDIUM": ".", "LOW": " "}
        sys.stdout.write(tier_sym.get(result["tier"], " "))
        sys.stdout.flush()
    print()

    print_summary(results, patterns)

    if not summary_only:
        report_path = OUTPUT_DIR / "prose_report.json"
        report_data = {
            "preset": preset,
            "total_chapters": len(results),
            "total_words": sum(r["word_count"] for r in results),
            "tiers": {
                "CRITICAL": [r["file"] for r in results if r["tier"] == "CRITICAL"],
                "HIGH": [r["file"] for r in results if r["tier"] == "HIGH"],
                "MEDIUM": [r["file"] for r in results if r["tier"] == "MEDIUM"],
                "LOW": [r["file"] for r in results if r["tier"] == "LOW"],
            },
            "chapters": results,
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"  Full report: {report_path}")


if __name__ == "__main__":
    main()
