#!/usr/bin/env python3
"""
OpenRouter Prompt Runner

A Python program that scans for JSON prompt files and executes them against
input files using the OpenRouter API.

Usage:
    python prompt_runner.py [-o output_file.md]
"""

import argparse
import logging
import sys

from config_manager import ConfigManager
from logging_manager import LoggingManager
from prompt_scanner import PromptScanner
from prompt_handler import PromptLoader, PromptProcessor
from input_handler import InputFileHandler
from prompt_runner_api_client import PromptAPIClient
from response_handler import ResponseHandler


class PromptRunner:
    """Main application class."""
    
    def __init__(self, output_file: str = None):
        """Initialize the prompt runner."""
        logging.info("Initializing OpenRouter Prompt Runner")
        
        # Create a minimal config for API operations
        config_dict = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.8,
            'max_tokens': 10000,
            'log_level': 'INFO',
            'log_to_file': False,
            'payload_file': 'prompt_runner.payload.json'  # Add payload file path
        }
        
        # Initialize components
        self.config = ConfigManager()
        self.config.config = config_dict  # Override with our settings
        self.logging_manager = LoggingManager(self.config)
        self.api_client = PromptAPIClient(self.config)  # Use our custom API client
        
        # Initialize other components
        self.scanner = PromptScanner()
        self.prompt_loader = PromptLoader()
        self.input_handler = InputFileHandler()
        self.processor = PromptProcessor()
        self.response_handler = ResponseHandler(output_file)
        
        logging.info("✓ Prompt runner initialized successfully")
    
    def run_interactive_session(self):
        """Run interactive prompt selection and processing session."""
        separator = "=" * 60
        logging.info(separator)
        logging.info("Starting OpenRouter Prompt Runner")
        logging.info(separator)
        
        try:
            while True:
                # Scan for JSON prompts
                logging.info("Step 1: Scanning for JSON prompt files")
                json_files = self.scanner.scan_for_prompts()
                
                if not json_files:
                    print("No JSON files found in the current directory.")
                    break
                
                # Display menu and get selection
                selected_index = self.scanner.display_prompt_menu(json_files)
                if selected_index is None:
                    print("Goodbye!")
                    break
                
                selected_prompt = json_files[selected_index]
                logging.info(f"✓ Selected prompt: {selected_prompt.name}")
                logging.info(f"✓ Selected prompt full path: {selected_prompt.absolute()}")
                
                # Load prompt
                logging.info("Step 2: Loading prompt configuration")
                try:
                    prompt_data = self.prompt_loader.load_prompt(selected_prompt)
                    logging.info("✓ Prompt loaded successfully")
                except Exception as e:
                    logging.error(f"Failed to load prompt: {e}")
                    continue
                
                # Get input file
                logging.info("Step 3: Getting input file")
                input_file = self.input_handler.get_input_file()
                if input_file is None:
                    continue
                
                logging.info(f"✓ Selected input file: {input_file.name}")
                logging.info(f"✓ Selected input file full path: {input_file.absolute()}")
                
                # Load input content
                logging.info("Step 4: Loading input content")
                try:
                    input_content = self.input_handler.load_input_content(input_file)
                    logging.info("✓ Input content loaded")
                except Exception as e:
                    logging.error(f"Failed to load input content: {e}")
                    continue
                
                # Create full prompt
                logging.info("Step 5: Creating full prompt")
                full_prompt = self.processor.create_full_prompt(prompt_data, input_content)
                
                # Call API
                logging.info("Step 6: Calling OpenRouter API")
                try:
                    response = self.api_client.call_api(full_prompt)
                    logging.info("✓ API call successful")
                except Exception as e:
                    logging.error(f"API call failed: {e}")
                    continue
                
                # Stream response
                logging.info("Step 7: Streaming response")
                self.response_handler.stream_response(response, selected_prompt, input_file)
                
                # Ask if user wants to continue
                print("\nWould you like to run another prompt? (y/n): ", end="")
                if input().strip().lower() not in ['y', 'yes']:
                    print("Goodbye!")
                    break
                    
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
        except Exception as e:
            logging.error(f"Unexpected error in interactive session: {e}")
            logging.debug("Full error details:", exc_info=True)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run JSON prompts against input files using OpenRouter API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python prompt_runner.py
    python prompt_runner.py -o responses.md
    python prompt_runner.py --output-file analysis_results.md

The program will:
1. Scan the current directory for .json files
2. Present a numbered menu of available prompts
3. Ask you to select a prompt and input file
4. Execute the prompt against the input using OpenRouter API
5. Stream the response to console and optionally to a file
        """
    )
    
    parser.add_argument(
        '-o', '--output-file',
        help='Output file to append responses (markdown format)',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        runner = PromptRunner(args.output_file)
        runner.run_interactive_session()
    except Exception as e:
        logging.error(f"Failed to initialize prompt runner: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()