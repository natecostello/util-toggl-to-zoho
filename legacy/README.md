# Legacy Implementation

This directory contains the original single-file implementation of the Toggl-to-Zoho converter.

## ⚠️ DEPRECATED

**This script is no longer maintained.** Please use the modern package version instead.

### Modern Installation

```bash
uv tool install git+https://github.com/natecostello/util-toggl-to-zoho.git
```

### Modern Usage

```bash
# File-to-file conversion
toggl-to-zoho input.csv output.csv

# Pipe support
cat toggl-export.csv | toggl-to-zoho > zoho-import.csv

# Help
toggl-to-zoho --help
```

## Why Keep This?

The original `toggl2zoho` script is preserved here for:
- Historical reference
- Understanding the evolution of the project
- Comparing behavior with the refactored version
- Learning purposes

## What Changed?

The modern version includes:
- ✨ Proper Python package structure
- 📦 Easy installation via uv
- 🔧 stdin/stdout pipe support
- 🧪 Comprehensive test suite (33 tests)
- 📚 Better documentation
- 🎯 Dynamic versioning
- 🐍 Python 3.8+ support

All the core functionality remains the same - this is purely a structural improvement.
