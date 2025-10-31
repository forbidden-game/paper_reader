"""Entry point for paper_reader module."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    from paper_reader.main import cli

    sys.exit(cli())
