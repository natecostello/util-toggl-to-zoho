# Agent Instructions for Packaging toggl-to-zoho

## Context
This repository contains a Python command-line utility that converts Toggl time tracking CSV exports to Zoho-compatible CSV format. The goal is to refactor it into a properly packaged Python project following modern best practices while keeping it lightweight.

**Key Decisions:** 
- This is a CLI tool, so `pipx` should be the recommended installation method for end users
- Command name and package name will both be `toggl-to-zoho` for consistency and better UX
- Support stdin/stdout pipes for flexible workflows
- Maintain zero runtime dependencies (stdlib only)

## Quick Reference: What We Built

**Final Structure:**
- Modern src/ layout with `toggl_to_zoho` package
- 33 comprehensive tests (unit, integration, CLI, subprocess)
- stdin/stdout pipe support with auto-detection
- Dynamic versioning (single source in `__init__.py`)
- Sanitized test fixtures (no real customer data)
- Clean documentation with schema mapping table
- Legacy script preserved in `legacy/` directory

## Current State
- Single script file: `toggl2zoho` (Python script without .py extension)
- Uses basic Python libraries: csv, datetime, sys
- No formal package structure
- Development uses virtual environments (venv)
- Current installation: manual copy to `/usr/local/bin`
- Repository name: `util-toggl-to-zoho` (will remain as is, but package will be `toggl-to-zoho`)

## Target Structure
```
util-toggl-to-zoho/                    # Repository name (unchanged)
├── src/
│   └── toggl_to_zoho/             # Module name (Python underscore convention)
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── converter.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_converter.py
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
└── .python-version (optional, for pyenv users)
```

## Implementation Tasks

### Task 1: Create pyproject.toml
Create a modern `pyproject.toml` file with:
- Build system using Hatchling (lightweight, no setuptools needed)
- Project metadata (name: `toggl-to-zoho`, version: 0.1.0)
- Minimal dependencies (only stdlib is currently used, so initially empty)
- Console script entry point: `toggl-to-zoho` (matching package name for UX consistency)
- Optional dev dependencies: pytest, black, ruff
- **Important**: Ensure `[project.scripts]` is properly configured for pipx compatibility

Example:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "toggl-to-zoho"
version = "0.1.0"
description = "Convert Toggl time entries to Zoho-compatible CSV format"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [{name = "Nate Costello"}]

[project.scripts]
toggl-to-zoho = "toggl_to_zoho.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black",
    "ruff",
]
```

### Task 2: Create src/ Layout
Create the `src/toggl_to_zoho/` directory structure:
- `__init__.py`: Package initialization with version info (`__version__ = "0.1.0"`)
- `__main__.py`: Enable `python -m toggl_to_zoho` execution
- `cli.py`: Argument parsing and main CLI entry point with `main()` function
- `converter.py`: Core logic from current `toggl2zoho` script including:
  - `required_headers()` - CSV validation
  - `required_data()` - Data validation
  - `getDuration()` - Time calculations
  - `splitDates()` - Multi-day entry splitting
  - `reformatTime()` - Time format conversion
  - Main conversion workflow
- `utils.py`: Shared utility functions if needed

### Task 3: Refactor Current Script
Break down the monolithic `toggl2zoho` script:
1. Extract validation functions to `converter.py`
2. Extract CSV processing logic to `converter.py`
3. Create CLI interface in `cli.py` that:
   - Accepts input/output file paths as arguments
   - Handles stdin/stdout for piping
   - Provides helpful error messages
   - Has a `main()` function that serves as the entry point
4. Wire up entry points in `__main__.py` and `cli.py`

### Task 4: Add Comprehensive Tests
Create thorough test coverage across multiple levels:

**Unit Tests (`tests/test_converter.py`):**
- Test `getDuration()` with various time ranges including midnight crossings
- Test `splitDates()` with same-day and multi-day entries (2+ days)
- Test `reformatTime()` for time format conversions
- Test `renameBillable()` for Yes/No → Billable/Non Billable mapping
- Test `renameHeaders()` for field name transformations
- Test validation functions with valid/invalid data

**Integration Tests (`tests/test_integration.py`):**
- Full end-to-end conversion with realistic sanitized CSV data (50+ rows)
- Test midnight-crossing entries
- Use try/finally for cleanup to guarantee temp files are removed

**CLI Tests (`tests/test_cli.py`):**
- File-to-file conversion with explicit paths
- Auto-named output files
- stdin/stdout pipe support (explicit `-` and implicit detection)
- File-to-stdout and stdin-to-file combinations
- Error handling (missing files, invalid CSV)
- Data integrity (piped output matches file output)
- Success messages go to stderr when stdout has data

**Real-World Subprocess Tests:**
- Test CLI via `subprocess.run([sys.executable, '-m', 'toggl_to_zoho', ...])`
- Validates the actual user experience
- Tests --version and --help flags

**Test Fixtures:**
- Create sanitized test CSV files with fake data (no real names, emails, clients, projects)
- Store fixtures in `tests/` directory, not repo root
- Use consistent fake data: "John Doe", "john.doe@example.com", "Acme Corp", "Project Alpha"

### Task 5: Update Documentation
Update `README.md` with pipx-first installation instructions:

**Installation Section:**
```markdown
# toggl-to-zoho

Convert Toggl time tracking CSV exports to Zoho Books-compatible CSV format.

## Installation

### For Users (Recommended)
Install using pipx for isolated, global access:
```bash
pipx install git+https://github.com/natecostello/util-toggl-to-zoho.git
```

If you don't have pipx installed:
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### For Developers
Clone and install in editable mode with a virtual environment:
```bash
git clone https://github.com/natecostello/util-toggl-to-zoho.git
cd util-toggl-to-zoho

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Usage
```bash
# Basic usage
toggl-to-zoho input.csv output.csv

# Using pipes
cat toggl-export.csv | toggl-to-zoho > zoho-import.csv

# Get help
toggl-to-zoho --help
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/ tests/
ruff check src/ tests/
```

## Upgrading

To upgrade to the latest version:
```bash
pipx upgrade toggl-to-zoho
```

## Uninstalling

```bash
pipx uninstall toggl-to-zoho
```
```

Include:
- Clear pipx installation instructions as primary method
- How to install pipx itself
- Development setup with venv workflow
- Usage examples with the new CLI command (`toggl-to-zoho`)
- Basic development commands (testing, formatting)
- Upgrade and uninstall instructions

### Task 6: Dynamic Versioning Setup
Configure single source of truth for version:

In `pyproject.toml`:
```toml
[project]
dynamic = ["version"]

[tool.hatchling.version]
path = "src/toggl_to_zoho/__init__.py"
```

This eliminates manual version syncing between `pyproject.toml` and `__init__.py`.
Version is maintained in one place: `src/toggl_to_zoho/__init__.py`

### Task 7: Configuration Files
Update or create:
- `.gitignore`: Add Python-specific ignores:
  ```
  # Python
  __pycache__/
  *.py[cod]
  *$py.class
  *.so
  .Python
  
  # Virtual environments
  venv/
  env/
  ENV/
  
  # Distribution / packaging
  build/
  dist/
  *.egg-info/
  
  # Testing
  .pytest_cache/
  .coverage
  htmlcov/
  
  # IDEs
  .vscode/
  .idea/
  *.swp
  *.swo
  *~
  
  # OS
  .DS_Store
  Thumbs.db
  ```
- **Optional**: `.python-version` file if using pyenv (e.g., `3.12` or `3.11`)
- **Optional**: Consider removing or archiving `.devcontainer/` directory since it's no longer in use

## Design Principles
1. **Lightweight**: Use only stdlib where possible, minimal dependencies
2. **Modern**: Follow PEP 621 (pyproject.toml) and current packaging standards
3. **src/ layout**: Prevents import errors and follows best practices
4. **Installable**: Users can pipx install directly from GitHub
5. **Maintainable**: Clear separation of CLI, business logic, and utilities
6. **pipx-optimized**: Package structure designed for CLI tool isolation
7. **venv-friendly**: Easy local development with virtual environments
8. **Consistent naming**: Package name matches command name (`toggl-to-zoho`) for better UX
9. **Dynamic versioning**: Single source of truth in `__init__.py`, read by pyproject.toml
10. **Pipe-friendly**: Support both file-based and stdin/stdout pipe workflows

## Development Workflow (Post-Implementation)

### Initial Setup
```bash
git clone https://github.com/natecostello/util-toggl-to-zoho.git
cd util-toggl-to-zoho
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Daily Development
```bash
source venv/bin/activate  # Activate venv
# Make changes
pytest                     # Run tests
black src/ tests/          # Format code
ruff check src/ tests/     # Lint code
```

### Testing User Experience
```bash
# Deactivate dev venv
deactivate

# Install with pipx to test user experience
pipx install .
toggl-to-zoho --help

# Uninstall when done testing
pipx uninstall toggl-to-zoho

# Reactivate dev venv
source venv/bin/activate
```

### Optional: Create Personal Alias
If you type the command frequently, add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias t2z='toggl-to-zoho'
```

Then you can use: `t2z input.csv output.csv`

## Installation Methods (Post-Implementation)

### End Users
- **Primary**: `pipx install git+https://github.com/natecostello/util-toggl-to-zoho.git`
- Alternative: `pip install --user git+https://github.com/natecostello/util-toggl-to-zoho.git` (not recommended)

### Developers
- Development mode with venv: `python3 -m venv venv && source venv/bin/activate && pip install -e ".[dev]"`

### Future
- Publish to PyPI for simple: `pipx install toggl-to-zoho`

## Non-Goals
- Don't add unnecessary dependencies
- Don't create standalone executables (PyInstaller) unless specifically requested
- Don't over-engineer - keep it simple and focused
- Don't use pip for user installation examples (use pipx instead)
- Don't require Docker/DevContainers for development
- Don't use inconsistent naming between package and command

## Success Criteria
- ✅ Can install with pipx from GitHub
- ✅ Command `toggl-to-zoho` available globally after pipx installation
- ✅ Package name and command name match (`toggl-to-zoho`)
- ✅ Each installation is isolated from other Python packages
- ✅ Original functionality preserved
- ✅ Code is more maintainable and testable
- ✅ Follows Python packaging best practices
- ✅ Remains lightweight (minimal dependencies)
- ✅ Easy to uninstall: `pipx uninstall toggl-to-zoho`
- ✅ Simple venv-based development workflow
- ✅ Can be developed on any platform without Docker
- ✅ User experience is intuitive (install name matches command name)

## Testing pipx Installation
Before considering the refactor complete, test:
```bash
# Install from local directory
cd /path/to/util-toggl-to-zoho
pipx install .

# Verify command is available
which toggl-to-zoho
toggl-to-zoho --help

# Test functionality
toggl-to-zoho sample-input.csv output.csv

# Uninstall
pipx uninstall toggl-to-zoho

# Install from GitHub (final test)
pipx install git+https://github.com/natecostello/util-toggl-to-zoho.git
toggl-to-zoho --version
```

## Notes on Naming
- **Repository**: `util-toggl-to-zoho` (keeping current name to avoid breaking URLs/clones)
- **Package**: `toggl-to-zoho` (PyPI/pipx install name)
- **Command**: `toggl-to-zoho` (what users type)
- **Module**: `toggl_to_zoho` (Python import name, with underscores)

This ensures:
- Consistency between what users install and what they run
- Follows CLI naming conventions (lowercase, hyphens)
- Follows Python module naming conventions (underscores)
- Professional appearance
- Good discoverability and user experience

## Repository Cleanup (Post-Refactoring)

After completing the refactoring, clean up the repository:

### Files to Remove:
1. **`.devcontainer/`** - Not needed with venv workflow
2. **`dev-notebook.ipynb`** - Extract important info to README, then delete
3. **Schema images** - Replace with markdown tables in documentation

### Files to Relocate:
1. **`toggl2zoho`** - Move to `legacy/` with deprecation notice
   - Create `legacy/README.md` explaining it's deprecated
   - Reference the new package installation method

### Documentation to Enhance:
1. Add **Purpose & Workflow** section to README
2. Add **Schema Requirements** section with field mapping table
3. Document which fields are mapped/unmapped between Toggl and Zoho

### LICENSE Verification:
- Ensure LICENSE file matches what's declared in `pyproject.toml`
- Use MIT license (simple, permissive)
- Verify copyright year and author name

## Release & Versioning Best Practices

### Workflow:
1. **Develop on feature branch** (e.g., `refactor`)
2. **All tests pass** before merging
3. **Merge to main** (no version bump yet)
4. **On main**: Bump version in `__init__.py`
5. **Commit**: "Release v0.1.0"
6. **Tag**: `git tag -a v0.1.0 -m "Version 0.1.0..."`
7. **Push**: `git push origin main && git push origin v0.1.0`

### Version Updates:
- Manually edit `__version__` in `src/toggl_to_zoho/__init__.py`
- Follow Semantic Versioning (MAJOR.MINOR.PATCH)
- No automation needed for simple projects
- Optional: Use `bump-my-version` or `hatch version` for automation

### Feature Branches:
- After merging to main, delete the feature branch locally
- No need to push feature branches to GitHub if merging locally
- Keep main branch clean and linear

## Fresh Repository Start (Optional)

If desired, create a clean initial commit for public release:

### Benefits:
- Clean history without development artifacts
- No risk of sensitive data in old commits
- Professional appearance
- Simpler for new users

### Process:
1. `rm -rf .git` - Remove git history
2. `git init` - Fresh repository
3. `git branch -M main` - Set default branch
4. Update all GitHub URLs in docs to new repo name
5. `git add -A && git commit -m "Initial commit..."`
6. `git tag -a v0.1.0 -m "Version 0.1.0..."`
7. Create new GitHub repository
8. `git remote add origin <new-url>`
9. `git push -u origin main && git push origin v0.1.0`

### When to Use:
- Typo in old repository name
- Development history contains sensitive data (even if later removed)
- Want clean slate for public project
- Prefer single initial commit over messy development history
