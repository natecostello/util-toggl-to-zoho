"""Command-line interface for toggl-to-zoho converter."""

import sys
import argparse
import io
from pathlib import Path
from toggl_to_zoho.converter import convert_toggl_to_zoho


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Convert Toggl time tracking CSV exports to Zoho-compatible CSV format.',
        epilog='''Examples:
  toggl-to-zoho input.csv output.csv          # File to file
  toggl-to-zoho input.csv                     # Auto-named output
  cat input.csv | toggl-to-zoho > output.csv  # Pipe stdin to stdout
  cat input.csv | toggl-to-zoho - output.csv  # Explicit stdin to file
  toggl-to-zoho input.csv -                   # File to stdout
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        default=None,
        help='Path to the Toggl CSV export file (or "-" for stdin)'
    )
    
    parser.add_argument(
        'output',
        nargs='?',
        default=None,
        help='Path to the output Zoho CSV file (or "-" for stdout, default: zoho_<input> or stdout if stdin)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Determine if input is from stdin
    input_is_stdin = False
    if args.input is None or args.input == '-':
        # Check if stdin is being piped
        if not sys.stdin.isatty() or args.input == '-':
            input_is_stdin = True
            args.input = '-'
        elif args.input is None:
            parser.error("No input file specified and stdin is not piped")
    
    # Determine output destination
    output_is_stdout = False
    if args.output is None:
        if input_is_stdin:
            # Reading from stdin, default to stdout
            args.output = '-'
            output_is_stdout = True
        else:
            # Reading from file, create auto-named output
            input_path = Path(args.input)
            args.output = f"zoho_{input_path.name}"
    elif args.output == '-':
        output_is_stdout = True
    
    try:
        # Prepare input source
        if input_is_stdin:
            # Use stdin directly (already a TextIOWrapper)
            input_handle = sys.stdin
        else:
            input_handle = args.input
        
        # Prepare output destination  
        if output_is_stdout:
            # Use stdout directly (already a TextIOWrapper)
            output_handle = sys.stdout
        else:
            output_handle = args.output
        
        # Perform conversion
        convert_toggl_to_zoho(input_handle, output_handle)
        
        # Flush output if using stdout
        if output_is_stdout:
            sys.stdout.flush()
        
        # Only print success message if not writing to stdout
        if not output_is_stdout:
            input_name = 'stdin' if input_is_stdin else args.input
            print(f"Successfully converted {input_name} to {args.output}", file=sys.stderr)
    
    except FileNotFoundError as e:
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
