# toggl-to-zoho

Convert Toggl time tracking CSV exports to Zoho Books-compatible CSV format.

## Purpose

This command-line utility streamlines the workflow of tracking time in Toggl Track and then importing that data into Zoho Books for invoicing. It "massages" CSV files exported from Toggl Track into a format that Zoho Books can import directly.

**Typical Workflow:**
1. Track all time entries in Toggl Track throughout your billing period
2. Export time entries from Toggl Track as CSV
3. Run `toggl-to-zoho` to convert the CSV format
4. Import the converted CSV into Zoho Books for invoicing

**Important:** For this integration to work properly, you must maintain a **common schema** of project names, user emails, task names, and customer/client names between Zoho Books and Toggl Track. See the Schema Requirements section below for details.

## Features

- ✅ Converts Toggl CSV exports to Zoho Books import format
- ✅ Automatically splits multi-day time entries into separate daily entries
- ✅ Handles midnight-crossing entries correctly
- ✅ Converts billable status (Yes/No → Billable/Non Billable)
- ✅ Reformats time from HH:MM:SS to HH:MM
- ✅ Validates input data and provides clear error messages

## Installation

### For Users (Recommended)

Install using `pipx` for isolated, global access:

```bash
pipx install git+https://github.com/natecostello/util-toggl-to-zoho.git
```

If you don't have `pipx` installed:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

After installation, restart your terminal or run `source ~/.zshrc` (or `~/.bashrc`).

### For Developers

Clone the repository and install in editable mode with a virtual environment:

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

### Basic Usage

```bash
# Convert with explicit output filename
toggl-to-zoho input.csv output.csv

# Convert with automatic output filename (zoho_input.csv)
toggl-to-zoho input.csv

# Get help
toggl-to-zoho --help

# Check version
toggl-to-zoho --version
```

## Schema Requirements

For the integration to work correctly, maintain consistent naming across Toggl Track and Zoho Books for:
- **Project Names**: Must match exactly between systems
- **Task Names**: Must match exactly between systems  
- **User Emails**: Must match exactly between systems
- **Customer/Client Names**: Used for organization in Toggl, not imported to Zoho

### Field Mapping Reference

| Toggl Export Field | Type / Example | → | Zoho Books Import Field | Type / Example | Notes |
|---|---|---:|---|---|---|
| **Project** | String {Project Names} | → | **Project Name** | String {Project Names} | Must match exactly |
| **Task** | String {Task Names} | → | **Task Name** | String {Task Names} | Must match exactly |
| **Description** | String | → | **Notes** | String | Free text |
| **Email** | "user@example.com" | → | **Email** | "user@example.com" | Must match exactly |
| **Billable** | String {"Yes","No"} | → | **Billable Status** | String {"Billable","Non Billable"} | Mapped: Yes→Billable, No→Non Billable |
| **Start Date** | String "YYYY-MM-DD" | → | **Date** | String "YYYY-MM-DD" | If multi-day, split into separate rows |
| **Start Time** | String "HH:MM:SS" | → | **Begin Time** | String "HH:MM" | Seconds trimmed |
| **End Time** | String "HH:MM:SS" | → | **End Time** | String "HH:MM" | Seconds trimmed |
| **Duration** | String "HH:MM:SS" | → | **Time Spent** | String "HH:MM" | Converted to HH:MM |

**Fields not imported to Zoho:**
- User (informational only)
- Client (used in Toggl for organization)
- End Date (handled via date splitting)
- Tags (not supported in Zoho import)
- Amount (not imported)

**Optional Zoho fields** (left blank by this tool):
- Staff Rate
- Billed Status
- Cost Rate

### Required Toggl CSV Format

Your Toggl export must include these columns:
- `User`
- `Email`
- `Client`
- `Project`
- `Task`
- `Description`
- `Billable` (Yes/No)
- `Start date` (YYYY-MM-DD)
- `Start time` (HH:MM:SS)
- `End date` (YYYY-MM-DD)
- `End time` (HH:MM:SS)
- `Duration`
- `Tags`

### Output Zoho CSV Format

The tool generates a CSV with these columns:
- `Project Name`
- `Notes`
- `Email`
- `Task Name`
- `Time Spent` (HH:MM)
- `Begin Time` (HH:MM)
- `End Time` (HH:MM)
- `Date` (YYYY-MM-DD)
- `Billable Status` (Billable/Non Billable)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=toggl_to_zoho

# Run specific test file
pytest tests/test_converter.py
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check formatting without making changes
black --check src/ tests/
```

### Linting

```bash
# Run linter
ruff check src/ tests/

# Fix auto-fixable issues
ruff check --fix src/ tests/
```

### Running Locally Without Installing

```bash
# From the repo root with venv activated
python -m toggl_to_zoho input.csv output.csv
```

## Upgrading

To upgrade to the latest version:

```bash
pipx upgrade toggl-to-zoho
```

Or if you installed from the repository:

```bash
pipx reinstall toggl-to-zoho
```

## Uninstalling

```bash
pipx uninstall toggl-to-zoho
```

## How It Works

1. **Validation**: Checks that all required headers and data are present
2. **Date Splitting**: Entries spanning multiple days are split into separate daily entries
3. **Time Formatting**: Converts times from HH:MM:SS to HH:MM format
4. **Status Conversion**: Changes "Yes/No" to "Billable/Non Billable"
5. **Header Mapping**: Renames Toggl columns to match Zoho's expected format

### Example: Multi-Day Entry Splitting

If you have a Toggl entry that starts on April 8 at 23:00 and ends on April 9 at 02:00:

**Input (Toggl):**
```
Start: 2025-04-08 23:00:00
End: 2025-04-09 02:00:00
```

**Output (Zoho):**
```
Entry 1: 2025-04-08, 23:00 - 23:59 (0:59)
Entry 2: 2025-04-09, 00:00 - 02:00 (2:00)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Nate Costello

## Repository

https://github.com/natecostello/util-toggl-to-zoho

