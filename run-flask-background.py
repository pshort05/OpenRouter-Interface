#!/usr/bin/env python3
"""
Background Flask runner script for OpenRouter Interface.
This script avoids import issues by using absolute imports.
"""

import sys
import os
import argparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for background Flask execution."""
    parser = argparse.ArgumentParser(description="Background Flask Runner")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--foreground', action='store_true', help='Run in foreground')
    
    args = parser.parse_args()
    
    try:
        # Enable shutdown functionality for development
        os.environ['ALLOW_SHUTDOWN'] = 'true'
        if args.debug:
            os.environ['FLASK_ENV'] = 'development'
            
        # Import with absolute path after setting up sys.path
        from openrouter_interface.prompt_runner_flask import FlaskPromptRunner
        
        # Create and run the Flask app
        flask_runner = FlaskPromptRunner()
        flask_runner.app.run(
            host=args.host, 
            port=args.port, 
            debug=args.debug,
            use_reloader=False,  # Disable reloader for background execution
            threaded=True
        )
        
    except Exception as e:
        print(f"Error starting Flask application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()