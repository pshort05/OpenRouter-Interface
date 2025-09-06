#!/usr/bin/env python3
"""
Chain runner entry point for OpenRouter Interface.

This module provides the main entry point for the prompt chain runner.
"""

import sys

def main():
    """Main entry point for the chain runner application."""
    try:
        from .prompt_chain_runner import main as chain_main
        chain_main()
    except KeyboardInterrupt:
        print("\nChain execution cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()