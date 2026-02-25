# Publishing Guide

The publishing tool compiles your markdown chapters into professional book formats: EPUB, PDF, HTML, and combined Markdown.

## Quick Start

```bash
# Generate all formats
python tools/publish.py --all

# Just EPUB
python tools/publish.py --epub

# Word count breakdown
python tools/publish.py --count
```

## Output Formats

### EPUB
The most portable ebook format. Works with Kindle (via Send to Kindle), Apple Books, Kobo, and any EPUB reader.

Features:
- Table of contents
- Part divider pages
- Chapter page breaks
- Custom typography via `templates/epub.css`
- Cover image (if configured)
- Chapter illustrations (if available)

### PDF
6x9 inch trim size, suitable for print-on-demand or high-quality reading.

Features:
- Book-class document with Palatino Linotype
- Proper margins for reading
- Cover as first page
- Table of contents
- Chapter page breaks

Requires `xelatex` (install via TeX Live or MiKTeX).

### HTML
Single-page HTML with embedded styles. Good for web reading or sharing.

### Markdown
All chapters combined into a single file with front matter. Useful as an intermediate format or for platforms that accept Markdown.

## Configuration

All settings come from `project.yaml`:

```yaml
project:
  title: "My Novel"
  subtitle: "A Story"
  author: "Author Name"
  publisher: "Publisher Name"
  year: 2026

structure:
  book_dir: "book"
  output_dir: "output"
  cover_image: "cover.png"
  illustrations_src: "images/chapters"
  front_matter:
    - "00_Foreword.md"
    - "00a_Prologue.md"
  parts:
    1:  { number: "I",   name: "Part One" }
    20: { number: "II",  name: "Part Two" }
```

## Book Structure

The publisher assembles the book in this order:

1. **Half-title page** — Just the title, centered
2. **Title page** — Title, subtitle, author, publisher
3. **Copyright page** — Standard copyright notice
4. **Chapters** — In filename order, with part dividers inserted

### Chapter Ordering

Chapters are sorted by the number at the start of their filename:

```
00_Foreword.md      → sorted first
00a_Prologue.md     → sorted after 00
01_First_Chapter.md → sorted next
02_Second.md        → etc.
```

Letters after numbers (like `00a`) sort after the base number.

### Part Dividers

Part dividers are inserted before the first chapter of each part, as defined in `project.yaml`:

```yaml
structure:
  parts:
    1:  { number: "I",   name: "The Beginning" }
    20: { number: "II",  name: "The Middle" }
    40: { number: "III", name: "The End" }
```

This inserts a part divider page before Chapter 1, Chapter 20, and Chapter 40.

### Front Matter

Files listed in `front_matter` are treated as front matter — they don't get part dividers even if their chapter number matches a part break:

```yaml
structure:
  front_matter:
    - "00_Foreword.md"
    - "00a_Prologue.md"
```

## Illustrations

### Setup

1. Place chapter illustrations in your illustrations source directory
2. Name them to match chapter file stems: `01_first_chapter.webp`
3. Configure the source directory:

```yaml
structure:
  illustrations_src: "images/chapters"
```

### Editions

```bash
# Illustrated (default, if illustrations exist)
python tools/publish.py --all

# Plain (no illustrations)
python tools/publish.py --all --no-illustrations

# Both editions
python tools/publish.py --all --both
```

The `--both` flag generates both illustrated and plain editions. Illustrated files get a `_Illustrated` suffix.

### Image Processing

The publisher converts WebP illustrations to 256x256 PNG for EPUB/PDF compatibility. Originals are not modified.

## Customizing Styles

### EPUB CSS

Edit `templates/epub.css` to customize:
- Typography (font family, size, line height)
- Paragraph indentation
- Heading styles
- Scene break rendering (asterism character)
- Front matter positioning
- Illustration sizing

### PDF Settings

PDF uses pandoc with xelatex. To change fonts or margins, edit the `generate_pdf()` function in `tools/publish.py`:

```python
"-V", "mainfont:Your Font Name",
"-V", "fontsize=11pt",
"-V", "geometry:papersize={6in,9in}",
```

## Word Count

```bash
python tools/publish.py --count
```

Shows word count per chapter, grouped by part, with totals. Useful for tracking progress against your outline targets.

## Dependencies

- **pandoc** — Required for all formats except Markdown
- **xelatex** — Required for PDF only
- **Pillow** — Required for illustration processing only
