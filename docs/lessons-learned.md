# Lessons Learned

Practical insights from building and editing a 286,000-word novel across 111 chapters using AI-assisted parallel editing with Claude Code.

## The Big Picture

### What Worked

**Reference docs are everything.** The story bible, character profiles, and continuity reference files are the single biggest factor in output quality. Agents with good reference docs produce work that needs light editing. Agents without them produce work that needs rewriting.

**Pattern-driven editing is effective.** The prose scanner provides objective, measurable targets. "Fix em-dash overuse in chapters 12, 15, and 23" is a much better instruction than "make the prose better." Agents respond well to specific, measurable goals.

**Parallel agents work.** Launching 5-8 agents simultaneously on non-overlapping chapters cuts editorial time dramatically. A pass that would take hours sequentially completes in 20-30 minutes.

**The subtraction principle.** The single most effective editing instruction is "cut, don't replace." Agents that remove overused patterns produce cleaner results than agents that try to rewrite sentences. Less is more.

### What Didn't Work

**"Make it better" prompts.** Vague instructions produce vague edits. Agents add flowery descriptions, insert unnecessary transitions, and over-explain things the reader already understood. Always give specific, measurable targets.

**Long-running agents.** Agents that run more than 15-20 turns start degrading. They repeat earlier edits, introduce new patterns while fixing old ones, or begin adding content where they should be cutting. Keep editorial passes focused and short.

**Editing the same file with multiple agents.** Never do this. Merge conflicts in prose are unresolvable — you can't meaningfully combine two different rewrites of the same paragraph. One agent per file, always.

## Agent Behavior Insights

### The 3-4k Word Sweet Spot

New chapters written by agents work best at 3,000-4,000 words. Under 2,000 words, agents produce thin, summary-like chapters that lack texture. Over 5,000 words, agents start padding with unnecessary description and redundant dialogue.

### Pattern Introduction by Fix Agents

An agent fixing em-dash overuse will often introduce `something like` or `found myself` constructions as replacements. An agent removing filter words will add `the kind of X that` constructions. **Always re-scan after a fix pass.** Fix agents solve their target problem while creating new ones.

### Voice Drift During Editing

After 3-4 editorial passes, a chapter can lose its original voice. The rhythm flattens, distinctive constructions get smoothed out, and the prose starts sounding generic. Mitigations:
- Compare before/after versions after each pass
- Keep a "voice anchor" — 2-3 paragraphs of ideal prose in your bible
- Do a final sequential voice-match pass after all pattern fixes

### The Explanation Instinct

AI agents love to explain things. After showing a character's grief through action, an agent will add "That was the grief — the kind that sits in your chest like a stone." This is the `show_then_tell` pattern, and it's the single most common AI writing fingerprint. Train yourself to recognize and cut it.

## Process Insights

### The 5-Phase Methodology

This sequence works well for editorial passes:

1. **Global cut** — Reduce total word count by 10-20%. Scanner-driven. Cut overused patterns everywhere.
2. **Voice surgery** — Remove AI fingerprints. Focus on `found_myself`, `something_like`, `show_then_tell`, `emotional_softening`.
3. **Structural pass** — Fix pacing, transitions, chapter architecture. This is the human-judgment pass.
4. **Precision pass** — Line-level fixes for remaining scanner issues.
5. **Verification** — Re-scan everything. Fix any HIGH or CRITICAL chapters.

### Commit Before Every Wave

Git commit before each wave of parallel editing. You will want to revert. Sometimes an agent makes a chapter worse, and the fastest fix is `git checkout -- book/15_Chapter.md` rather than trying to un-edit.

### The Minimum Viable Chapter Problem

Short chapters (under 1,500 words) produce inflated density scores. A single em-dash in a 500-word chapter gives 2.0/1k density — "over target" but not actually a problem. The scanner works best on chapters of 2,000+ words. For shorter chapters, check the absolute counts, not the density ratios.

### Foreshadowing Discipline

Track every plant immediately. It's tempting to plant a detail and figure out the payoff later, but in a long manuscript with many agents, "later" never comes. Update `reference/foreshadowing.md` after every drafting session. Before writing climactic chapters, review all `planted` threads and decide which need resolution.

## Technical Insights

### MCP Server Startup

The fiction context MCP server loads all reference files at startup. If you change a reference file, restart Claude Code (or the MCP server) to pick up the changes. Changes to chapter files in `book/` are read live — no restart needed.

### Scanner Preset Tuning

Start with the `literary_fiction` preset. If your style naturally uses more of certain patterns (e.g., many similes in fantasy), create a custom preset with adjusted thresholds rather than ignoring all scanner warnings. The goal isn't zero flags — it's catching genuine overuse while respecting your style.

### File Naming Conventions

Chapters must start with a number for the tools to work:

```
01_Chapter_Title.md     ✓
Chapter_01.md           ✗ (number must be first)
The_Opening.md          ✗ (no number)
```

Use two-digit zero-padded numbers for proper sorting: `01`, `02`, ... `99`. Use letter suffixes for insertions: `00a_Prologue.md`.

### Renumbering Chapters

If you need to renumber (after adding or removing chapters), use a two-pass approach to avoid filename collisions:

1. Rename all files to temporary names (`temp_01.md`, `temp_02.md`, ...)
2. Rename temporaries to final names (`01_New_Title.md`, `02_New_Title.md`, ...)

Single-pass renaming fails when source and target names overlap.
