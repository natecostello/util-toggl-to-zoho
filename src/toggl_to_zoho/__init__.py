"""Convert Toggl time entries to Zoho-compatible CSV format."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("toggl-to-zoho")
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = "0.0.0-dev"
