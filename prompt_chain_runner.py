#!/usr/bin/env python3
"""
OpenRouter Prompt Chain Runner

A wrapper for prompt_runner.py that automates running multiple prompts in sequence.
Supports 1-99 prompts configured via YAML file with intermediate file management.

Usage:
    python prompt_chain_runner.py -c config.yaml [-i input_file] [-o output_file]
"""

import argparse
import logging
import os
import subprocess
import sys
import tempfile
import uuid
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class PromptChainRunner:
    """Manages sequential execution of multiple prompts."""
    
    def __init__(self, config_file: str, input_file: str = None, output_file: str = None, debug: bool = False):
        """
        Initialize the prompt chain runner.
        
        Args:
            config_file: Path to YAML configuration file
            input_file: Override input file from command line
            output_file: Override output file from command line
            debug: Enable debug logging
        """
        self.config_file = Path(config_file)
        self.input_file_override = input_file
        self.output_file_override = output_file
        self.debug = debug
        
        # Track execution state - Initialize before config loading
        self.prompts_executed = 0
        self.total_prompts = 0  # Will be set in _validate_config()
        
        # Create unique identifiers for this run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.execution_id = str(uuid.uuid4())[:8]
        
        # Create unique log file
        self.log_file = self._create_log_file()
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config()
        
        # Create temp directory for intermediate files
        self.temp_dir = self._create_temp_dir()
        
        logging.info(f"Prompt Chain Runner initialized - Execution ID: {self.execution_id}")
        logging.info(f"Configuration file: {self.config_file}")
        logging.info(f"Temp directory: {self.temp_dir}")
        logging.info(f"Total prompts loaded: {self.total_prompts}")
        if hasattr(self, 'config'):
            logging.info(f"Config prompts keys: {list(self.config.get('prompts', {}).keys())}")
        else:
            logging.warning("Config not yet loaded during initialization")
    
    def _create_log_file(self) -> Path:
        """Create a unique log file name using timestamp and execution ID."""
        log_filename = f"prompt_chain_{self.timestamp}_{self.execution_id}.log"
        return Path.cwd() / log_filename
    
    def _setup_logging(self):
        """Setup logging to the unique log file."""
        # Remove any existing handlers to avoid duplicates
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configure logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG if self.debug else logging.INFO)
        
        # Configure root logger
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)
        
        logging.info(f"Logging initialized - Log file: {self.log_file}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        logging.info(f"Loading configuration from: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate configuration structure
            self._validate_config(config)
            
            logging.info(f"Configuration loaded successfully")
            logging.debug(f"Configuration: {config}")
            
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration structure and prompt file existence."""
        logging.debug("Starting configuration validation")
        
        required_fields = ['input_file', 'output_file', 'prompts']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in configuration: {field}")
        
        logging.debug(f"Required fields validated: {required_fields}")
        
        # Validate prompts section
        prompts = config['prompts']
        logging.debug(f"Found prompts section: {prompts}")
        
        if not isinstance(prompts, dict):
            raise ValueError("'prompts' must be a dictionary")
        
        if not prompts:
            raise ValueError("At least one prompt must be specified")
        
        logging.debug(f"Prompts is dictionary with {len(prompts)} entries")
        
        # Validate prompt numbering (1-99)
        valid_numbers = set(range(1, 100))
        prompt_numbers = set()
        
        for key in prompts.keys():
            logging.debug(f"Validating prompt key: {key}")
            if not key.startswith('prompt '):
                raise ValueError(f"Invalid prompt key format: {key}. Expected 'prompt N' where N is 1-99")
            
            try:
                number = int(key.split()[1])
                logging.debug(f"Extracted number {number} from key {key}")
                if number not in valid_numbers:
                    raise ValueError(f"Prompt number must be 1-99, got: {number}")
                prompt_numbers.add(number)
            except (IndexError, ValueError) as e:
                raise ValueError(f"Invalid prompt key format: {key}. Expected 'prompt N' where N is 1-99")
        
        logging.debug(f"Prompt numbers found: {sorted(prompt_numbers)}")
        
        # Check for sequential numbering starting from 1
        sorted_numbers = sorted(prompt_numbers)
        expected_numbers = list(range(1, len(sorted_numbers) + 1))
        
        logging.debug(f"Expected numbers: {expected_numbers}")
        logging.debug(f"Found numbers: {sorted_numbers}")
        
        if sorted_numbers != expected_numbers:
            raise ValueError(f"Prompts must be numbered sequentially starting from 1. Found: {sorted_numbers}")
        
        # Validate ALL prompt files exist before any execution
        missing_prompts = []
        for prompt_key, prompt_file in prompts.items():
            logging.debug(f"Checking existence of {prompt_key}: {prompt_file}")
            prompt_path = Path(prompt_file)
            if not prompt_path.exists():
                missing_prompts.append(f"{prompt_key}: {prompt_file}")
                logging.debug(f"Missing: {prompt_file}")
            elif not prompt_path.is_file():
                missing_prompts.append(f"{prompt_key}: {prompt_file} (exists but is not a file)")
                logging.debug(f"Not a file: {prompt_file}")
            else:
                logging.debug(f"Verified: {prompt_file}")
        
        if missing_prompts:
            error_msg = "Missing or invalid prompt files:\n"
            for missing in missing_prompts:
                error_msg += f"  - {missing}\n"
            error_msg += "\nAll prompt files must exist before execution can begin."
            raise FileNotFoundError(error_msg)
        
        # FIX: Set total_prompts AFTER validation passes
        self.total_prompts = len(prompts)
        logging.info(f"Configuration validation passed - {self.total_prompts} prompts found")
        logging.info("All prompt files verified to exist")
        logging.debug(f"Prompts: {list(prompts.keys())}")
        logging.debug(f"self.total_prompts set to: {self.total_prompts}")
    
    def _create_temp_dir(self) -> Path:
        """Create temporary directory for intermediate files using unique naming."""
        temp_base = Path.cwd() / "temp"
        temp_base.mkdir(exist_ok=True)
        
        # Create unique subdirectory using same naming convention as log file
        temp_subdir = temp_base / f"prompt_chain_{self.timestamp}_{self.execution_id}"
        temp_subdir.mkdir(exist_ok=True)
        
        return temp_subdir
    
    def _validate_input_file(self) -> Path:
        """Validate that the input file exists before starting execution."""
        input_file = self._get_input_file()
        
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if not input_file.is_file():
            raise ValueError(f"Input path exists but is not a file: {input_file}")
        
        # Check if file is readable
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                f.read(1)  # Try to read at least one character
        except UnicodeDecodeError:
            logging.warning(f"Input file may not be UTF-8 encoded: {input_file}")
        except PermissionError:
            raise PermissionError(f"No permission to read input file: {input_file}")
        except Exception as e:
            raise RuntimeError(f"Cannot read input file {input_file}: {e}")
        
        return input_file
    
    def _get_input_file(self) -> Path:
        """Get the input file path (command line override or config)."""
        if self.input_file_override:
            input_file = Path(self.input_file_override)
            logging.info(f"Using command line input file: {input_file}")
        else:
            input_file = Path(self.config['input_file'])
            logging.info(f"Using config input file: {input_file}")
        
        return input_file.resolve()
    
    def _get_output_file(self) -> Path:
        """Get the output file (command line override or config)."""
        if self.output_file_override:
            output_file = Path(self.output_file_override)
            logging.info(f"Using command line output file: {output_file}")
        else:
            output_file = Path(self.config['output_file'])
            logging.info(f"Using config output file: {output_file}")
        
        # Create parent directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        return output_file.resolve()
    
    def _get_temp_file(self, step: int, prompt_name: str = None) -> Path:
        """
        Generate temporary file path for intermediate steps with unique naming.
        
        Args:
            step: Current step number
            prompt_name: Optional prompt name for more descriptive naming
            
        Returns:
            Path object for temporary file
        """
        # Extract prompt name from file if provided
        if prompt_name:
            # Remove .json extension and clean up the name
            clean_name = Path(prompt_name).stem
            # Replace spaces and special characters with underscores
            clean_name = "".join(c if c.isalnum() else "_" for c in clean_name)
            temp_filename = f"step{step:02d}_{clean_name}_{self.timestamp}_{self.execution_id}.tmp"
        else:
            temp_filename = f"step{step:02d}_{self.timestamp}_{self.execution_id}.tmp"
        
        temp_file = self.temp_dir / temp_filename
        return temp_file.resolve()
    
    def _run_prompt_runner(self, prompt_file: str, input_file: Path, output_file: Path, step: int) -> bool:
        """
        Run prompt_runner.py with specified parameters.
        
        Args:
            prompt_file: Path to JSON prompt file
            input_file: Input file for this step
            output_file: Output file for this step
            step: Current step number for logging
            
        Returns:
            True if successful, False otherwise
        """
        # Build command
        cmd = [
            sys.executable,  # Use same Python interpreter
            "prompt_runner.py",
            "-p", prompt_file,
            "-i", str(input_file),
            "-o", str(output_file),
            "-l", str(self.log_file)  # Use same log file
        ]
        
        logging.info(f"Step {step}: Executing prompt_runner.py")
        logging.info(f"Full command: {' '.join(cmd)}")
        logging.info(f"Prompt file: {prompt_file}")
        logging.info(f"Input file: {input_file}")
        logging.info(f"Output file: {output_file}")
        
        try:
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Log the results
            if result.returncode == 0:
                logging.info(f"Step {step}: SUCCESS - prompt_runner.py completed")
                if result.stdout:
                    logging.debug(f"Step {step} stdout: {result.stdout}")
                return True
            else:
                logging.error(f"Step {step}: FAILED - prompt_runner.py returned code {result.returncode}")
                if result.stderr:
                    logging.error(f"Step {step} stderr: {result.stderr}")
                if result.stdout:
                    logging.error(f"Step {step} stdout: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error(f"Step {step}: TIMEOUT - prompt_runner.py timed out after 5 minutes")
            return False
        except Exception as e:
            logging.error(f"Step {step}: ERROR - Failed to execute prompt_runner.py: {e}")
            return False
    
    def _verify_output_file(self, file_path: Path, step: int) -> bool:
        """Verify that output file was created and has content."""
        if not file_path.exists():
            logging.error(f"Step {step}: Output file not created: {file_path}")
            return False
        
        file_size = file_path.stat().st_size
        if file_size == 0:
            logging.error(f"Step {step}: Output file is empty: {file_path}")
            return False
        
        logging.info(f"Step {step}: Output file verified - {file_size} bytes: {file_path}")
        return True
    
    def run_chain(self) -> bool:
        """
        Execute the prompt chain.
        
        Returns:
            True if all steps completed successfully, False otherwise
        """
        logging.info("=" * 80)
        logging.info(f"Starting prompt chain execution - {self.total_prompts} prompts")
        logging.info("=" * 80)
        
        try:
            # Validate all files exist before starting execution
            initial_input = self._validate_input_file()
            final_output = self._get_output_file()
            
            logging.info(f"Pre-execution validation completed successfully")
            logging.info(f"Initial input: {initial_input}")
            logging.info(f"Final output: {final_output}")
            
            # Get sorted prompt list
            prompts = self.config['prompts']
            logging.info(f"Processing {len(prompts)} prompts from config")
            logging.debug(f"Available prompts: {list(prompts.keys())}")
            logging.debug(f"Total prompts from validation: {self.total_prompts}")
            
            # FIX: Check if we have prompts to execute
            if self.total_prompts == 0:
                logging.error("No prompts found to execute!")
                logging.error(f"Config prompts section: {prompts}")
                return False
            
            sorted_prompts = []
            for i in range(1, self.total_prompts + 1):
                prompt_key = f"prompt {i}"
                logging.debug(f"Looking for {prompt_key} in prompts")
                if prompt_key in prompts:
                    sorted_prompts.append((i, prompts[prompt_key]))
                    logging.debug(f"Added {prompt_key}: {prompts[prompt_key]}")
                else:
                    logging.error(f"Missing {prompt_key} in prompts configuration")
                    logging.error(f"Available keys: {list(prompts.keys())}")
            
            logging.info(f"Sorted prompts list has {len(sorted_prompts)} entries")
            
            if not sorted_prompts:
                logging.error("No prompts to execute - this should not happen after validation")
                return False
            
            # Execute prompts in sequence
            current_input = initial_input
            
            for step, prompt_file in sorted_prompts:
                logging.info(f"\n--- Step {step}/{self.total_prompts} ---")
                logging.info(f"Executing prompt: {prompt_file}")
                
                # Determine output file for this step
                if step == self.total_prompts:
                    # Last step - use final output file
                    current_output = final_output
                    logging.info(f"Final step - output to: {current_output}")
                else:
                    # Intermediate step - use temp file with descriptive naming
                    current_output = self._get_temp_file(step, prompt_file)
                    logging.info(f"Intermediate step - temp output: {current_output.name}")
                
                # Run prompt_runner.py
                success = self._run_prompt_runner(prompt_file, current_input, current_output, step)
                
                if not success:
                    logging.error(f"Chain execution failed at step {step}")
                    return False
                
                # Verify output file
                if not self._verify_output_file(current_output, step):
                    logging.error(f"Output verification failed at step {step}")
                    return False
                
                # Log temp file details for tracking
                if step < self.total_prompts:
                    logging.info(f"Step {step} temp file created: {current_output}")
                    logging.info(f"Temp file size: {current_output.stat().st_size} bytes")
                
                # Update input for next iteration
                current_input = current_output
                self.prompts_executed += 1
                
                logging.info(f"Step {step} completed successfully")
            
            logging.info("=" * 80)
            logging.info(f"Prompt chain execution completed successfully!")
            logging.info(f"Final output: {final_output}")
            logging.info(f"Temporary files preserved in: {self.temp_dir}")
            logging.info(f"Log file: {self.log_file}")
            logging.info("=" * 80)
            
            return True
            
        except Exception as e:
            logging.error(f"Prompt chain execution failed: {e}")
            logging.debug("Full traceback:", exc_info=True)
            return False
    
    def cleanup(self, keep_temp: bool = True):
        """
        Cleanup temporary files and directories.
        
        Args:
            keep_temp: If True, keep temporary files (default: True)
        """
        if keep_temp:
            logging.info(f"Preserving temporary files in: {self.temp_dir}")
            temp_files = list(self.temp_dir.glob("*.tmp"))
            if temp_files:
                logging.info("Temporary files created:")
                for temp_file in temp_files:
                    file_size = temp_file.stat().st_size
                    logging.info(f"  - {temp_file.name} ({file_size} bytes)")
            return
        
        try:
            # Remove temporary files
            temp_files = list(self.temp_dir.glob("*.tmp"))
            for temp_file in temp_files:
                temp_file.unlink()
                logging.debug(f"Removed temp file: {temp_file}")
            
            logging.info(f"Cleaned up {len(temp_files)} temporary files")
            
            # Remove temp directory if empty
            if not any(self.temp_dir.iterdir()):
                self.temp_dir.rmdir()
                logging.debug(f"Removed temp directory: {self.temp_dir}")
            else:
                logging.info(f"Temp directory not empty, keeping: {self.temp_dir}")
                
        except Exception as e:
            logging.warning(f"Cleanup failed: {e}")


def create_sample_config():
    """Create a sample configuration file."""
    sample_config = {
        'input_file': 'input_document.md',
        'output_file': 'final_output.md',
        'prompts': {
            'prompt 1': 'step1_analysis.json',
            'prompt 2': 'step2_refinement.json',
            'prompt 3': 'step3_finalization.json'
        }
    }
    
    sample_path = Path('prompt_chain_config_sample.yaml')
    with open(sample_path, 'w', encoding='utf-8') as f:
        yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Sample configuration created: {sample_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OpenRouter Prompt Chain Runner - Execute multiple prompts in sequence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage with config file
    python prompt_chain_runner.py -c my_chain.yaml
    
    # Enable debug logging
    python prompt_chain_runner.py -c my_chain.yaml --debug
    
    # Override input and output files
    python prompt_chain_runner.py -c my_chain.yaml -i input.md -o output.md
    
    # Keep temporary files for debugging (default behavior)
    python prompt_chain_runner.py -c my_chain.yaml
    
    # Clean up temporary files after execution
    python prompt_chain_runner.py -c my_chain.yaml --clean-temp
    
    # Create sample configuration
    python prompt_chain_runner.py --create-sample

Configuration File Format (YAML):
    input_file: input_document.md
    output_file: final_output.md
    prompts:
        prompt 1: step1_analysis.json
        prompt 2: step2_refinement.json
        prompt 3: step3_finalization.json

Execution Flow:
    1. input_document.md -> step1_analysis.json -> temp/step01_analysis_20250126_154530_a1b2c3d4.tmp
    2. temp/step01_analysis_20250126_154530_a1b2c3d4.tmp -> step2_refinement.json -> temp/step02_refinement_20250126_154530_a1b2c3d4.tmp
    3. temp/step02_refinement_20250126_154530_a1b2c3d4.tmp -> step3_finalization.json -> final_output.md

File Naming Convention:
    Log file: prompt_chain_20250126_154530_a1b2c3d4.log
    Temp dir: temp/prompt_chain_20250126_154530_a1b2c3d4/
    Temp files: step01_promptname_20250126_154530_a1b2c3d4.tmp

Requirements:
    - prompt_runner.py must be in PATH or current directory
    - All prompt JSON files must exist
    - Input file must exist
    - OpenRouter API key must be set (OPENROUTER_API_KEY)
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        required=False,
        help='YAML configuration file path',
        metavar='CONFIG_FILE'
    )
    
    parser.add_argument(
        '-i', '--input',
        help='Input file (overrides config file)',
        metavar='INPUT_FILE'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file (overrides config file)',
        metavar='OUTPUT_FILE'
    )
    
    parser.add_argument(
        '--clean-temp',
        action='store_true',
        help='Clean up temporary files after execution (default: keep files)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging output to console'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create a sample configuration file and exit'
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.create_sample:
        create_sample_config()
        return 0
    
    if not args.config:
        parser.error("Configuration file is required (use -c/--config or --create-sample)")
    
    try:
        # Initialize runner
        runner = PromptChainRunner(args.config, args.input, args.output, args.debug)
        
        # Execute chain
        success = runner.run_chain()
        
        # Cleanup (temp files preserved by default)
        runner.cleanup(keep_temp=not args.clean_temp)
        
        # Exit with appropriate code
        if success:
            print(f"\n✅ Prompt chain completed successfully!")
            print(f"Final output: {runner._get_output_file()}")
            print(f"Temporary files: {runner.temp_dir}")
            print(f"Log file: {runner.log_file}")
            return 0
        else:
            print(f"\n❌ Prompt chain failed!")
            print(f"Check log file: {runner.log_file}")
            return 1
            
    except FileNotFoundError as e:
        print(f"File Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())