# Contributing to fiction-forge

Thanks for your interest in contributing. fiction-forge is a [Galleys.ai](https://galleys.ai) project.

## Ways to Contribute

### Submit Pattern Presets

Pattern presets live in `presets/patterns/`. To add a new one:

1. Create a YAML file following the format in `presets/patterns/literary_fiction.yaml`
2. Define patterns with `regex`, `description`, and `target_density` fields
3. Include a comment header explaining what genre/style the preset targets
4. Test against a few chapters to verify thresholds are reasonable

### Add Style Profiles

Style profiles in `presets/style_profiles/` document author-specific prose patterns. Include:

- Sentence length distribution
- Vocabulary preferences
- Common constructions and rhythms
- Example passages

### Add New Tools

Tools live in `tools/`. New tools should:

1. Read configuration from `project.yaml`
2. Include a `--help` flag with clear usage
3. Work from the project root directory
4. Handle missing optional dependencies gracefully

### Improve Documentation

Docs live in `docs/`. Fix errors, clarify steps, or add new guides.

## Code Style

- Python 3.11+
- Type hints on function signatures
- Docstrings on public functions
- No external dependencies beyond what's in `requirements.txt` without discussion

## Submitting Changes

1. Fork the repo
2. Create a feature branch (`git checkout -b add-mystery-preset`)
3. Make your changes
4. Test that existing tools still work (`python tools/prose_scanner.py --help`)
5. Open a pull request with a clear description of what you added

## Issues

- **Bug reports**: Include the command you ran, the error output, and your Python version
- **Feature requests**: Describe the use case, not just the feature
- **Pattern suggestions**: Include example text showing the pattern and why it matters
