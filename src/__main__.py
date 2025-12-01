"""
Entry point for running snowflake_linter as a module.

Usage:
    python -m snowflake_linter <path> [--report <output>] [--verbose]
"""

import sys

if __name__ == '__main__':
    # Import and run main from linter module
    from linter import main
    main()
