# Prose Pattern Scanner

The prose scanner detects overused syntactic patterns in your manuscript and generates severity-tiered reports. It's the primary tool for identifying which chapters need editorial attention.

## How It Works

The scanner reads every chapter in `book/`, counts regex pattern matches, calculates density (occurrences per 1,000 words), and compares against target thresholds. Chapters exceeding targets get flagged with a severity score.

### Density Calculation

```
density = (match_count / word_count) * 1000
```

A chapter with 3,000 words and 4 em-dashes has a density of 1.33/1k. If the target is 1.0/1k, it's over threshold.

### Severity Score

Each over-target pattern contributes to the severity score:

```
contribution = (density - target_density) * weight
```

Patterns with higher weights (e.g., `something_complicated` at 3.0) penalize more heavily than lower-weight patterns (e.g., `sentence_start_and` at 0.5).

Additional penalties:
- Each **cluster** (3+ of the same pattern in 150 words) adds 1.5 to severity
- Each **repeated opening** (3+ sentences starting the same way) adds 1.0

### Severity Tiers

| Tier | Score | Meaning |
|------|-------|---------|
| CRITICAL | 12.0+ | Multiple severe pattern overuses; needs major editing |
| HIGH | 6.0+ | Noticeable pattern issues; should be addressed |
| MEDIUM | 3.0+ | Minor issues; fix if time permits |
| LOW | < 3.0 | Clean prose; no action needed |

Thresholds are configurable in `project.yaml`:

```yaml
scanner:
  severity:
    critical: 12.0
    high: 6.0
    medium: 3.0
```

## Usage

```bash
# Full scan — all chapters, summary table
python tools/prose_scanner.py --summary

# Full scan with JSON report
python tools/prose_scanner.py

# Single chapter with line-by-line detail
python tools/prose_scanner.py --chapter 12

# Override preset
python tools/prose_scanner.py --preset genre_fiction
```

## Understanding the Output

### Summary Table

```
  Pattern                   Count   Density    Target
  -------------------------------------------------------
  em_dash                     342     1.19/1k    1.00/1k **
  like_a_an                   156     0.54/1k    0.60/1k
  found_myself                 23     0.08/1k    0.15/1k
```

Patterns marked `**` are over target globally. Individual chapters may be over even when the global average is fine.

### Chapter Table

```
  Ch    File                      Words  Score Tier     Top issues
  ----  ------------------------  -----  ----- -------- ----------
  12    12_The_Storm.md           3,421   8.2  HIGH     em_dash=2.1/1k, found_myself=0.4/1k
  15    15_Aftermath.md           2,890  14.5  CRITICAL show_then_tell=0.5/1k, 2 clusters
```

### Chapter Detail

With `--chapter N`, you get exact line numbers:

```
  em_dash: 7 (2.05/1k, target 1.00/1k) ** OVER TARGET
    L  23: ...the door — heavy oak bound with iron — swung open...
    L  47: ...she paused — not from uncertainty — but from...
    L  89: ...three things — silence, shadow, and the smell of...
```

## Pattern Categories

### Core Prose Patterns
Basic constructions that become noticeable when overused:
- `em_dash` — Parenthetical asides with em-dashes
- `like_a_an` — Simile constructions ("like a river")
- `as_if` — As-if/as-though comparisons
- `the_way` — "The way she looked at him"
- `hedging_verbs` — "seemed to", "appeared to"
- `sentence_start_and/but` — Sentences opening with conjunctions

### AI Fingerprint Patterns
Constructions that AI models overuse, making prose sound machine-generated:
- `filter_words` — "I noticed", "I realized", "I felt"
- `found_myself` — "found myself wondering"
- `something_like` — "something like grief"
- `for_a_long_moment` — Padding that can be cut
- `or_perhaps` — AI's favorite equivocation
- `passive_emotion` — "was filled with rage"
- `named_emotion_bare` — "felt anger" instead of showing it
- `emotional_softening` — "but there was no malice"

### Voice Drift Patterns
Constructions that break the narrative voice:
- `show_then_tell` — Showing a moment, then explaining it
- `the_kind_of` — "the kind of silence that..."
- `the_particular` — False precision
- `retrospective_foreshadow` — "years later, I would understand"
- `something_vague` — "something shifted between us"

### Precision Patterns
Specific constructions that should rarely (or never) appear:
- `not_x_not_y_but_z` — Rhetorical Not-X, Not-Y, But-Z
- `something_complicated` — Never the right word
- `silence_was_not` — Overused silence characterization
- `triple_simile_stack` — Three "like" comparisons in one sentence
- `might_have_been` — Conditional past weakening assertions

## Presets

### literary_fiction (default)
Strict thresholds. Designed for dense, carefully crafted prose where every word counts.

### genre_fiction
~30% higher thresholds. Appropriate for fantasy, sci-fi, thriller, and other genre work where faster pacing naturally increases some pattern densities.

### Custom Presets

Copy `presets/patterns/custom.yaml.example` and modify:

```yaml
patterns:
  - name: my_pattern
    regex: "\\bmy\\s+regex\\b"
    target_density: 0.5
    weight: 2.0
    description: "Why this pattern matters"
```

Reference in `project.yaml`:

```yaml
scanner:
  preset: "presets/patterns/my_patterns.yaml"
```

Or use the CLI flag:

```bash
python tools/prose_scanner.py --preset presets/patterns/my_patterns.yaml
```

## Cluster Detection

The scanner detects **clusters** — 3 or more occurrences of the same pattern within a 150-word window. Clusters are especially jarring to readers because the repetition is noticeable within a single paragraph or page.

```
  CLUSTERS (2):
    em_dash: 4x in 89 words (lines 23-31)
    like_a_an: 3x in 120 words (lines 67-74)
```

Even if overall chapter density is acceptable, clusters should be broken up.

## Tips

- **Run the scanner before and after every editorial pass.** Fix agents can introduce new patterns while removing others.
- **Don't chase zero.** A LOW severity score is fine. Some patterns are necessary and natural.
- **Short chapters inflate density.** A 500-word chapter with 2 em-dashes shows 4.0/1k — technically high, but not actually a problem. Use judgment.
- **The scanner finds the problems; you decide the fixes.** Not every flagged line needs changing. Sometimes the pattern is exactly right for that moment.
