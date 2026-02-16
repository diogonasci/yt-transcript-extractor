"""Utility functions: logging and filename sanitization."""

import logging
import re


logger = logging.getLogger("study")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with the appropriate level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    root = logging.getLogger("study")
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)


def sanitize_filename(name: str) -> str:
    """Remove or replace characters that are invalid in filenames."""
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", name)
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip(" _.")
    if len(sanitized) > 200:
        sanitized = sanitized[:200].rstrip(" _.")
    return sanitized or "untitled"
