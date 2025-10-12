"""Tests for the CLI functionality including stdin/stdout support."""

import io
import sys
import csv
from pathlib import Path
from unittest.mock import patch
import pytest
from toggl_to_zoho.cli import main


class TestCLIFileToFile:
    """Tests for traditional file-to-file conversion."""
    
    def test_explicit_input_output(self, tmp_path):
        """Test with explicit input and output files."""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        output_file = tmp_path / "output.csv"
        
        with patch('sys.argv', ['toggl-to-zoho', str(input_file), str(output_file)]):
            main()
        
        assert output_file.exists()
        with open(output_file, encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))
            assert len(rows) == 50
            assert rows[0]['Project Name'] == 'Project Alpha'
    
    def test_auto_named_output(self, tmp_path):
        """Test with only input file (auto-generate output name)."""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        
        # Change to tmp directory so auto-named file is created there
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            with patch('sys.argv', ['toggl-to-zoho', str(input_file)]):
                main()
            
            expected_output = tmp_path / f"zoho_{input_file.name}"
            assert expected_output.exists()
            
            with open(expected_output, encoding='utf-8-sig') as f:
                rows = list(csv.DictReader(f))
                assert len(rows) == 50
        finally:
            os.chdir(original_dir)
    
    def test_file_not_found(self, capsys):
        """Test error handling for missing input file."""
        with patch('sys.argv', ['toggl-to-zoho', 'nonexistent.csv', 'output.csv']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert 'not found' in captured.err


class TestCLIStdinStdout:
    """Tests for stdin/stdout pipe support."""
    
    def test_stdin_to_stdout(self):
        """Test piping: cat input.csv | toggl-to-zoho > output.csv"""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        
        # Read test input
        with open(input_file, 'rb') as f:
            input_data = f.read()
        
        # Mock stdin and stdout
        fake_stdin = io.BytesIO(input_data)
        fake_stdout = io.BytesIO()
        
        # Create text wrappers
        stdin_wrapper = io.TextIOWrapper(fake_stdin, encoding='utf-8-sig')
        stdout_wrapper = io.TextIOWrapper(fake_stdout, encoding='utf-8-sig', write_through=True)
        
        with patch('sys.stdin', stdin_wrapper):
            with patch('sys.stdout', stdout_wrapper):
                with patch('sys.stdin.isatty', return_value=False):
                    with patch('sys.argv', ['toggl-to-zoho']):
                        main()
        
        # Read output (main() already flushed)
        output_data = fake_stdout.getvalue().decode('utf-8-sig')
        
        # Verify output
        reader = csv.DictReader(io.StringIO(output_data))
        rows = list(reader)
        assert len(rows) == 50
        assert rows[0]['Project Name'] == 'Project Alpha'
    
    def test_explicit_stdin_to_stdout(self):
        """Test: cat input.csv | toggl-to-zoho - -"""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        
        with open(input_file, 'rb') as f:
            input_data = f.read()
        
        fake_stdin = io.BytesIO(input_data)
        fake_stdout = io.BytesIO()
        
        stdin_wrapper = io.TextIOWrapper(fake_stdin, encoding='utf-8-sig')
        stdout_wrapper = io.TextIOWrapper(fake_stdout, encoding='utf-8-sig', write_through=True)
        
        with patch('sys.stdin', stdin_wrapper):
            with patch('sys.stdout', stdout_wrapper):
                with patch('sys.argv', ['toggl-to-zoho', '-', '-']):
                    main()
        
        output_data = fake_stdout.getvalue().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(output_data))
        rows = list(reader)
        assert len(rows) == 50
    
    def test_stdin_to_file(self, tmp_path):
        """Test: cat input.csv | toggl-to-zoho - output.csv"""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        output_file = tmp_path / "output.csv"
        
        with open(input_file, 'rb') as f:
            input_data = f.read()
        
        fake_stdin = io.BytesIO(input_data)
        stdin_wrapper = io.TextIOWrapper(fake_stdin, encoding='utf-8-sig')
        
        with patch('sys.stdin', stdin_wrapper):
            with patch('sys.argv', ['toggl-to-zoho', '-', str(output_file)]):
                main()
        
        assert output_file.exists()
        with open(output_file, encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))
            assert len(rows) == 50
    
    def test_file_to_stdout(self):
        """Test: toggl-to-zoho input.csv -"""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        
        fake_stdout = io.BytesIO()
        stdout_wrapper = io.TextIOWrapper(fake_stdout, encoding='utf-8-sig', write_through=True)
        
        with patch('sys.stdout', stdout_wrapper):
            with patch('sys.argv', ['toggl-to-zoho', str(input_file), '-']):
                main()
        
        output_data = fake_stdout.getvalue().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(output_data))
        rows = list(reader)
        assert len(rows) == 50
        assert rows[0]['Task Name'] == 'Task A'
    
    def test_no_input_no_pipe_error(self, capsys):
        """Test error when no input file and stdin is not piped."""
        with patch('sys.stdin.isatty', return_value=True):
            with patch('sys.argv', ['toggl-to-zoho']):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 2  # argparse error
    
    def test_success_message_to_stderr_not_stdout(self, capsys):
        """Test that success messages go to stderr when using stdout for data."""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        
        fake_stdout = io.BytesIO()
        stdout_wrapper = io.TextIOWrapper(fake_stdout, encoding='utf-8-sig', write_through=True)
        
        # Need to patch sys.stderr as well to capture it with capsys
        with patch('sys.stdout', stdout_wrapper):
            with patch('sys.argv', ['toggl-to-zoho', str(input_file), '-']):
                main()
        
        # Success message should not be in stdout when piping
        # (No success message is printed when output is stdout)
        
        # stdout should only have CSV data
        output_data = fake_stdout.getvalue().decode('utf-8-sig')
        assert output_data.startswith('Project Name,Notes,Email')
        assert 'Successfully' not in output_data


class TestCLIDataIntegrity:
    """Tests verifying data integrity through pipes."""
    
    def test_piped_output_matches_file_output(self, tmp_path):
        """Test that piped output is identical to file output."""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        file_output = tmp_path / "file_output.csv"
        
        # Generate file output
        with patch('sys.argv', ['toggl-to-zoho', str(input_file), str(file_output)]):
            main()
        
        # Generate piped output
        fake_stdout = io.BytesIO()
        stdout_wrapper = io.TextIOWrapper(fake_stdout, encoding='utf-8-sig', write_through=True)
        
        with patch('sys.stdout', stdout_wrapper):
            with patch('sys.argv', ['toggl-to-zoho', str(input_file), '-']):
                main()
        
        # Compare
        with open(file_output, 'rb') as f:
            file_data = f.read()
        
        pipe_data = fake_stdout.getvalue()
        
        # They should be identical (including BOM)
        assert file_data == pipe_data
    
    def test_round_trip_through_pipes(self, tmp_path):
        """Test stdin -> stdout maintains data integrity."""
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        expected_output = tests_dir / "test-output-zoho.csv"
        
        # Read input
        with open(input_file, 'rb') as f:
            input_data = f.read()
        
        # Process through pipes
        fake_stdin = io.BytesIO(input_data)
        fake_stdout = io.BytesIO()
        
        stdin_wrapper = io.TextIOWrapper(fake_stdin, encoding='utf-8-sig')
        stdout_wrapper = io.TextIOWrapper(fake_stdout, encoding='utf-8-sig', write_through=True)
        
        with patch('sys.stdin', stdin_wrapper):
            with patch('sys.stdout', stdout_wrapper):
                with patch('sys.stdin.isatty', return_value=False):
                    with patch('sys.argv', ['toggl-to-zoho']):
                        main()
        
        # Compare with expected output
        with open(expected_output, encoding='utf-8-sig') as f:
            expected_rows = list(csv.DictReader(f))
        
        output_data = fake_stdout.getvalue().decode('utf-8-sig')
        actual_rows = list(csv.DictReader(io.StringIO(output_data)))
        
        assert len(actual_rows) == len(expected_rows)
        for i, (expected, actual) in enumerate(zip(expected_rows, actual_rows)):
            assert expected == actual, f"Row {i+1} mismatch"


class TestCLIEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_empty_csv_file(self, tmp_path):
        """Test handling of empty CSV file."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        output_file = tmp_path / "output.csv"
        
        with patch('sys.argv', ['toggl-to-zoho', str(empty_file), str(output_file)]):
            with pytest.raises(SystemExit):
                main()
    
    def test_invalid_csv_format(self, tmp_path, capsys):
        """Test handling of CSV with missing required headers."""
        bad_file = tmp_path / "bad.csv"
        bad_file.write_text("Not,A,Valid,Toggl,CSV\n1,2,3,4,5\n")
        output_file = tmp_path / "output.csv"
        
        with patch('sys.argv', ['toggl-to-zoho', str(bad_file), str(output_file)]):
            with pytest.raises(SystemExit):
                main()
        
        captured = capsys.readouterr()
        assert 'Error' in captured.err


class TestCLIRealWorldSubprocess:
    """Integration tests calling the CLI as a subprocess (like a real user)."""
    
    def test_cli_as_subprocess_file_to_file(self, tmp_path):
        """Test calling toggl-to-zoho as a subprocess with files."""
        import subprocess
        import sys
        
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        output_file = tmp_path / "output.csv"
        
        # Call the CLI as a subprocess using python -m
        result = subprocess.run(
            [sys.executable, '-m', 'toggl_to_zoho', str(input_file), str(output_file)],
            capture_output=True,
            text=True
        )
        
        # Should succeed
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists()
        
        # Verify output
        with open(output_file, encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))
            assert len(rows) == 50
            assert rows[0]['Project Name'] == 'Project Alpha'
    
    def test_cli_as_subprocess_pipe_stdin_stdout(self):
        """Test calling toggl-to-zoho with pipes (like: cat input.csv | toggl-to-zoho > output.csv)."""
        import subprocess
        import sys
        
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        
        # Read input data
        with open(input_file, 'rb') as f:
            input_data = f.read()
        
        # Pipe stdin to stdout using python -m
        result = subprocess.run(
            [sys.executable, '-m', 'toggl_to_zoho', '-', '-'],
            input=input_data,
            capture_output=True
        )
        
        # Should succeed
        assert result.returncode == 0, f"Command failed: {result.stderr.decode()}"
        
        # Verify output
        output_data = result.stdout.decode('utf-8-sig')
        rows = list(csv.DictReader(io.StringIO(output_data)))
        assert len(rows) == 50
        assert rows[0]['Project Name'] == 'Project Alpha'
    
    def test_cli_as_subprocess_implicit_pipe(self):
        """Test: cat input.csv | toggl-to-zoho (implicit stdin/stdout)."""
        import subprocess
        import sys
        
        tests_dir = Path(__file__).parent
        input_file = tests_dir / "test-input-toggl.csv"
        
        with open(input_file, 'rb') as f:
            input_data = f.read()
        
        # No arguments, just piped data using python -m
        result = subprocess.run(
            [sys.executable, '-m', 'toggl_to_zoho'],
            input=input_data,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Command failed: {result.stderr.decode()}"
        output_data = result.stdout.decode('utf-8-sig')
        rows = list(csv.DictReader(io.StringIO(output_data)))
        assert len(rows) == 50
    
    def test_cli_as_subprocess_version(self):
        """Test --version flag."""
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, '-m', 'toggl_to_zoho', '--version'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert '0.1.0' in result.stdout
    
    def test_cli_as_subprocess_help(self):
        """Test --help flag."""
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, '-m', 'toggl_to_zoho', '--help'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'Convert Toggl' in result.stdout
        assert 'Examples:' in result.stdout
