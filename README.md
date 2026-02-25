# fiction-forge

**AI-assisted novel writing toolkit** | A [Galleys.ai](https://galleys.ai) project

Prose pattern scanner, MCP context server, multi-format publisher, and a battle-tested editorial workflow for novel-length manuscripts. Works with [Claude Code](https://claude.ai/claude-code).

## What's Included

**Tools**
- **Prose Scanner** — Detects 24 overused patterns (em-dashes, similes, AI fingerprints, voice drift) with severity scoring and cluster detection
- **MCP Context Server** — Gives Claude Code real-time access to your story bible, character profiles, continuity rules, and foreshadowing threads
- **Publisher** — Compiles markdown chapters into EPUB, PDF, HTML with cover images, part dividers, and professional typography
- **Image Generator** — Batch DALL-E 3 illustration generator with rate limiting and manifest tracking

**Templates**
- Story bible, character profiles, foreshadowing ledger, chapter template, editorial notes format, master outline

**Presets**
- Literary fiction and genre fiction pattern presets with configurable thresholds
- Style profiles (Rothfuss, Sanderson) as examples

**Documentation**
- Complete workflow guide for parallel-agent editorial passes
- Prose pattern reference, MCP server deep dive, publishing guide
- Lessons learned from a real 286k-word project

## Quick Start

```bash
git clone https://github.com/geobond13/fiction-forge.git
cd fiction-forge
pip install -r requirements.txt
```

1. Edit `project.yaml` with your book's title, author, and part structure
2. Copy `templates/chapter.md` to `book/01_First_Chapter.md` and start writing
3. Populate `reference/bible.md` with your story's voice rules and canon decisions
4. Run `python tools/prose_scanner.py --summary` to scan for pattern issues
5. Open Claude Code in the project — the MCP server starts automatically

## Architecture

```
project.yaml          Single config file — all tools read from here
     |
     ├── tools/
     │   ├── fiction_mcp.py      MCP server (5 tools for Claude Code)
     │   ├── prose_scanner.py    Pattern detection + severity reports
     │   ├── publish.py          Markdown → EPUB / PDF / HTML
     │   └── generate_images.py  DALL-E 3 batch illustration generator
     │
     ├── presets/
     │   ├── patterns/           Prose pattern definitions (YAML)
     │   └── style_profiles/     Author style references
     │
     ├── reference/              Your story's source of truth
     │   ├── bible.md            Story bible
     │   ├── characters.md       Character profiles
     │   ├── foreshadowing.md    Plant/payoff tracking
     │   └── continuity.md       Timeline and state tracking
     │
     ├── book/                   Your chapters (00_Prologue.md, 01_Title.md, ...)
     ├── templates/              Blank templates for new files
     └── docs/                   Process documentation
```

## The Workflow

The core editorial process uses **parallel AI agents** coordinated by the prose scanner:

1. **Foundation** — Build your story bible and outline before writing
2. **Draft** — Write chapters with MCP context keeping agents grounded
3. **Scan** — Identify problem chapters by severity tier
4. **Fix in waves** — Launch parallel agents on non-overlapping files
5. **Re-scan** — Verify fixes, catch new issues introduced by agents
6. **Polish** — Sequential voice consistency pass

See [docs/workflow.md](docs/workflow.md) for the complete process.

## Scanner Output

```
================================================================================
  Prose Pattern Scan — 45 chapters
================================================================================

  Tiers: CRITICAL=2  HIGH=5  MEDIUM=12  LOW=26

  Pattern                   Count   Density    Target
  -------------------------------------------------------
  em_dash                     142     0.87/1k    1.00/1k
  like_a_an                    89     0.55/1k    0.60/1k
  found_myself                 12     0.07/1k    0.15/1k
  show_then_tell                8     0.05/1k    0.10/1k

  Ch    File                           Words  Score Tier     Top issues
  ----  ---------------------------    -----  ----- ----     ----------
  12    12_The_Storm.md                3,421   14.2 CRITICAL em_dash=2.3/1k, 3 clusters
  23    23_Aftermath.md                2,890    8.1 HIGH     show_then_tell=0.4/1k
```

## Case Study: The Third Silence

fiction-forge was developed and battle-tested on [The Third Silence](https://thethirdsilence.com), a 286,000-word, 111-chapter fan completion of Patrick Rothfuss's Kingkiller Chronicle.

- 5 complete editorial passes using parallel Claude agents
- 24 chapters expanded, 8 new chapters written with AI assistance
- 60+ chapters modified across the editorial fix plan
- Prose scanner identified and fixed 2,000+ pattern overuses

Read the full process writeup at [thethirdsilence.com](https://thethirdsilence.com).

## Documentation

- [Getting Started](docs/getting-started.md) — Setup and first steps
- [Workflow Guide](docs/workflow.md) — The parallel-agent editorial process
- [Prose Patterns](docs/prose-patterns.md) — Understanding the scanner
- [MCP Server](docs/mcp-server.md) — Context server deep dive
- [Story Bible Guide](docs/story-bible-guide.md) — Building effective reference docs
- [Publishing](docs/publishing.md) — Multi-format output
- [Lessons Learned](docs/lessons-learned.md) — Practical insights from a real project

## Requirements

- Python 3.11+
- [pandoc](https://pandoc.org/installing.html) (for EPUB/HTML generation)
- [xelatex](https://tug.org/texlive/) (for PDF generation, optional)
- [Claude Code](https://claude.ai/claude-code) (for AI-assisted editing)
- OpenAI API key (for DALL-E image generation, optional)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting pattern presets, adding tools, and code style.

## License

MIT — see [LICENSE](LICENSE).

---

A [Galleys.ai](https://galleys.ai) project | [The Third Silence](https://thethirdsilence.com)
