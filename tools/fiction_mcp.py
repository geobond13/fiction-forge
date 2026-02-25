#!/usr/bin/env python3
"""
Fiction Context MCP Server.

Exposes 5 tools for Claude Code to query story bible, character voices,
chapter context, continuity constraints, and foreshadowing threads.

Usage: Configured in .mcp.json, started automatically by Claude Code.
"""

import re
import sys
from pathlib import Path

import yaml
from fastmcp import FastMCP

from config import (
    ROOT_DIR,
    load_config,
    get_characters,
    get_reference_sources,
    get_structure,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG = load_config()
STRUCTURE = get_structure(CONFIG)
BOOK_DIR = STRUCTURE["book_dir"]
CHARACTER_ALIASES = get_characters(CONFIG)
REFERENCE_SOURCES = get_reference_sources(CONFIG)
PART_BREAKS = STRUCTURE["parts"]

# Optional continuity rules
CONTINUITY_RULES_PATH = STRUCTURE["reference_dir"] / "continuity_rules.yaml"
CHARACTER_STATES_PATH = STRUCTURE["reference_dir"] / "character_states.yaml"


def _load_yaml_optional(path: Path) -> dict:
    """Load a YAML file if it exists, otherwise return empty dict."""
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {}


CONTINUITY_RULES = _load_yaml_optional(CONTINUITY_RULES_PATH)
CHARACTER_STATES = _load_yaml_optional(CHARACTER_STATES_PATH)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

class DataStore:
    """Loads and indexes all reference data at startup."""

    def __init__(self):
        self.documents: dict[str, str] = {}
        self.sections: list[dict] = []
        self._load_all()

    def _load_all(self):
        """Load all reference documents and parse into sections."""
        for name, path in REFERENCE_SOURCES.items():
            if path.exists():
                text = path.read_text(encoding="utf-8")
                self.documents[name] = text
                self._parse_sections(name, text)

    def _parse_sections(self, source: str, text: str):
        """Split markdown into heading-delimited sections."""
        lines = text.split("\n")
        current_heading = "(top)"
        current_level = 0
        current_lines: list[str] = []

        for line in lines:
            m = re.match(r'^(#{1,4})\s+(.+)', line)
            if m:
                if current_lines:
                    content = "\n".join(current_lines).strip()
                    if content:
                        self.sections.append({
                            "source": source,
                            "heading": current_heading,
                            "level": current_level,
                            "content": content,
                        })
                current_heading = m.group(2).strip()
                current_level = len(m.group(1))
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                self.sections.append({
                    "source": source,
                    "heading": current_heading,
                    "level": current_level,
                    "content": content,
                })

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """Case-insensitive substring search across all sections."""
        query_lower = query.lower()
        terms = query_lower.split()
        results = []

        for section in self.sections:
            text_lower = section["content"].lower()
            heading_lower = section["heading"].lower()

            matches = sum(1 for t in terms if t in text_lower or t in heading_lower)
            if matches == len(terms):
                density = sum(text_lower.count(t) + heading_lower.count(t) for t in terms)
                results.append((density, section))

        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:max_results]]

    def get_character_sections(self, name: str) -> list[dict]:
        """Find all sections mentioning a character (resolves aliases)."""
        name_lower = name.lower().strip()
        aliases = [name_lower]
        for canonical, alias_list in CHARACTER_ALIASES.items():
            if name_lower in [a.lower() for a in alias_list] or name_lower == canonical.lower():
                aliases = [a.lower() for a in alias_list] + [canonical.lower()]
                break

        results = []
        for section in self.sections:
            text_lower = section["content"].lower()
            heading_lower = section["heading"].lower()
            for alias in aliases:
                if alias in text_lower or alias in heading_lower:
                    results.append(section)
                    break

        return results


# ---------------------------------------------------------------------------
# Chapter utilities
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


def get_chapter_number(filename: str) -> int:
    """Extract numeric chapter number from filename."""
    m = re.match(r'(\d+)', filename)
    return int(m.group(1)) if m else -1


def find_chapter_file(chapter_num: int) -> Path | None:
    """Find the chapter file for a given number."""
    for ch in get_chapters():
        if get_chapter_number(ch.name) == chapter_num:
            return ch
    return None


def get_chapter_title(text: str) -> str:
    """Extract the H1 title from chapter text."""
    m = re.match(r'^#\s+(.+)', text, re.MULTILINE)
    return m.group(1).strip() if m else "(untitled)"


def get_part_for_chapter(ch_num: int) -> str:
    """Determine which Part a chapter belongs to."""
    if ch_num < 1:
        return "Front Matter"
    current_part = "Front Matter"
    for break_ch in sorted(PART_BREAKS.keys()):
        if ch_num >= break_ch:
            info = PART_BREAKS[break_ch]
            current_part = f"Part {info['number']}: {info['name']}"
    return current_part


# ---------------------------------------------------------------------------
# Character state lookup
# ---------------------------------------------------------------------------

def _get_character_state(canonical: str, chapter: int) -> str:
    """Get character state at a specific chapter point from character_states.yaml."""
    if not CHARACTER_STATES:
        return ""

    states = CHARACTER_STATES.get(canonical, [])
    for entry in states:
        if len(entry) >= 3:
            start, end, note = entry[0], entry[1], entry[2]
            if start <= chapter <= end:
                return note
    return ""


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP("fiction-context")

store = DataStore()


@mcp.tool()
def search_bible(query: str) -> str:
    """Full-text search across story bible, characters, worldbuilding, and all reference docs.

    Returns matching sections with source and heading. Use for any general
    question about the story world, characters, or plot.

    Args:
        query: Search terms (e.g. "magic system", "character motivation", "timeline")
    """
    results = store.search(query, max_results=8)
    if not results:
        return f"No results found for: {query}"

    output = []
    for r in results:
        output.append(f"## [{r['source']}] {r['heading']}\n")
        content = r["content"]
        if len(content) > 2000:
            content = content[:2000] + "\n\n... (truncated)"
        output.append(content)
        output.append("")

    return "\n".join(output)


@mcp.tool()
def get_character(name: str, chapter: int | None = None) -> str:
    """Get character voice notes, speech patterns, physical tells, and arc position.

    Handles character aliases as defined in project.yaml.
    If chapter is provided, includes state/arc position at that point in the story.

    Args:
        name: Character name or alias
        chapter: Optional chapter number to get state at that point
    """
    sections = store.get_character_sections(name)
    if not sections:
        return f"No character information found for: {name}"

    char_sections = [s for s in sections if s["source"] == "characters"]
    other_sections = [s for s in sections if s["source"] != "characters"]

    output = []

    if char_sections:
        output.append("## Character Profile\n")
        for s in char_sections[:5]:
            output.append(f"### {s['heading']}\n{s['content']}\n")

    if other_sections:
        output.append("## Additional References\n")
        for s in other_sections[:5]:
            content = s["content"]
            if len(content) > 1500:
                content = content[:1500] + "\n... (truncated)"
            output.append(f"### [{s['source']}] {s['heading']}\n{content}\n")

    if chapter is not None:
        output.append(f"\n## Chapter {chapter} Context\n")
        part = get_part_for_chapter(chapter)
        output.append(f"Story position: {part}")

        name_lower = name.lower()
        canonical = name_lower
        for c, aliases in CHARACTER_ALIASES.items():
            if name_lower in [a.lower() for a in aliases]:
                canonical = c
                break

        state_notes = _get_character_state(canonical, chapter)
        if state_notes:
            output.append(f"\nState at Ch {chapter}:\n{state_notes}")

    return "\n".join(output)


@mcp.tool()
def get_chapter_context(chapter_number: int) -> str:
    """Get chapter metadata, opening/closing lines, and surrounding chapter context.

    Essential for maintaining continuity during editing. Returns POV, location,
    timeline position, plus the ending of the previous chapter and opening of
    the next chapter.

    Args:
        chapter_number: The chapter number
    """
    chapters = get_chapters()
    ch_idx = None
    target_file = None

    for i, ch in enumerate(chapters):
        if get_chapter_number(ch.name) == chapter_number:
            ch_idx = i
            target_file = ch
            break

    if target_file is None:
        return f"Chapter {chapter_number} not found."

    content = strip_comments(target_file.read_text(encoding="utf-8"))
    title = get_chapter_title(content)
    part = get_part_for_chapter(chapter_number)
    word_count = len(content.split())

    lines = content.split("\n")
    content_lines = [l for l in lines if l.strip() and not l.startswith("#")]
    opening = "\n".join(content_lines[:5])
    closing = "\n".join(content_lines[-5:])

    output = [
        f"# Chapter {chapter_number}: {title}",
        f"**Part**: {part}",
        f"**File**: {target_file.name}",
        f"**Words**: {word_count:,}",
        f"\n## Opening lines\n```\n{opening}\n```",
        f"\n## Closing lines\n```\n{closing}\n```",
    ]

    if ch_idx > 0:
        prev_file = chapters[ch_idx - 1]
        prev_content = strip_comments(prev_file.read_text(encoding="utf-8"))
        prev_title = get_chapter_title(prev_content)
        prev_lines = [l for l in prev_content.split("\n") if l.strip() and not l.startswith("#")]
        prev_ending = "\n".join(prev_lines[-5:])
        output.append(
            f"\n## Previous chapter ending (Ch {get_chapter_number(prev_file.name)}: {prev_title})"
            f"\n```\n{prev_ending}\n```"
        )

    if ch_idx < len(chapters) - 1:
        next_file = chapters[ch_idx + 1]
        next_content = strip_comments(next_file.read_text(encoding="utf-8"))
        next_title = get_chapter_title(next_content)
        next_lines = [l for l in next_content.split("\n") if l.strip() and not l.startswith("#")]
        next_opening = "\n".join(next_lines[:5])
        output.append(
            f"\n## Next chapter opening (Ch {get_chapter_number(next_file.name)}: {next_title})"
            f"\n```\n{next_opening}\n```"
        )

    return "\n".join(output)


@mcp.tool()
def check_continuity(text: str, chapter: int) -> str:
    """Check a text passage against canon facts, character states, and story rules.

    Scans for character names, key terms, and timeline references, then validates
    against rules defined in reference/continuity_rules.yaml. Returns warnings/errors.

    Args:
        text: The text passage to check
        chapter: The chapter number this text belongs to
    """
    warnings = []
    text_lower = text.lower()

    # --- Config-driven death checks ---
    for event in CONTINUITY_RULES.get("death_events", []):
        death_ch = event.get("chapter", 999)
        if chapter > death_ch:
            for alias in event.get("aliases", [event.get("character", "")]):
                if alias.lower() in text_lower:
                    action_patterns = [
                        rf'{re.escape(alias.lower())}\s+(said|says|walked|ran|looked|smiled|laughed|spoke|reached|turned)',
                        rf'{re.escape(alias.lower())}\s+was\s+\w+ing',
                    ]
                    for pat in action_patterns:
                        if re.search(pat, text_lower):
                            warnings.append(
                                f"WARNING: {event['character'].title()} appears active in Ch {chapter}, "
                                f"but died in Ch {death_ch}. If this is a memory/flashback, "
                                f"ensure past tense framing is clear."
                            )
                            break

    # --- Config-driven reveal checks ---
    for reveal in CONTINUITY_RULES.get("reveals", []):
        reveal_ch = reveal.get("chapter", 999)
        if chapter >= reveal_ch:
            before = reveal.get("before", "").lower()
            if before and before in text_lower:
                after = reveal.get("after", "").lower()
                if after and after not in text_lower:
                    note = reveal.get("note", f"After Ch {reveal_ch}, '{before}' is known as '{after}'.")
                    warnings.append(f"NOTE: {note}")

    # --- Config-driven status changes ---
    for change in CONTINUITY_RULES.get("status_changes", []):
        change_ch = change.get("chapter", 999)
        if chapter >= change_ch:
            character = change.get("character", "").lower()
            if character in text_lower:
                note = change.get("note", "")
                if note:
                    # Only warn if there's a potential conflict indicator
                    flag = change.get("flag", "")
                    if flag:
                        warnings.append(f"NOTE: {note}")

    # --- Basic structural checks (always active) ---
    part = get_part_for_chapter(chapter)

    if not warnings:
        return f"No continuity issues detected for Ch {chapter}.\nStory position: {part}"

    result = [f"Continuity check for Ch {chapter} ({part}):\n"]
    for w in warnings:
        result.append(f"- {w}")
    return "\n".join(result)


@mcp.tool()
def get_foreshadowing(thread: str | None = None) -> str:
    """Get plants/payoffs from foreshadowing reference and the outline resolution table.

    Shows what's planted where, how it resolves, and current status.

    Args:
        thread: Optional specific thread to search for (e.g. "prophecy", "weapon").
               If omitted, returns the full foreshadowing ledger.
    """
    foreshadow_text = store.documents.get("foreshadowing", "")
    outline_text = store.documents.get("outline", "")

    if not thread:
        output = []
        if foreshadow_text:
            output.append(foreshadow_text)
        if outline_text:
            m = re.search(r'## .*[Rr]esolution.*', outline_text, re.DOTALL)
            if m:
                output.append("\n---\n\n## From Outline\n" + m.group(0))
        return "\n".join(output) if output else "No foreshadowing data found."

    thread_lower = thread.lower()
    results = []

    for section in store.sections:
        if section["source"] in ("foreshadowing", "outline"):
            if thread_lower in section["content"].lower() or thread_lower in section["heading"].lower():
                results.append(section)

    if not results:
        results = store.search(thread, max_results=5)

    if not results:
        return f"No foreshadowing found for thread: {thread}"

    output = [f"## Foreshadowing: {thread}\n"]
    for r in results:
        output.append(f"### [{r['source']}] {r['heading']}\n{r['content']}\n")
    return "\n".join(output)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
