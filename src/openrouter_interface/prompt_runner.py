#!/usr/bin/env python3
"""
OpenRouter Prompt Runner

A Python program that scans for JSON prompt files and executes them against
input files using the OpenRouter API. Supports both interactive and batch modes.

Required Files:
    - prompt_runner.py (this file)
    - config_manager.py
    - logging_manager.py
    - prompt_scanner.py
    - prompt_handler.py
    - input_handler.py
    - prompt_runner_api_client.py
    - response_handler.py
    - file_handler.py (required by API client)

Required Dependencies:
    - requests
    - yaml
    - pathlib (built-in)
    - json (built-in)
    - logging (built-in)

Environment Variables:
    - OPENROUTER_API_KEY (required) - Your OpenRouter API key

Usage:
    # Interactive mode (original functionality)
    python prompt_runner.py [-o output_file.md] [-c config.yaml] [-l log_file.log]
    
    # Batch mode (new functionality)
    python prompt_runner.py -p prompt.json -i input.md [-o output.md] [-c config.yaml] [-l log_file.log]
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config_manager import ConfigManager
from .logging_manager import LoggingManager
from .prompt_scanner import PromptScanner
from .prompt_handler import PromptLoader, PromptProcessor
from .input_handler import InputFileHandler
from .prompt_runner_api_client import PromptAPIClient
from .response_handler import ResponseHandler


class PromptRunner:
    """Main application class."""
    
    def __init__(self, output_file: str = None, config_file: str = None, log_file: str = None, temp_dir: str = None):
        """Initialize the prompt runner."""
        logging.info("Initializing OpenRouter Prompt Runner")
        
        # Store temp directory
        self.temp_dir = temp_dir
        
        # Initialize configuration manager with optional config file
        self.config = ConfigManager(config_file)
        
        # Handle log file specification and auto-enable file logging
        if log_file:
            # Command line log file takes precedence
            # If temp_dir is provided and log_file is not absolute, put log in temp_dir
            if temp_dir and not Path(log_file).is_absolute():
                temp_log_path = Path(temp_dir) / log_file
                self.config.config['log_file'] = str(temp_log_path)
                logging.info(f"Using temp directory for log file: {temp_log_path}")
            else:
                self.config.config['log_file'] = log_file
                logging.info(f"Command line log file specified: {log_file}")
            self.config.config['log_to_file'] = True
        elif 'log_file' in self.config.config and self.config.config['log_file']:
            # Config file has log_file specified, enable file logging
            # If temp_dir is provided and log_file is not absolute, put log in temp_dir  
            config_log_file = self.config.config['log_file']
            if temp_dir and not Path(config_log_file).is_absolute():
                temp_log_path = Path(temp_dir) / config_log_file
                self.config.config['log_file'] = str(temp_log_path)
                logging.info(f"Using temp directory for config log file: {temp_log_path}")
            else:
                logging.info(f"Config file log file specified: {config_log_file}")
            self.config.config['log_to_file'] = True
        
        # FIXED: Only set defaults for missing values, don't override config file values
        # Create unique payload file name with timestamp and process ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = os.getpid()
        unique_payload_name = f'prompt_runner_{timestamp}_{process_id}.payload.json'
        
        # Set payload file location based on temp_dir
        default_payload_file = unique_payload_name
        if temp_dir:
            default_payload_file = str(Path(temp_dir) / unique_payload_name)
            logging.info(f"Using unique payload file in temp directory: {unique_payload_name}")
        else:
            logging.info(f"Using unique payload file: {unique_payload_name}")
        
        config_defaults = {
            'log_level': 'INFO',
            'payload_file': default_payload_file,
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.8,
            'max_tokens': 25000
        }
        
        # Only set defaults for missing keys, preserve config file values
        for key, default_value in config_defaults.items():
            if key not in self.config.config or self.config.config[key] is None:
                self.config.config[key] = default_value
                logging.debug(f"Set default value for {key}: {default_value}")
            else:
                logging.debug(f"Using config value for {key}: {self.config.config[key]}")
        
        # Initialize logging manager (this will handle log file appending)
        self.logging_manager = LoggingManager(self.config)
        self.api_client = PromptAPIClient(self.config)
        
        # Initialize other components
        self.scanner = PromptScanner()
        self.prompt_loader = PromptLoader()
        self.input_handler = InputFileHandler()
        self.processor = PromptProcessor()
        self.response_handler = ResponseHandler(output_file)
        
        if config_file:
            logging.info(f"✓ Using configuration file: {config_file}")
        if self.config.get('log_to_file'):
            logging.info(f"✓ Logging to file: {self.config.get('log_file')}")
        logging.info("✓ Prompt runner initialized successfully")
    
    def run_batch_mode(self, prompt_file: str, input_file: str) -> bool:
        """
        Run in batch mode with specified files.
        
        Args:
            prompt_file: Path to JSON prompt file
            input_file: Path to input file
            
        Returns:
            True if successful, False otherwise
        """
        separator = "=" * 60
        logging.info(separator)
        logging.info("Running OpenRouter Prompt Runner in BATCH MODE")
        logging.info(f"Prompt file: {prompt_file}")
        logging.info(f"Input file: {input_file}")
        logging.info(separator)
        
        try:
            # Validate and convert to Path objects
            prompt_path = Path(prompt_file)
            input_path = Path(input_file)
            
            # Validate files exist
            if not prompt_path.exists():
                logging.error(f"Prompt file not found: {prompt_path}")
                return False
                
            if not prompt_path.is_file():
                logging.error(f"Prompt path is not a file: {prompt_path}")
                return False
                
            if not input_path.exists():
                logging.error(f"Input file not found: {input_path}")
                return False
                
            if not input_path.is_file():
                logging.error(f"Input path is not a file: {input_path}")
                return False
            
            # Validate file extensions
            if prompt_path.suffix.lower() != '.json':
                logging.warning(f"Prompt file does not have .json extension: {prompt_path}")
            
            logging.info(f"✓ Files validated successfully")
            
            # Load prompt
            logging.info("Step 1: Loading prompt configuration")
            try:
                prompt_data = self.prompt_loader.load_prompt(prompt_path)
                logging.info("✓ Prompt loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load prompt: {e}")
                return False
            
            # Load input content
            logging.info("Step 2: Loading input content")
            try:
                input_content = self.input_handler.load_input_content(input_path)
                logging.info("✓ Input content loaded")
            except Exception as e:
                logging.error(f"Failed to load input content: {e}")
                return False
            
            # Create full prompt
            logging.info("Step 3: Creating full prompt")
            full_prompt = self.processor.create_full_prompt(prompt_data, input_content)
            
            # Call API
            logging.info("Step 4: Calling OpenRouter API")
            try:
                response = self.api_client.call_api(full_prompt)
                logging.info("✓ API call successful")
            except Exception as e:
                logging.error(f"API call failed: {e}")
                return False
            
            # Handle response
            logging.info("Step 5: Processing response")
            self.response_handler.stream_response(response, prompt_path, input_path)
            
            logging.info("✓ Batch processing completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Unexpected error in batch mode: {e}")
            logging.debug("Full error details:", exc_info=True)
            return False
    
    def run_interactive_session(self):
        """Run interactive prompt selection and processing session."""
        separator = "=" * 60
        logging.info(separator)
        logging.info("Starting OpenRouter Prompt Runner in INTERACTIVE MODE")
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


def validate_file_path(file_path: str, file_type: str) -> Path:
    """
    Validate that a file path exists and is accessible.
    
    Args:
        file_path: Path string to validate
        file_type: Description of file type for error messages
        
    Returns:
        Path object if valid
        
    Raises:
        argparse.ArgumentTypeError: If path is invalid
    """
    path = Path(file_path)
    
    if not path.exists():
        raise argparse.ArgumentTypeError(f"{file_type} file not found: {path}")
    
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"{file_type} path is not a file: {path}")
    
    return path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run JSON prompts against input files using OpenRouter API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Mode Selection:
    Interactive Mode (default): Scan directory and select files interactively
    Batch Mode: Process specific files specified via command line

Interactive Mode Examples:
    python prompt_runner.py
    python prompt_runner.py -o responses.md
    python prompt_runner.py -c my_config.yaml -o responses.md
    python prompt_runner.py -l debug.log -v -o responses.md

Batch Mode Examples:
    python prompt_runner.py -p analysis.json -i document.md
    python prompt_runner.py -p review.json -i code.py -o results.md
    python prompt_runner.py -p analysis.json -i data.txt -o analysis.md -c custom_config.yaml
    python prompt_runner.py -p review.json -i code.py -l batch.log -o results.md

Batch Processing Multiple Files:
    # Process multiple files with the same prompt and config, logging to file
    python prompt_runner.py -p review.json -i file1.md -o results.md -c config.yaml -l batch.log
    python prompt_runner.py -p review.json -i file2.md -o results.md -c config.yaml -l batch.log
    python prompt_runner.py -p review.json -i file3.md -o results.md -c config.yaml -l batch.log

Configuration File Format (YAML):
    model: anthropic/claude-4-sonnet-20250522
    api_base_url: https://openrouter.ai/api/v1
    temperature: 0.8
    max_tokens: 25000
    log_level: INFO
    log_to_file: true          # Optional: explicit file logging
    log_file: prompt_runner.log # Automatically enables file logging

Logging Examples:
    # Log to specific file via command line
    python prompt_runner.py -p analysis.json -i doc.md -l debug.log
    
    # Log to file specified in config
    python prompt_runner.py -c config.yaml -p analysis.json -i doc.md
    
    # Combine command line log file with config
    python prompt_runner.py -c config.yaml -l custom.log -p analysis.json -i doc.md

The program will:
1. In Interactive Mode: Scan directory, present menu, get user input
2. In Batch Mode: Process specified files directly
3. Execute the prompt against the input using OpenRouter API
4. Stream the response to console and optionally to a file
        """
    )
    
    # Configuration options
    config_group = parser.add_argument_group('Configuration Options')
    config_group.add_argument(
        '-c', '--config',
        help='Configuration file (YAML format)',
        metavar='CONFIG_FILE'
    )
    
    # Mode selection arguments
    mode_group = parser.add_argument_group('Mode Selection')
    mode_group.add_argument(
        '-p', '--prompt',
        type=lambda x: validate_file_path(x, "Prompt"),
        help='JSON prompt file (enables batch mode)',
        metavar='PROMPT_FILE'
    )
    mode_group.add_argument(
        '-i', '--input',
        type=lambda x: validate_file_path(x, "Input"),
        help='Input file to process (requires --prompt for batch mode)',
        metavar='INPUT_FILE'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '-o', '--output-file',
        help='Output file to append responses (markdown format)',
        metavar='OUTPUT_FILE'
    )
    
    # Logging options
    logging_group = parser.add_argument_group('Logging Options')
    logging_group.add_argument(
        '-l', '--log-file',
        help='Log file path (enables file logging automatically)',
        metavar='LOG_FILE'
    )
    logging_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    logging_group.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress all output except errors'
    )
    
    # Temporary directory option
    logging_group.add_argument(
        '--temp-dir',
        help='Temporary directory for logs and intermediate files',
        metavar='TEMP_DIR'
    )
    
    args = parser.parse_args()
    
    # Validate argument combinations
    if args.prompt and not args.input:
        parser.error("--input is required when --prompt is specified (batch mode)")
    
    if args.input and not args.prompt:
        parser.error("--prompt is required when --input is specified (batch mode)")
    
    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet cannot be used together")
    
    # Determine mode
    batch_mode = args.prompt is not None and args.input is not None
    
    try:
        # Initialize runner with output file, config file, log file, and temp directory
        runner = PromptRunner(args.output_file, args.config, args.log_file, args.temp_dir)
        
        # Adjust logging level if requested
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.info("Verbose logging enabled")
        elif args.quiet:
            logging.getLogger().setLevel(logging.ERROR)
        
        if batch_mode:
            # Run in batch mode
            logging.info(f"Running in batch mode")
            success = runner.run_batch_mode(str(args.prompt), str(args.input))
            
            if success:
                if not args.quiet:
                    print(f"✓ Successfully processed {args.input} with {args.prompt}")
                sys.exit(0)
            else:
                if not args.quiet:
                    print(f"✗ Failed to process {args.input} with {args.prompt}")
                sys.exit(1)
        else:
            # Run in interactive mode
            logging.info(f"Running in interactive mode")
            runner.run_interactive_session()
            
    except Exception as e:
        logging.error(f"Failed to initialize prompt runner: {e}")
        if args.verbose:
            logging.debug("Full error details:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
