#!/usr/bin/env python3
"""
Web interface entry point for OpenRouter Interface.

This module provides the main entry point for the Flask web application.
"""

import sys
import os

def main():
    """Main entry point for the web application."""
    try:
        # Import Flask app after ensuring we have flask installed
        try:
            from .prompt_runner_flask import app, main as flask_main
        except ImportError:
            print("Error: Flask is required for the web interface.")
            print("Install with: pip install openrouter-interface[web]")
            sys.exit(1)
        
        # Run the Flask application
        flask_main()
        
    except KeyboardInterrupt:
        print("\nWeb server stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting web server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()