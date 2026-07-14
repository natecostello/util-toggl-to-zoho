# Copilot Instructions

## Role

You are a code reviewer only. Deliver all feedback as inline review comments with
suggestion blocks on the PR. Include concrete code suggestions wherever possible
rather than descriptive-only feedback.

Do NOT act as a coding agent. Do NOT open sub-PRs, create branches, or push commits.
All feedback must be review comments.

## Repository Summary

Python CLI utility that converts Toggl time tracking CSV exports to Zoho Books-compatible
CSV format for invoicing workflows. Zero runtime dependencies (stdlib only). Python 3.9+,
managed with uv and hatchling.

## Build, Test, and Lint

```bash
uv sync                                    # Install dependencies
uv run pytest                              # Run tests (~0.2s)
uv run ruff check src/ tests/              # Lint
uv run ruff format --check src/ tests/     # Format check
```

No environment variables required. Tests use fixture CSV files in `tests/`.

## Architecture

Single-purpose converter pipeline: read Toggl CSV -> validate -> transform -> write Zoho CSV.

Key transformations:
- Duration calculation with midnight-crossing handling
- Multi-day entry splitting into separate daily rows
- Time reformatting (HH:MM:SS -> HH:MM)
- Field renaming and billable status mapping (Yes/No -> Billable/Non Billable)

No external services or databases. All I/O is file-based CSV.

## Project Layout

```
src/toggl_to_zoho/
  __init__.py       — __version__, read from installed metadata (importlib.metadata)
  cli.py            — argparse CLI: file args, auto-naming, stdin/stdout piping
  converter.py      — Core conversion: validation, duration calc, date splitting, field mapping
  __main__.py       — Module entry point
tests/
  test_converter.py — Unit tests for individual conversion functions
  test_cli.py       — CLI behavior, stdin/stdout piping, subprocess tests
  test_integration.py — End-to-end with fixture files
  test-input-toggl.csv / test-output-zoho.csv — Test fixtures
legacy/
  toggl2zoho        — Original monolithic script (reference only)
```

Configuration files:
- `pyproject.toml` — dependencies, ruff config, pytest config, hatchling build
- `.github/workflows/ci.yml` — CI: ruff lint/format + pytest on Python 3.9, 3.12, 3.13

## Key Abstractions

- `convert_toggl_to_zoho(input, output)` — Main entry point; accepts file paths or file-like objects
- `required_headers(reader)` / `required_data(reader)` — Input validation
- `get_duration(start_date, start_time, end_date, end_time)` — Duration calc with midnight handling
- `split_multi_day_entry(row)` — Splits entries spanning multiple days into daily rows

## Dependencies and Non-Obvious Relationships

- Zero runtime dependencies — only stdlib `csv`, `datetime`, `argparse`
- Dev dependencies are in `[dependency-groups]` (not `[project.optional-dependencies]`), so `uv sync` installs them automatically
- `version` in `pyproject.toml` is the single source of truth — `__init__.py` and the CLI `--version` flag read it back via `importlib.metadata.version("toggl-to-zoho")`, so no version literal exists outside the manifest
- CLI sends success messages to stderr to keep stdout clean for piping

## Coding Conventions

- Python 3.9+, managed with uv
- Ruff for linting and formatting, 100 char line length
- Ruff lint rules: E, W, F, I, B, C4
- Build backend: hatchling with a static `version` in `pyproject.toml`
- Naming: package/command uses hyphens (`toggl-to-zoho`), Python module uses underscores (`toggl_to_zoho`)

## Code Review Focus Areas

1. **CSV field mapping correctness** — verify Toggl column names map to correct Zoho columns; mismatches silently produce bad output
2. **Date/time edge cases** — midnight crossings, multi-day splits, and duration calculations must handle boundary conditions
3. **Stdin/stdout piping** — CLI must keep stdout clean (no status messages) when used in pipes
4. **No runtime dependencies** — do not introduce external packages; this tool is stdlib-only by design
5. **Input validation** — required headers and data checks should produce clear, actionable error messages

## What NOT to Flag

- Do not suggest adding type annotations beyond what exists — the codebase uses typing selectively
- Do not suggest replacing `csv` module with pandas or similar — stdlib-only is intentional
- Do not flag `Exception` raises in validation — these are user-facing error messages, not internal errors
- Do not suggest adding logging — print-to-stderr is the deliberate approach for this CLI
- Do not suggest reorganizing imports beyond what ruff enforces
- Do not flag the `legacy/` directory — it is preserved for reference only, not maintained
