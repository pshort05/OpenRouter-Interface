#!/usr/bin/env python3
"""
BookGen entry point for OpenRouter Interface.

This module provides the main entry point for the book generation utilities.
"""

import sys

def main():
    """Main entry point for the book generation application."""
    try:
        from .bookGen import main as bookgen_main
        bookgen_main()
    except KeyboardInterrupt:
        print("\nBook generation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()