# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CLI utility that converts Toggl time tracking CSV exports to Zoho Books-compatible CSV format. Zero runtime dependencies (stdlib only). Python 3.8+.

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
- **`src/toggl_to_zoho/__init__.py`** — Single source of truth for `__version__` (read by hatchling for dynamic versioning).
- **`legacy/toggl2zoho`** — Original monolithic script, preserved for reference.

## Testing

Three test levels in `tests/`:
- **`test_converter.py`** — Unit tests for individual conversion functions
- **`test_cli.py`** — CLI behavior including stdin/stdout piping, error handling, and subprocess tests via `subprocess.run`
- **`test_integration.py`** — End-to-end conversion using fixture files (`test-input-toggl.csv` → `test-output-zoho.csv`)

## Code Style

- Ruff: formatting + linting, 100 char line length, Python 3.8 target
- Ruff lint rules: E, W, F, I, B, C4
- Build backend: hatchling (configured in `pyproject.toml`)

## Naming Conventions

- Repository: `util-toggl-to-zoho`
- Package/command: `toggl-to-zoho` (hyphens)
- Python module: `toggl_to_zoho` (underscores)
