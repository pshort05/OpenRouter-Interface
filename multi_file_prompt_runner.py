#!/usr/bin/env python3
"""
Multi-File Prompt Runner

An advanced utility that extends prompt_runner.py to support complex prompts
with multiple attached files (up to 10). Handles sophisticated prompting
scenarios where additional context files need to be referenced.

Features:
- Complex prompt support with file attachments
- Up to 10 additional files per prompt execution
- Reuses existing codebase (config, logging, API client)
- JSON-based prompt configuration with file references
- Full integration with existing project infrastructure

Usage:
    # Interactive mode - scan and select complex prompts
    python multi_file_prompt_runner.py

    # Batch mode - process specific complex prompt with attachments  
    python multi_file_prompt_runner.py -p complex_prompt.json -i main_input.md

    # With configuration and logging
    python multi_file_prompt_runner.py -p prompt.json -i input.md -c config.yaml -l debug.log
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config_manager import ConfigManager
from logging_manager import LoggingManager
from prompt_scanner import PromptScanner
from input_handler import InputFileHandler
from prompt_runner_api_client import PromptAPIClient
from response_handler import ResponseHandler


class MultiFilePromptLoader:
    """Loads and validates complex JSON prompt files with file attachments."""
    
    def load_complex_prompt(self, prompt_file: Path) -> Dict[str, Any]:
        """
        Load and validate a complex JSON prompt file.
        
        Args:
            prompt_file: Path to complex JSON prompt file
            
        Returns:
            Complex prompt configuration dictionary
        """
        logging.info(f"Loading complex prompt from: {prompt_file}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_data = json.load(f)
            
            logging.debug(f"Loaded complex prompt data keys: {list(prompt_data.keys())}")
            
            # Validate complex prompt structure
            self._validate_complex_prompt(prompt_data, prompt_file)
            
            return prompt_data
            
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in complex prompt file {prompt_file}: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to load complex prompt file {prompt_file}: {e}")
            raise
    
    def _validate_complex_prompt(self, prompt_data: Dict[str, Any], prompt_file: Path):
        """
        Validate complex prompt data structure.
        
        Args:
            prompt_data: Prompt configuration data
            prompt_file: Path to prompt file (for error reporting)
        """
        # Required fields for complex prompts
        required_fields = ['instruction', 'main_prompt']
        
        for field in required_fields:
            if field not in prompt_data:
                raise ValueError(f"Missing required field '{field}' in complex prompt {prompt_file}")
        
        # Validate attached files if present
        if 'attached_files' in prompt_data:
            self._validate_attached_files(prompt_data['attached_files'], prompt_file)
        
        # Validate referenced prompts if present
        if 'referenced_prompts' in prompt_data:
            self._validate_referenced_prompts(prompt_data['referenced_prompts'], prompt_file)
            
        logging.info(f"✓ Complex prompt validation passed for {prompt_file}")
    
    def _validate_attached_files(self, attached_files: List[Dict[str, str]], prompt_file: Path):
        """Validate attached files configuration."""
        if not isinstance(attached_files, list):
            raise ValueError(f"'attached_files' must be a list in {prompt_file}")
        
        if len(attached_files) > 10:
            raise ValueError(f"Maximum 10 attached files allowed, found {len(attached_files)} in {prompt_file}")
        
        for i, file_config in enumerate(attached_files):
            if not isinstance(file_config, dict):
                raise ValueError(f"Attached file {i+1} must be an object in {prompt_file}")
            
            required_file_fields = ['name', 'path', 'description']
            for field in required_file_fields:
                if field not in file_config:
                    raise ValueError(f"Attached file {i+1} missing '{field}' in {prompt_file}")
            
            # Check if file exists
            file_path = Path(file_config['path'])
            if not file_path.exists():
                raise FileNotFoundError(f"Attached file not found: {file_path} (referenced in {prompt_file})")
            
            logging.debug(f"✓ Validated attached file: {file_config['name']} -> {file_path}")
    
    def _validate_referenced_prompts(self, referenced_prompts: List[Dict[str, str]], prompt_file: Path):
        """Validate referenced prompts configuration."""
        if not isinstance(referenced_prompts, list):
            raise ValueError(f"'referenced_prompts' must be a list in {prompt_file}")
        
        for i, prompt_config in enumerate(referenced_prompts):
            if not isinstance(prompt_config, dict):
                raise ValueError(f"Referenced prompt {i+1} must be an object in {prompt_file}")
            
            required_prompt_fields = ['name', 'path', 'purpose']
            for field in required_prompt_fields:
                if field not in prompt_config:
                    raise ValueError(f"Referenced prompt {i+1} missing '{field}' in {prompt_file}")
            
            # Check if prompt file exists
            ref_prompt_path = Path(prompt_config['path'])
            if not ref_prompt_path.exists():
                raise FileNotFoundError(f"Referenced prompt not found: {ref_prompt_path} (referenced in {prompt_file})")
            
            logging.debug(f"✓ Validated referenced prompt: {prompt_config['name']} -> {ref_prompt_path}")


class MultiFilePromptProcessor:
    """Processes complex prompts with multiple file attachments."""
    
    def __init__(self, input_handler: InputFileHandler):
        """Initialize with input handler for file processing."""
        self.input_handler = input_handler
    
    def create_complex_prompt(self, prompt_data: Dict[str, Any], main_input_content: str) -> str:
        """
        Create a complex prompt with attached files and referenced prompts.
        
        Args:
            prompt_data: Complex prompt configuration
            main_input_content: Main input file content
            
        Returns:
            Fully constructed prompt string
        """
        logging.info("Creating complex prompt with file attachments")
        
        # Start with the main instruction
        full_prompt = prompt_data['instruction'] + "\n\n"
        
        # Add main prompt content
        full_prompt += prompt_data['main_prompt'] + "\n\n"
        
        # Process attached files
        if 'attached_files' in prompt_data:
            full_prompt += self._process_attached_files(prompt_data['attached_files'])
        
        # Process referenced prompts  
        if 'referenced_prompts' in prompt_data:
            full_prompt += self._process_referenced_prompts(prompt_data['referenced_prompts'])
        
        # Add the main input content
        full_prompt += "=== MAIN INPUT TO PROCESS ===\n"
        full_prompt += main_input_content + "\n\n"
        
        # Add final instructions if present
        if 'final_instructions' in prompt_data:
            full_prompt += "=== FINAL INSTRUCTIONS ===\n"
            full_prompt += prompt_data['final_instructions'] + "\n"
        
        logging.info(f"✓ Complex prompt created, total length: {len(full_prompt)} characters")
        return full_prompt
    
    def _process_attached_files(self, attached_files: List[Dict[str, str]]) -> str:
        """Process and embed attached files into the prompt."""
        logging.info(f"Processing {len(attached_files)} attached files")
        
        files_section = "=== ATTACHED FILES ===\n"
        
        for i, file_config in enumerate(attached_files, 1):
            file_path = Path(file_config['path'])
            file_name = file_config['name']
            description = file_config['description']
            
            logging.info(f"Loading attached file {i}: {file_name} ({file_path})")
            
            try:
                file_content = self.input_handler.load_file_content(file_path)
                
                files_section += f"\n--- ATTACHED FILE {i}: {file_name} ---\n"
                files_section += f"Description: {description}\n"
                files_section += f"File Path: {file_path}\n\n"
                files_section += file_content + "\n"
                
                logging.debug(f"✓ Loaded attached file {i}: {len(file_content)} characters")
                
            except Exception as e:
                logging.error(f"Failed to load attached file {file_name}: {e}")
                files_section += f"\n--- ATTACHED FILE {i}: {file_name} (LOAD FAILED) ---\n"
                files_section += f"Error: {e}\n"
        
        files_section += "\n"
        return files_section
    
    def _process_referenced_prompts(self, referenced_prompts: List[Dict[str, str]]) -> str:
        """Process and embed referenced prompts into the prompt."""
        logging.info(f"Processing {len(referenced_prompts)} referenced prompts")
        
        prompts_section = "=== REFERENCED PROMPTS ===\n"
        
        for i, prompt_config in enumerate(referenced_prompts, 1):
            prompt_path = Path(prompt_config['path'])
            prompt_name = prompt_config['name']
            purpose = prompt_config['purpose']
            
            logging.info(f"Loading referenced prompt {i}: {prompt_name} ({prompt_path})")
            
            try:
                # Load the referenced prompt file
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    import json
                    ref_prompt_data = json.load(f)
                
                # Extract the main instruction/content
                prompt_content = ref_prompt_data.get('instruction', 
                                ref_prompt_data.get('main_prompt', 
                                str(ref_prompt_data)))
                
                prompts_section += f"\n--- REFERENCED PROMPT {i}: {prompt_name} ---\n"
                prompts_section += f"Purpose: {purpose}\n"
                prompts_section += f"Source: {prompt_path}\n\n"
                prompts_section += prompt_content + "\n"
                
                logging.debug(f"✓ Loaded referenced prompt {i}: {len(prompt_content)} characters")
                
            except Exception as e:
                logging.error(f"Failed to load referenced prompt {prompt_name}: {e}")
                prompts_section += f"\n--- REFERENCED PROMPT {i}: {prompt_name} (LOAD FAILED) ---\n"
                prompts_section += f"Error: {e}\n"
        
        prompts_section += "\n"
        return prompts_section


class MultiFilePromptRunner:
    """Main application class for multi-file prompt processing."""
    
    def __init__(self, output_file: str = None, config_file: str = None, 
                 log_file: str = None, temp_dir: str = None):
        """Initialize the multi-file prompt runner."""
        logging.info("Initializing Multi-File Prompt Runner")
        
        # Store temp directory
        self.temp_dir = temp_dir
        
        # Initialize configuration manager with optional config file
        self.config = ConfigManager(config_file)
        
        # Handle log file specification and auto-enable file logging (same as prompt_runner.py)
        if log_file:
            if temp_dir and not Path(log_file).is_absolute():
                temp_log_path = Path(temp_dir) / log_file
                self.config.config['log_file'] = str(temp_log_path)
                logging.info(f"Using temp directory for log file: {temp_log_path}")
            else:
                self.config.config['log_file'] = log_file
                logging.info(f"Command line log file specified: {log_file}")
            self.config.config['log_to_file'] = True
        elif 'log_file' in self.config.config and self.config.config['log_file']:
            config_log_file = self.config.config['log_file']
            if temp_dir and not Path(config_log_file).is_absolute():
                temp_log_path = Path(temp_dir) / config_log_file
                self.config.config['log_file'] = str(temp_log_path)
                logging.info(f"Using temp directory for config log file: {temp_log_path}")
            else:
                logging.info(f"Config file log file specified: {config_log_file}")
            self.config.config['log_to_file'] = True
        
        # Create unique payload file name with timestamp and process ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = os.getpid()
        unique_payload_name = f'multi_file_prompt_runner_{timestamp}_{process_id}.payload.json'
        
        # Set payload file location based on temp_dir
        default_payload_file = unique_payload_name
        if temp_dir:
            default_payload_file = str(Path(temp_dir) / unique_payload_name)
            logging.info(f"Using unique payload file in temp directory: {unique_payload_name}")
        else:
            logging.info(f"Using unique payload file: {unique_payload_name}")
        
        # Set configuration defaults (reuse existing patterns)
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
        
        # Initialize managers and components (reuse existing codebase)
        self.logging_manager = LoggingManager(self.config)
        self.api_client = PromptAPIClient(self.config)
        
        # Initialize multi-file specific components
        self.scanner = PromptScanner()
        self.prompt_loader = MultiFilePromptLoader()
        self.input_handler = InputFileHandler()
        self.processor = MultiFilePromptProcessor(self.input_handler)
        self.response_handler = ResponseHandler(output_file)
        
        logging.info("✓ Multi-File Prompt Runner initialized successfully")
    
    def run_batch_mode(self, prompt_file: Path, input_file: Path):
        """
        Run in batch mode with specified complex prompt and input files.
        
        Args:
            prompt_file: Path to complex JSON prompt file
            input_file: Path to main input file
        """
        logging.info("=" * 60)
        logging.info("MULTI-FILE PROMPT RUNNER - BATCH MODE")
        logging.info("=" * 60)
        
        try:
            # Step 1: Load complex prompt
            logging.info("Step 1: Loading complex prompt file")
            prompt_data = self.prompt_loader.load_complex_prompt(prompt_file)
            logging.info("✓ Complex prompt loaded successfully")
            
            # Log prompt summary
            self._log_prompt_summary(prompt_data)
            
            # Step 2: Load main input content
            logging.info("Step 2: Loading main input file")
            input_content = self.input_handler.load_file_content(input_file)
            logging.info(f"✓ Main input loaded: {len(input_content)} characters")
            
            # Step 3: Create complex prompt
            logging.info("Step 3: Processing complex prompt with attachments")
            full_prompt = self.processor.create_complex_prompt(prompt_data, input_content)
            logging.info("✓ Complex prompt processing completed")
            
            # Step 4: Call API
            logging.info("Step 4: Calling OpenRouter API")
            response = self.api_client.call_api(full_prompt)
            logging.info("✓ API call successful")
            
            # Step 5: Handle response
            logging.info("Step 5: Processing response")
            self.response_handler.stream_response(response, str(prompt_file), str(input_file))
            
            logging.info("=" * 60)
            logging.info("✓ BATCH MODE COMPLETED SUCCESSFULLY")
            logging.info("=" * 60)
            
        except Exception as e:
            logging.error(f"Batch mode execution failed: {e}")
            logging.debug("Full error details:", exc_info=True)
            raise
    
    def run_interactive_mode(self):
        """Run in interactive mode for complex prompt selection."""
        logging.info("=" * 60)
        logging.info("MULTI-FILE PROMPT RUNNER - INTERACTIVE MODE") 
        logging.info("=" * 60)
        
        try:
            while True:
                # Step 1: Scan for complex prompt files
                logging.info("Step 1: Scanning for complex prompt files")
                prompt_files = self.scanner.scan_prompts()
                
                if not prompt_files:
                    print("No JSON prompt files found in the current directory.")
                    break
                
                # Filter for complex prompts (this is just a demo - all JSON files are considered)
                print(f"\n📁 Found {len(prompt_files)} prompt file(s):")
                for i, prompt_file in enumerate(prompt_files, 1):
                    print(f"  {i}. {prompt_file}")
                
                # Step 2: Prompt selection
                print(f"\n📝 Select a complex prompt file (1-{len(prompt_files)}, or 'q' to quit): ", end="")
                choice = input().strip()
                
                if choice.lower() in ['q', 'quit']:
                    print("Goodbye!")
                    break
                
                try:
                    selected_index = int(choice) - 1
                    if 0 <= selected_index < len(prompt_files):
                        selected_prompt = prompt_files[selected_index]
                    else:
                        print(f"Invalid selection. Please choose 1-{len(prompt_files)}")
                        continue
                except ValueError:
                    print("Invalid input. Please enter a number or 'q'")
                    continue
                
                # Step 3: Input file selection
                print(f"\n📄 Enter the main input file path: ", end="")
                input_path = input().strip()
                
                if not input_path:
                    print("Input file path cannot be empty")
                    continue
                
                input_file = Path(input_path)
                if not input_file.exists():
                    print(f"Input file not found: {input_file}")
                    continue
                
                # Step 4: Execute with selected files
                try:
                    self.run_batch_mode(Path(selected_prompt), input_file)
                except Exception as e:
                    logging.error(f"Execution failed: {e}")
                    print(f"❌ Error: {e}")
                
                # Ask if user wants to continue
                print("\nWould you like to run another complex prompt? (y/n): ", end="")
                if input().strip().lower() not in ['y', 'yes']:
                    print("Goodbye!")
                    break
                    
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
        except Exception as e:
            logging.error(f"Unexpected error in interactive session: {e}")
            logging.debug("Full error details:", exc_info=True)
    
    def _log_prompt_summary(self, prompt_data: Dict[str, Any]):
        """Log a summary of the complex prompt configuration."""
        attached_count = len(prompt_data.get('attached_files', []))
        referenced_count = len(prompt_data.get('referenced_prompts', []))
        
        logging.info(f"Complex prompt summary:")
        logging.info(f"  - Main instruction: {len(prompt_data.get('instruction', ''))} characters")
        logging.info(f"  - Main prompt: {len(prompt_data.get('main_prompt', ''))} characters")
        logging.info(f"  - Attached files: {attached_count}")
        logging.info(f"  - Referenced prompts: {referenced_count}")
        
        if attached_count > 0:
            logging.info("  Attached files:")
            for i, file_config in enumerate(prompt_data['attached_files'], 1):
                logging.info(f"    {i}. {file_config['name']} ({file_config['path']})")
        
        if referenced_count > 0:
            logging.info("  Referenced prompts:")
            for i, prompt_config in enumerate(prompt_data['referenced_prompts'], 1):
                logging.info(f"    {i}. {prompt_config['name']} ({prompt_config['path']})")


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
        raise argparse.ArgumentTypeError(f"{file_type} path exists but is not a file: {path}")
    
    return path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run complex JSON prompts with multiple file attachments using OpenRouter API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Mode Selection:
    Interactive Mode (default): Scan directory and select complex prompts interactively
    Batch Mode: Process specific complex prompt with main input file

Interactive Mode Examples:
    python multi_file_prompt_runner.py
    python multi_file_prompt_runner.py -o responses.md
    python multi_file_prompt_runner.py -c my_config.yaml -o responses.md
    python multi_file_prompt_runner.py -l debug.log -v -o responses.md

Batch Mode Examples:
    python multi_file_prompt_runner.py -p complex_analysis.json -i document.md
    python multi_file_prompt_runner.py -p multi_step_prompt.json -i input.txt -o results.md
    python multi_file_prompt_runner.py -p complex_prompt.json -i data.md -o analysis.md -c config.yaml
    python multi_file_prompt_runner.py -p prompt.json -i input.md -l batch.log -o results.md

Complex Prompt JSON Format:
    {
        "instruction": "Main instruction for the AI",
        "main_prompt": "Primary prompt content",
        "attached_files": [
            {
                "name": "Reference Document",
                "path": "reference.md",
                "description": "Supporting context document"
            }
        ],
        "referenced_prompts": [
            {
                "name": "Style Guide",
                "path": "style_prompt.json", 
                "purpose": "Defines writing style requirements"
            }
        ],
        "final_instructions": "Final processing instructions"
    }

File Attachment Limits:
    - Maximum 10 attached files per prompt
    - Files can be any text format (markdown, txt, json, etc.)
    - Referenced prompts are loaded and embedded into the main prompt

Requirements:
    - OPENROUTER_API_KEY environment variable must be set
    - All attached files and referenced prompts must exist
    - Complex prompt JSON must follow the required schema
        """
    )
    
    # Mode selection arguments
    mode_group = parser.add_argument_group('Mode Selection')
    mode_group.add_argument(
        '-p', '--prompt',
        type=lambda x: validate_file_path(x, "Complex prompt"),
        help='Complex JSON prompt file (enables batch mode)',
        metavar='PROMPT_FILE'
    )
    mode_group.add_argument(
        '-i', '--input',
        type=lambda x: validate_file_path(x, "Main input"),
        help='Main input file to process (requires --prompt for batch mode)',
        metavar='INPUT_FILE'
    )
    
    # Configuration options
    config_group = parser.add_argument_group('Configuration Options')
    config_group.add_argument(
        '-c', '--config',
        help='Configuration file (YAML format)',
        metavar='CONFIG_FILE'
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
        help='Temporary directory for logs and payload files',
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
        # Initialize runner with all parameters
        runner = MultiFilePromptRunner(args.output_file, args.config, args.log_file, args.temp_dir)
        
        # Adjust logging level if requested
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.info("Debug logging enabled")
        elif args.quiet:
            logging.getLogger().setLevel(logging.ERROR)
        
        # Execute in appropriate mode
        if batch_mode:
            logging.info(f"Running in batch mode: {args.prompt} -> {args.input}")
            runner.run_batch_mode(args.prompt, args.input)
        else:
            logging.info("Running in interactive mode")
            runner.run_interactive_mode()
            
        logging.info("✓ Multi-file prompt runner completed successfully")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logging.error(f"Application error: {e}")
        if args.verbose:
            logging.debug("Full error details:", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    import json  # Add this import at the top level
    exit(main())