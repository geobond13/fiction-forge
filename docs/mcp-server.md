# Fiction Context MCP Server

The MCP (Model Context Protocol) server gives Claude Code real-time access to your story bible, character profiles, chapter context, continuity rules, and foreshadowing threads. This is what keeps AI agents grounded in your story's facts rather than hallucinating details.

## Architecture

```
Claude Code  <-->  MCP Protocol  <-->  fiction_mcp.py  <-->  Your reference files
                                            |
                                        DataStore
                                    (loaded at startup)
```

The server:
1. Reads `project.yaml` for configuration
2. Loads all files listed in `reference_sources`
3. Parses them into heading-delimited sections
4. Indexes sections for fast search
5. Exposes 5 tools that Claude Code can call

## Setup

The server is registered in `.mcp.json`:

```json
{
  "mcpServers": {
    "fiction-context": {
      "command": "python",
      "args": ["tools/fiction_mcp.py"]
    }
  }
}
```

When you open Claude Code in the project directory, it starts the server automatically.

## Tools

### search_bible

Full-text search across all reference documents.

```
> Search the bible for "magic rules"
> Search the bible for "protagonist backstory"
```

Returns matching sections ranked by relevance, with source file and heading. Truncates long sections at 2,000 characters.

### get_character

Character profile with optional chapter-specific state.

```
> Get character info for "protagonist"
> Get character info for "mentor" at chapter 25
```

Resolves aliases defined in `project.yaml`. If `reference/character_states.yaml` exists and a chapter number is provided, includes the character's state at that point in the story.

### get_chapter_context

Opening/closing lines and surrounding chapter transitions.

```
> Get chapter context for chapter 12
```

Returns:
- Chapter title, part, word count
- First 5 content lines
- Last 5 content lines
- Previous chapter's last 5 lines
- Next chapter's first 5 lines

Essential for maintaining continuity at chapter boundaries.

### check_continuity

Validates a text passage against your continuity rules.

```
> Check continuity of [pasted text] for chapter 80
```

If `reference/continuity_rules.yaml` exists, checks:
- Dead characters appearing alive (with action verbs)
- Identity reveals (using pre-reveal names after the reveal)
- Status changes (referencing outdated character states)

Always checks:
- Part membership (which section of the story this chapter belongs to)

### get_foreshadowing

Query plant/payoff threads.

```
> Get foreshadowing for "the prophecy"
> Get all foreshadowing
```

Searches the foreshadowing reference doc and outline for matching threads.

## Configuration

### Reference Sources

In `project.yaml`:

```yaml
reference_sources:
  bible: "reference/bible.md"
  characters: "reference/characters.md"
  foreshadowing: "reference/foreshadowing.md"
  continuity: "reference/continuity.md"
  outline: "reference/outline.md"
  magic_systems: "reference/magic_systems.md"
```

Add as many sources as you need. The server loads them all and indexes them for search.

### Character Aliases

```yaml
characters:
  aliases:
    john: ["john", "johnny", "j", "the detective"]
    mary: ["mary", "the doctor", "dr. chen"]
```

These aliases are used by `get_character` to resolve fuzzy name references.

### Continuity Rules

Create `reference/continuity_rules.yaml` for automated checks:

```yaml
death_events:
  - character: mentor
    chapter: 45
    aliases: ["mentor", "old man", "grandfather"]

reveals:
  - name: "traitor_identity"
    chapter: 30
    before: "the stranger"
    after: "brother"
    note: "After Ch 30, protagonist knows the stranger is their brother"

status_changes:
  - character: protagonist
    chapter: 60
    flag: "injured"
    note: "Broken leg. Cannot run or fight through Ch 65."
```

### Character States

Create `reference/character_states.yaml` for timeline-aware character info:

```yaml
protagonist:
  - [0, 15, "At the academy. Learning. Optimistic."]
  - [16, 30, "Investigating the murders. Growing suspicious of mentor."]
  - [31, 45, "On the run. Mentor killed. Grief and anger."]
  - [46, 60, "Gathering allies. Planning the confrontation."]

mentor:
  - [0, 44, "Alive. Training protagonist. Hiding a secret."]
  - [45, 999, "DEAD. Killed in Ch 45."]
```

## Performance

The server loads all reference files at startup and holds them in memory. For a typical novel project (5-10 reference files, 100k total words), startup takes under a second. Search is instantaneous — it's simple string matching, not a vector database.

If your reference files are very large (500k+ words), consider splitting them into focused documents rather than one massive file. The section-based indexing works best with well-structured markdown (clear headings, focused sections).

## Adding Custom Tools

The server uses [FastMCP](https://github.com/jlowin/fastmcp). To add a custom tool:

```python
@mcp.tool()
def my_custom_tool(query: str) -> str:
    """Description of what this tool does.

    Args:
        query: What to search for
    """
    # Your logic here
    return "result"
```

Add the function to `tools/fiction_mcp.py` and restart Claude Code to pick up the change.
