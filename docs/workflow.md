# The Parallel-Agent Editorial Workflow

This workflow was developed while creating [The Third Silence](https://thethirdsilence.com), a 286k-word novel edited across 5 complete passes with parallel Claude agents. It describes how to use Claude Code with fiction-forge to write, edit, and polish a novel-length manuscript using parallel AI agents.

## Overview

The workflow has four phases:

1. **Foundation** — Build reference docs before writing
2. **Drafting** — Write with context from the MCP server
3. **Editorial passes** — Systematic improvement in waves
4. **Polish** — Final voice consistency and continuity verification

## Phase 1: Foundation

Before writing a single chapter, build your reference documents. This is the single most important thing you can do for AI-assisted fiction. Without reference docs, agents hallucinate, contradict themselves, and drift from your intended voice.

### Story Bible First

Populate `reference/bible.md` with:

- **Voice analysis**: How your prose sounds. Be specific — "literary first person" is useless. "First person past tense, Anglo-Saxon vocabulary preference, sentences average 15 words with periodic 40-word compounds, no contractions in narration" is useful.
- **Canon decisions**: Immutable plot points. Once locked, agents cannot contradict them.
- **World rules**: Hard constraints on magic, geography, politics. Agents check these.

### Character Profiles

For every significant character, document:

- Speech patterns (not just "talks formally" — give examples)
- Verbal tics and word choices
- What they notice vs. what they miss
- How they change across the story (state timeline)

### Outline

Build your master outline in `reference/outline.md` before drafting. Include:

- Chapter-by-chapter plan with POV, location, word count targets
- Part structure (which chapter starts each part)
- Key plot beats and their chapter assignments

## Phase 2: Drafting with Context

### How the MCP Server Helps

When Claude Code is open in your project directory, it has access to five context tools:

- `search_bible` — Full-text search across all reference docs
- `get_character` — Character voice notes and state at a specific chapter
- `get_chapter_context` — Opening/closing lines of adjacent chapters
- `check_continuity` — Validate text against your rules
- `get_foreshadowing` — Track plant/payoff threads

Agents automatically query these tools while writing. You don't need to paste context into prompts — the MCP server provides it.

### Drafting Instructions

When asking Claude to write a chapter:

```
Write Chapter 12: The Storm Breaks.

Use get_chapter_context to check what happens before and after this chapter.
Use get_character to get voice notes for [character name].
Check continuity when done.

This chapter should:
- Open with [character] arriving at [location]
- The central conflict is [description]
- End with [the cliffhanger/resolution]
- Target: 3,000 words
```

### What Makes Good Agent Instructions

**Do:**
- Give specific scene goals ("the conversation reveals X")
- Specify emotional beats ("she's angry but hiding it")
- Reference the outline ("this is the midpoint reversal")
- Set word count targets (agents tend to under-write without them)

**Don't:**
- Give line-by-line instructions (agents write better with freedom)
- Over-specify dialogue (give the topic, not the words)
- Ask for "beautiful prose" (meaningless; reference your style bible instead)

## Phase 3: Editorial Passes

This is where fiction-forge shines. The editorial process uses a wave pattern with the prose scanner driving prioritization.

### The 5-Phase Editorial Methodology

#### Phase 1: Global Cut Pass
**Goal**: Reduce word count by 10-20% through pattern-driven cuts.

```bash
python tools/prose_scanner.py --summary
```

Identify CRITICAL and HIGH chapters. These have the most overused patterns. Launch agents to fix them:

```
Fix prose patterns in Chapter 15. The scanner flagged:
- em_dash: 2.3/1k (target 1.0)
- found_myself: 0.4/1k (target 0.15)
- show_then_tell: 0.3/1k (target 0.1)

Rules:
- Cut, don't replace. Remove the pattern; don't substitute with another.
- One touch only: each sentence gets edited once.
- Preserve the opening and closing lines exactly.
- Do not add new content. Only cut and tighten.
```

#### Phase 2: Voice Surgery
**Goal**: Eliminate AI writing fingerprints.

Focus on patterns that make prose sound machine-generated:
- `found_myself`, `something_like`, `or_perhaps` — AI favorites
- `show_then_tell` — showing a moment, then explaining it
- `emotional_softening` — defusing tension the reader should feel

#### Phase 3: Structural Pass
**Goal**: Fix pacing, transitions, and chapter-level architecture.

Read each chapter's opening and closing lines. Do they hook and land? Check:
- Does each chapter earn its existence? (If it could be cut, it should be.)
- Do transitions between chapters flow?
- Are there pacing sags in the middle of parts?

#### Phase 4: Precision Pass
**Goal**: Fix remaining scanner issues at the line level.

Re-run the scanner. Address anything above MEDIUM:

```bash
python tools/prose_scanner.py --chapter 15
```

This shows exact line numbers and context for each match.

#### Phase 5: Verification
**Goal**: Confirm all fixes hold and no new issues were introduced.

```bash
python tools/prose_scanner.py --summary
```

All chapters should be LOW or MEDIUM. Any remaining HIGH chapters get one final targeted pass.

### The Wave Pattern for Parallel Editing

The key insight: **you can launch multiple agents on non-overlapping files simultaneously.**

```
Wave 1: Scanner identifies 15 problem chapters
Wave 2: Launch 5-8 agents, each fixing 1-2 chapters (non-overlapping)
Wave 3: Re-scan, fix residual issues from Wave 2
Wave 4: Sequential read for voice consistency (one agent, one chapter at a time)
```

**Critical rule**: Never have two agents editing the same file. Merge conflicts in prose are catastrophic — you can't meaningfully merge two different edits to the same paragraph.

### Agent Prompt Patterns for Editing

**The Subtraction Prompt** (most effective for editorial work):

```
Edit Chapter 22. Your ONLY job is to cut.

Rules:
- Remove instances of [pattern] throughout
- Do not add any new words, sentences, or paragraphs
- Do not rephrase — just delete
- If removing a sentence leaves a gap, tighten the surrounding sentences
- Preserve all dialogue exactly
- Preserve the first and last paragraphs exactly
```

**The Voice Match Prompt**:

```
Edit Chapter 22 to match the voice in our story bible.

Read the style analysis in reference/bible.md first.
Then read the chapter.
Fix any sentences that don't match the documented voice.

Focus on:
- Sentence rhythm (target: [description])
- Register (target: [description])
- Filtering verbs (remove "I noticed/realized/felt")
```

**The Continuity Prompt**:

```
Check Chapter 22 for continuity errors.

Use check_continuity on the full text.
Use get_character for every named character to verify their state.
Use get_chapter_context to verify transitions.

Fix any errors found. Do not change anything else.
```

### What to Watch For

**Pattern introduction by fix agents**: An agent fixing em-dashes might introduce `something like` constructions. Always re-scan after a fix pass.

**Voice drift**: Agents editing for patterns can flatten voice. Compare before/after — if the chapter lost its rhythm, revert and try a more targeted approach.

**Over-writing**: Agents that run too many turns tend to add content. Set clear boundaries: "Cut only. Do not add."

**The minimum viable chapter problem**: Short chapters (under 1,500 words) inflate density scores. A single em-dash in a 500-word chapter gives a density of 2.0/1k — technically over target but not actually a problem. Use judgment.

## Phase 4: Polish

### Sequential Voice Read

After all parallel editing passes, do one final sequential read. One agent, one chapter at a time, in order. The agent reads the previous chapter's ending, the current chapter, and the next chapter's opening. It checks for:

- Voice consistency with adjacent chapters
- Smooth transitions
- Any remaining pattern issues

### Continuity Sweep

Run `check_continuity` on every chapter. Fix any warnings. Update the foreshadowing ledger to confirm all threads are resolved.

### Final Word Count

```bash
python tools/publish.py --count
```

Compare against your targets. Adjust if needed.

## Practical Tips

- **3-4k words is the sweet spot** for new chapters written by agents. Shorter feels thin; longer risks drift.
- **Agent turn limits matter.** An agent that runs 20+ turns will start over-writing. Keep editorial passes to 5-10 turns.
- **The story bible is your most important file.** Every hour spent on it saves ten hours of fixing agent mistakes.
- **Don't fix everything at once.** Pattern-driven passes are more effective than "make this chapter better."
- **Back up before editorial passes.** Git commit before each wave. You will want to revert occasionally.
