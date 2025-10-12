"""Integration tests using real CSV files."""

import csv
from pathlib import Path
from toggl_to_zoho.converter import convert_toggl_to_zoho


def test_full_conversion():
    """Test complete conversion using test CSV files."""
    # Use the test files in the tests directory
    tests_dir = Path(__file__).parent
    input_file = tests_dir / "test-input-toggl.csv"
    expected_output = tests_dir / "test-output-zoho.csv"
    actual_output = tests_dir / "test-output-actual.csv"
    
    # Skip if test files don't exist
    if not input_file.exists() or not expected_output.exists():
        return
    
    try:
        # Run conversion
        convert_toggl_to_zoho(str(input_file), str(actual_output))
        
        # Read both files and compare
        with open(expected_output, encoding='utf-8-sig') as f:
            expected_reader = csv.DictReader(f)
            expected_rows = list(expected_reader)
        
        with open(actual_output, encoding='utf-8-sig') as f:
            actual_reader = csv.DictReader(f)
            actual_rows = list(actual_reader)
        
        # Compare row count
        assert len(actual_rows) == len(expected_rows), \
            f"Row count mismatch: expected {len(expected_rows)}, got {len(actual_rows)}"
        
        # Compare each row
        for i, (expected, actual) in enumerate(zip(expected_rows, actual_rows)):
            assert expected == actual, \
                f"Row {i+1} mismatch:\nExpected: {expected}\nActual: {actual}"
    finally:
        # Clean up - always runs even if test fails
        if actual_output.exists():
            actual_output.unlink()


def test_midnight_crossing_entry():
    """Test that midnight-crossing entries are properly split."""
    tests_dir = Path(__file__).parent
    input_file = tests_dir / "test-input-toggl.csv"
    output_file = tests_dir / "test-output-actual.csv"
    
    if not input_file.exists():
        return
    
    try:
        convert_toggl_to_zoho(str(input_file), str(output_file))
        
        # Read output and check for the split midnight entry
        with open(output_file, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Find entries that span midnight (2025-04-08 23:56 -> 2025-04-09 01:16)
        # These should be split into multiple entries
        midnight_entries = [r for r in rows if 
                           r['Date'] in ('2025-04-08', '2025-04-09') and 
                           r['Notes'] == 'Tool configuration']
        
        # Should have entries on both days
        dates = {r['Date'] for r in midnight_entries}
        assert '2025-04-08' in dates
        assert '2025-04-09' in dates
    finally:
        # Clean up - always runs even if test fails
        if output_file.exists():
            output_file.unlink()
