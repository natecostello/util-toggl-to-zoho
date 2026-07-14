# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CLI utility that converts Toggl time tracking CSV exports to Zoho Books-compatible CSV format. Zero runtime dependencies (stdlib only). Python 3.9+.

## Commands

```bash
# Setup
uv sync

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_converter.py::TestGetDuration::test_simple_duration

# Format
uv run ruff format src/ tests/

# Lint
uv run ruff check --fix src/ tests/

# Run locally
uv run python -m toggl_to_zoho input.csv output.csv
toggl-to-zoho input.csv output.csv          # if installed
cat input.csv | toggl-to-zoho > output.csv   # pipe mode
```

## Architecture

- **`src/toggl_to_zoho/converter.py`** — Core conversion logic: CSV validation, duration calculation (handles midnight crossings), multi-day entry splitting, time reformatting (HH:MM:SS→HH:MM), field renaming (Toggl→Zoho column mapping). Main entry: `convert_toggl_to_zoho()` accepts both file paths and file-like objects.
- **`src/toggl_to_zoho/cli.py`** — argparse CLI. Supports file args, auto-generated output names (`zoho_<input>`), and stdin/stdout piping (explicit `-` or auto-detected). Success messages go to stderr to keep stdout clean for piping.
- **`src/toggl_to_zoho/__init__.py`** — Exposes `__version__`, read from installed package metadata via `importlib.metadata.version("toggl-to-zoho")`. Not a version literal — see [Versioning](#versioning).
- **`legacy/toggl2zoho`** — Original monolithic script, preserved for reference.

## Testing

Three test levels in `tests/`:
- **`test_converter.py`** — Unit tests for individual conversion functions
- **`test_cli.py`** — CLI behavior including stdin/stdout piping, error handling, and subprocess tests via `subprocess.run`
- **`test_integration.py`** — End-to-end conversion using fixture files (`test-input-toggl.csv` → `test-output-zoho.csv`)

## Code Style

- Ruff: formatting + linting, 100 char line length, Python 3.9 target
- Ruff lint rules: E, W, F, I, B, C4
- Build backend: hatchling (configured in `pyproject.toml`)

## Versioning

Version handling follows the `app-version-management` skill: the single version
literal lives in `pyproject.toml`; runtime code reads it via
`importlib.metadata.version("toggl-to-zoho")`. Distribution name: `toggl-to-zoho`
(executable: `toggl-to-zoho`). Never hardcode a version string elsewhere. The one
exception is the `0.0.0-dev` sentinel in `__init__.py`, which is what `__version__`
falls back to when the package is not installed (running straight from a source
tree); it is a "not installed" marker, not a release version, and it never changes
when the real version is bumped.

This tool is installed from git HEAD, so merging to main IS the release: a PR that
makes `uv tool upgrade` produce a functionally different tool carries a version bump
in `pyproject.toml` (patch by default). Docs/CI/test-only PRs do not bump.

## Code Review

GitHub Copilot is configured as a PR code reviewer. Its instructions are in
[`.github/copilot-instructions.md`](.github/copilot-instructions.md). Copilot reviews
deliver inline comments with suggestion blocks. Use `/resolve-pr-comments` to process
review feedback.

## Naming Conventions

- Repository: `util-toggl-to-zoho`
- Package/command: `toggl-to-zoho` (hyphens)
- Python module: `toggl_to_zoho` (underscores)
