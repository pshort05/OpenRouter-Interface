#!/usr/bin/env python3
"""
CLI entry point for OpenRouter Interface.

This module provides the main entry point for the command-line interface.
"""

import sys
from .prompt_runner import main as prompt_runner_main

def main():
    """Main entry point for the CLI application."""
    try:
        prompt_runner_main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()