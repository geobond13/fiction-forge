# Getting Started

This guide walks you through setting up fiction-forge for your novel project.

## Prerequisites

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **pandoc** — For EPUB/HTML generation. [pandoc.org/installing](https://pandoc.org/installing.html)
- **xelatex** (optional) — For PDF generation. Install via [TeX Live](https://tug.org/texlive/) or [MiKTeX](https://miktex.org/)
- **Claude Code** — For AI-assisted editing. [claude.ai/claude-code](https://claude.ai/claude-code)

## Installation

```bash
git clone https://github.com/yourname/fiction-forge.git
cd fiction-forge
pip install -r requirements.txt
```

## Quick Setup

### 1. Configure your project

Edit `project.yaml` with your book's metadata:

```yaml
project:
  title: "The Weight of Stars"
  author: "Jane Author"
  year: 2026

structure:
  parts:
    1:  { number: "I",   name: "Arrival" }
    15: { number: "II",  name: "Descent" }
    30: { number: "III", name: "Return" }
```

### 2. Create your first chapter

```bash
cp templates/chapter.md book/01_First_Chapter.md
```

Edit the file — replace the placeholder content with your prose. Follow the conventions documented in the template (ALL CAPS opening, metadata block, `---` for scene breaks).

### 3. Set up reference documents

```bash
# The reference/ directory has starter files. Populate them:
# - reference/bible.md       — Your story bible
# - reference/characters.md  — Character profiles
# - reference/foreshadowing.md — Plant/payoff tracking
```

See [Story Bible Guide](story-bible-guide.md) for how to build comprehensive reference docs.

### 4. Register the MCP server

The `.mcp.json` file is already configured. When you open Claude Code in the project directory, it will automatically start the fiction context server. Verify it works:

```
# In Claude Code, try:
> search the bible for "magic system"
> get chapter context for chapter 1
```

### 5. Run the prose scanner

```bash
python tools/prose_scanner.py --summary
```

This scans all chapters in `book/` against the pattern preset defined in `project.yaml`. See [Prose Patterns](prose-patterns.md) for how to interpret results.

### 6. Build your first output

```bash
# EPUB only
python tools/publish.py --epub

# All formats
python tools/publish.py --all

# Word count
python tools/publish.py --count
```

Output files appear in `output/`.

## Directory Structure

```
fiction-forge/
  project.yaml           # All tool configuration
  .mcp.json              # MCP server registration
  CLAUDE.md              # Claude Code project instructions

  book/                  # Your chapters (01_Title.md, 02_Title.md, ...)
  reference/             # Story bible, characters, foreshadowing, continuity
  output/                # Generated EPUB, PDF, HTML, reports
  templates/             # Blank templates for new chapters, characters, etc.
  presets/               # Prose pattern presets and style profiles
  tools/                 # Scanner, publisher, MCP server, image generator
  docs/                  # This documentation
```

## Next Steps

- [Workflow Guide](workflow.md) — The parallel-agent editorial process
- [Prose Patterns](prose-patterns.md) — Understanding and configuring the scanner
- [MCP Server](mcp-server.md) — Deep dive on the context server
- [Publishing](publishing.md) — Multi-format output options
