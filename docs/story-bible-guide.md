# Story Bible Guide

Your story bible is the most important file in your project. AI agents reference it constantly — during drafting, editing, and continuity checking. The quality of your bible directly determines the quality of your AI-assisted output.

## Why Reference Docs Matter

Without a story bible, AI agents:
- Invent character details that contradict earlier chapters
- Drift from your intended voice across long manuscripts
- Miss foreshadowing payoffs
- Apply generic prose patterns instead of your specific style

With a comprehensive bible, agents:
- Maintain consistent character voices across 100+ chapters
- Catch continuity errors before you do
- Reinforce your themes and motifs naturally
- Match your prose style to documented patterns

**Rule of thumb**: Every hour spent on reference docs saves ten hours of fixing agent mistakes.

## Building a Voice Analysis

This is the most critical section. "Write in a literary style" tells an AI nothing. Instead, document specific, observable patterns.

### Step 1: Analyze Sentence Structure

Read 10 pages of your drafted prose (or your target author if emulating a style) and note:

- **Average sentence length**: Count words in 20 random sentences. "14-18 words with periodic 35-word compounds" is specific.
- **Sentence variety**: Do you alternate long and short? Use fragments? Start with participial phrases?
- **Paragraph length**: How many sentences per paragraph? Do they vary by scene type?

### Step 2: Identify Vocabulary Patterns

- **Register**: Anglo-Saxon vs. Latinate roots? Formal vs. colloquial?
- **Contractions**: In narration? In dialogue only? Never?
- **Jargon**: Technical terms for your world (magic, technology, culture)
- **Forbidden words**: Words that don't belong in your world or style

### Step 3: Document POV Conventions

- **Tense**: Past or present?
- **Person**: First, third limited, omniscient?
- **Reliability**: Is the narrator honest? What do they omit?
- **Filtering**: Do you use "I saw" or direct description?

### Step 4: Note Structural Patterns

- **Opening convention**: ALL CAPS first line? Epigraph? Scene-setting?
- **Scene breaks**: What triggers a break within a chapter?
- **Dialogue formatting**: Tags ("said" only?) or action beats?
- **Songs/letters**: How are they formatted?

### Example Voice Analysis

> **POV**: First person past tense, retrospective narrator. He's telling the story years later and occasionally steps outside the moment to comment — but sparingly.
>
> **Sentence rhythm**: 14-18 word average. Long compounds (35+ words) in descriptive passages, broken by 3-5 word declaratives for impact. Never two long sentences in a row.
>
> **Vocabulary**: Anglo-Saxon preference in action ("gut" not "intuition", "quick" not "expeditious"). Latinate for magic system terminology. No contractions in narration; contractions in all dialogue.
>
> **Signature patterns**: Tricolon (groups of three). Silence as metaphor. Sensory details always precede emotional reactions.
>
> **Avoid**: Exclamation marks (never in narration, rarely in dialogue). "Suddenly" (show the interruption). Adverbs in dialogue tags.

## Documenting Characters

### Voice Notes Are More Important Than Backstory

An AI doesn't need to know a character's childhood trauma to write their dialogue. It needs to know:

- How they start sentences (questions? declarations? evasions?)
- Words they'd use and words they wouldn't
- How they respond to conflict (fight? deflect? go quiet?)
- Their verbal tics (repeated phrases, filler words, dialect)

### Example Character Voice Notes

> **Speech patterns**: Short, clipped sentences. Drops pronouns when stressed ("Don't need help" not "I don't need help"). Asks rhetorical questions when annoyed.
>
> **Vocabulary**: Blue-collar register. Swears casually but never uses slurs. Knows nautical terms from her father. Mispronounces academic words deliberately.
>
> **When lying**: Over-explains. Adds unnecessary detail. Uses "honestly" and "to be frank."
>
> **Internal voice**: More articulate than her speech. Notices sounds before visuals. Self-deprecating but not self-pitying.

## Canon Decisions

### What to Lock

Lock any decision that, if changed, would break multiple chapters:

- Character deaths
- Identity reveals
- Major plot turns
- World rules (what magic can/cannot do)
- Timeline anchors (when events happen relative to each other)

### How to Lock

Add it to the canon decisions table with:
- The decision itself
- Which chapter(s) it affects
- Why it was made (so you don't reverse it later on a whim)
- The date it was locked

Once locked, treat it as immutable. If you need to change a canon decision, update the table and note the change — then review every chapter that depends on it.

## Maintaining the Bible

### Update As You Write

Don't wait until the end to update reference docs. After drafting each chapter:
1. Add any new characters to the character roster
2. Log any foreshadowing plants
3. Update character state timelines
4. Note any new world rules established

### Review Before Editorial Passes

Before launching editing agents, verify your bible is current. Stale reference docs cause agents to revert fixes or introduce new errors.

### Version Control

Commit your bible changes alongside chapter changes. If you need to revert a chapter edit, you want the corresponding reference state to revert too.
