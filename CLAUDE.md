# Fiction-Forge Project Instructions

## Project Context

This is a novel manuscript project managed with fiction-forge tools. The AI assistant
has access to a fiction context MCP server with 5 tools for querying story reference
material.

## Available MCP Tools

When editing or writing chapters, use these tools proactively:

- `search_bible` — Search all reference docs for world/plot/character info
- `get_character` — Get voice notes and state for a character at a specific chapter
- `get_chapter_context` — Get opening/closing lines of surrounding chapters
- `check_continuity` — Validate text against continuity rules
- `get_foreshadowing` — Check plant/payoff thread status

## Writing Conventions

- **Opening lines**: First line of every chapter in ALL CAPS (first few words)
- **Scene breaks**: Use `---` (horizontal rule) between scenes within a chapter
- **Metadata**: HTML comment block at top of each chapter with POV, Location, Timeline
- **Songs/letters/epigraphs**: Use blockquotes (`>` prefix)
- **Emphasis**: `*italics*` for emphasis and internal thought

## Editorial Rules

When editing prose:

1. **Cut, don't replace.** Remove overused patterns; don't substitute with different patterns.
2. **One touch per sentence.** Each sentence gets edited once per pass.
3. **Preserve openings and closings.** First and last paragraphs of each chapter are protected.
4. **No new content during cut passes.** Only remove and tighten.
5. **Check continuity after every edit.** Use the `check_continuity` tool.

## File Structure

- `book/` — Chapter files (numbered: `01_Title.md`, `02_Title.md`)
- `reference/` — Story bible, characters, foreshadowing, continuity
- `project.yaml` — All tool configuration
- `output/` — Generated EPUB, PDF, HTML, scan reports

## Common Tasks

### Writing a new chapter
```
Write Chapter N: [Title].
Use get_chapter_context to check adjacent chapters.
Use get_character for each character in the scene.
Target: 3,000-4,000 words.
Check continuity when done.
```

### Fixing prose patterns
```
Fix prose patterns in Chapter N. The scanner flagged:
- [pattern]: [density] (target [target])
Rules: Cut only. Do not add content. Preserve first/last paragraphs.
```

### Continuity check
```
Check Chapter N for continuity. Use check_continuity on the full text.
Use get_character for every named character to verify their state.
Fix any issues found.
```
