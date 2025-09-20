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
import shutil
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
    
    def __init__(self, config_file: str, input_file: str = None, output_file: str = None, 
                 prompt_runner_config: str = None, debug: bool = False):
        """
        Initialize the prompt chain runner.
        
        Args:
            config_file: Path to YAML configuration file for the chain
            input_file: Override input file from command line
            output_file: Override output file from command line
            prompt_runner_config: Configuration file to pass to prompt_runner.py
            debug: Enable debug logging
        """
        self.config_file = Path(config_file)
        self.input_file_override = input_file
        self.output_file_override = output_file
        self.prompt_runner_config = prompt_runner_config
        self.debug = debug
        
        # Track execution state - Initialize before config loading
        self.prompts_executed = 0
        self.total_prompts = 0  # Will be set in _validate_config()
        
        # Create unique identifiers for this run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.process_id = os.getpid()
        
        # Load configuration first to determine input file
        self.config = self._load_config()
        
        # Create temp directory (requires input file to be known)
        self.temp_dir = self._create_temp_dir()
        
        # Create log file in temp directory
        self.log_file = self._create_log_file()
        self._setup_logging()
        
        logging.info(f"Prompt Chain Runner initialized - Process ID: {self.process_id}")
        logging.info(f"Configuration file: {self.config_file}")
        logging.info(f"Temp directory: {self.temp_dir}")
        logging.info(f"Log file: {self.log_file}")
        logging.info(f"Total prompts loaded: {self.total_prompts}")
        if hasattr(self, 'config'):
            logging.info(f"Config prompts keys: {list(self.config.get('prompts', {}).keys())}")
        else:
            logging.warning("Config not yet loaded during initialization")
    
    def _create_temp_dir(self) -> Path:
        """Create temporary directory using new naming convention: <input_filename>_<date>_<pid>"""
        # Get input file name (without extension) - use first file for multi-file mode
        if 'input_files' in self.config:
            input_file = Path(self.config['input_files'][0])
            input_basename = f"multi_{len(self.config['input_files'])}_files"
        else:
            input_file = self._get_input_file()
            input_basename = input_file.stem  # filename without extension
        
        # Create temp directory name: inputname_date_pid
        temp_dirname = f"{input_basename}_{self.timestamp}_{self.process_id}"
        
        temp_base = Path.cwd() / "temp"
        temp_base.mkdir(exist_ok=True)
        
        temp_subdir = temp_base / temp_dirname
        temp_subdir.mkdir(exist_ok=True)
        
        return temp_subdir
    
    def _create_log_file(self) -> Path:
        """Create log file in temp directory using same naming convention."""
        # Get input file name (without extension) - use first file for multi-file mode
        if 'input_files' in self.config:
            input_file = Path(self.config['input_files'][0])
            input_basename = f"multi_{len(self.config['input_files'])}_files"
        else:
            input_file = self._get_input_file()
            input_basename = input_file.stem
        
        # Create log filename using same convention as directory
        log_filename = f"{input_basename}_{self.timestamp}_{self.process_id}.log"
        return self.temp_dir / log_filename
    
    def _setup_logging(self):
        """Setup logging to the log file in temp directory."""
        # Remove any existing handlers to avoid duplicates
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configure logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler (now in temp directory)
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
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate configuration structure
            self._validate_config(config)
            
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration structure and prompt file existence."""
        # Support both single file and multiple files
        if 'input_file' not in config and 'input_files' not in config:
            raise ValueError("Either 'input_file' or 'input_files' must be specified")
        
        if 'input_file' in config and 'input_files' in config:
            raise ValueError("Cannot specify both 'input_file' and 'input_files'")
        
        # Validate output configuration
        if 'output_file' not in config and 'output_pattern' not in config:
            raise ValueError("Either 'output_file' or 'output_pattern' must be specified")
        
        if 'prompts' not in config:
            raise ValueError("Missing required field 'prompts' in configuration")
        
        # Validate input files
        if 'input_files' in config:
            self._validate_input_files(config['input_files'])
        elif 'input_file' in config:
            # Single input file
            input_file = Path(config['input_file'])
            if not input_file.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
        # Note: input_file might be provided via command line override, so don't error here
        
        # Validate prompts section  
        prompts = config['prompts']
        
        if not isinstance(prompts, dict):
            raise ValueError("'prompts' must be a dictionary")
        
        if not prompts:
            raise ValueError("At least one prompt must be specified")
        
        # Validate prompt numbering (1-99)
        valid_numbers = set(range(1, 100))
        prompt_numbers = set()
        
        for key, prompt_config in prompts.items():
            if not key.startswith('prompt '):
                raise ValueError(f"Invalid prompt key format: {key}. Expected 'prompt N' where N is 1-99")
            
            try:
                number = int(key.split()[1])
                if number not in valid_numbers:
                    raise ValueError(f"Prompt number must be 1-99, got: {number}")
                prompt_numbers.add(number)
            except (IndexError, ValueError) as e:
                raise ValueError(f"Invalid prompt key format: {key}. Expected 'prompt N' where N is 1-99")
            
            # Validate prompt configuration (can be string or dict)
            self._validate_prompt_config(prompt_config, key)
        
        # Check for sequential numbering starting from 1
        sorted_numbers = sorted(prompt_numbers)
        expected_numbers = list(range(1, len(sorted_numbers) + 1))
        
        if sorted_numbers != expected_numbers:
            raise ValueError(f"Prompts must be numbered sequentially starting from 1. Found: {sorted_numbers}")
        
        # Validate ALL prompt files exist before any execution
        missing_prompts = []
        for prompt_key, prompt_config in prompts.items():
            # Extract prompt file path (handle both string and dict formats)
            prompt_file = self._get_prompt_file(prompt_config)
            prompt_path = Path(prompt_file)
            if not prompt_path.exists():
                missing_prompts.append(f"{prompt_key}: {prompt_file}")
            elif not prompt_path.is_file():
                missing_prompts.append(f"{prompt_key}: {prompt_file} (exists but is not a file)")
                
            # Validate config file if specified
            config_file = self._get_prompt_config_file(prompt_config)
            if config_file:
                config_path = Path(config_file)
                if not config_path.exists():
                    missing_prompts.append(f"{prompt_key} config: {config_file}")
                elif not config_path.is_file():
                    missing_prompts.append(f"{prompt_key} config: {config_file} (exists but is not a file)")
        
        if missing_prompts:
            error_msg = "Missing or invalid prompt files and configs:\n"
            for missing in missing_prompts:
                error_msg += f"  - {missing}\n"
            error_msg += "\nAll prompt files and config files must exist before execution can begin."
            raise FileNotFoundError(error_msg)
        
        # Set total_prompts AFTER validation passes
        self.total_prompts = len(prompts)
    
    def _validate_input_files(self, input_files: List[str]):
        """Validate multiple input files configuration."""
        if not isinstance(input_files, list):
            raise ValueError("'input_files' must be a list")
        
        if not input_files:
            raise ValueError("'input_files' cannot be empty")
        
        for i, file_path in enumerate(input_files):
            input_file = Path(file_path)
            if not input_file.exists():
                raise FileNotFoundError(f"Input file {i+1} not found: {input_file}")
            if not input_file.is_file():
                raise ValueError(f"Input file {i+1} exists but is not a file: {input_file}")
    
    def _validate_prompt_config(self, prompt_config, prompt_key: str):
        """Validate individual prompt configuration (string or dict)."""
        if isinstance(prompt_config, str):
            # Simple format: just the prompt file path
            return
        elif isinstance(prompt_config, dict):
            # Extended format with prompt file and optional config
            if 'prompt_file' not in prompt_config:
                raise ValueError(f"'{prompt_key}' dict format must include 'prompt_file'")
            
            # Config file is optional
            if 'config_file' in prompt_config:
                logging.debug(f"Prompt {prompt_key} has custom config: {prompt_config['config_file']}")
        else:
            raise ValueError(f"'{prompt_key}' must be a string or dict, got {type(prompt_config)}")
    
    def _get_prompt_file(self, prompt_config) -> str:
        """Extract prompt file path from config (handles both string and dict formats)."""
        if isinstance(prompt_config, str):
            return prompt_config
        elif isinstance(prompt_config, dict):
            return prompt_config['prompt_file']
        else:
            raise ValueError(f"Invalid prompt config type: {type(prompt_config)}")
    
    def _get_prompt_config_file(self, prompt_config) -> Optional[str]:
        """Extract config file path from prompt config (returns None if not specified)."""
        if isinstance(prompt_config, dict):
            return prompt_config.get('config_file')
        return None
    
    def _get_prompt_model(self, prompt_config) -> Optional[str]:
        """Extract model from prompt config (returns None if not specified)."""
        if isinstance(prompt_config, dict):
            return prompt_config.get('model')
        return None
    
    def _create_step_config_file(self, step: int, step_model: str = None) -> Optional[str]:
        """
        Create a temporary config file for this step with the specified model.
        
        Args:
            step: Step number for filename uniqueness
            step_model: Model to use for this step (if None, no config file is created)
            
        Returns:
            Path to temporary config file, or None if no step-specific config needed
        """
        if not step_model and not self.prompt_runner_config:
            return None
            
        # Create a temporary config file in the temp directory
        step_config_path = self.temp_dir / f"step_{step:02d}_config.yaml"
        
        # Base configuration
        step_config = {}
        
        # Load from global config if provided
        if self.prompt_runner_config and Path(self.prompt_runner_config).exists():
            with open(self.prompt_runner_config, 'r', encoding='utf-8') as f:
                step_config = yaml.safe_load(f) or {}
        
        # Load from global_config section if it exists
        if 'global_config' in self.config:
            global_config = self.config['global_config']
            step_config.update(global_config)
        
        # Override with step-specific model if provided
        if step_model:
            step_config['model'] = step_model
            logging.info(f"Step {step}: Using step-specific model: {step_model}")
        
        # Write the temporary config file
        with open(step_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(step_config, f, default_flow_style=False, sort_keys=False)
        
        logging.debug(f"Step {step}: Created temporary config file: {step_config_path}")
        return str(step_config_path)
    
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
        """Get the input file path (command line override or config) - for single file mode."""
        if self.input_file_override:
            input_file = Path(self.input_file_override)
            logging.info(f"Using command line input file: {input_file}")
        else:
            if 'input_file' not in self.config:
                raise ValueError("input_file not in config and no command line override provided")
            input_file = Path(self.config['input_file'])
            logging.info(f"Using config input file: {input_file}")
        
        return input_file.resolve()
    
    def _get_input_files(self) -> List[Path]:
        """Get the input files list for multiple file processing."""
        if 'input_files' in self.config:
            input_files = [Path(f).resolve() for f in self.config['input_files']]
            logging.info(f"Using config input files: {len(input_files)} files")
            return input_files
        elif 'input_file' in self.config or self.input_file_override:
            # Single file mode - return as list
            return [self._get_input_file()]
        else:
            raise ValueError("No input files specified")
    
    def _is_multiple_file_mode(self) -> bool:
        """Check if we're in multiple file processing mode."""
        return 'input_files' in self.config
    
    def _get_output_file(self, input_file: Path = None) -> Path:
        """Get the output file (command line override or config)."""
        if self.output_file_override:
            output_file = Path(self.output_file_override)
            logging.info(f"Using command line output file: {output_file}")
        elif 'output_file' in self.config:
            output_file = Path(self.config['output_file'])
            logging.info(f"Using config output file: {output_file}")
        elif 'output_pattern' in self.config and input_file:
            # Generate output filename from pattern
            output_file = self._generate_output_filename(input_file, self.config['output_pattern'])
            logging.info(f"Generated output file: {output_file}")
        else:
            raise ValueError("No output file or pattern specified")
        
        # Create parent directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        return output_file.resolve()
    
    def _generate_output_filename(self, input_file: Path, pattern: str) -> Path:
        """Generate output filename using pattern substitution."""
        # Available substitutions:
        # {input_name} - input filename without extension
        # {input_ext} - input file extension
        # {timestamp} - current timestamp
        # {process_id} - process ID
        
        input_name = input_file.stem
        input_ext = input_file.suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = os.getpid()
        
        output_filename = pattern.format(
            input_name=input_name,
            input_ext=input_ext,
            timestamp=timestamp,
            process_id=process_id
        )
        
        return Path(output_filename)
    
    def _get_temp_file(self, step: int, prompt_name: str = None) -> Path:
        """
        Generate temporary file path for intermediate steps.
        
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
            temp_filename = f"step{step:02d}_{clean_name}.tmp"
        else:
            temp_filename = f"step{step:02d}.tmp"
        
        temp_file = self.temp_dir / temp_filename
        return temp_file.resolve()
    
    def _copy_input_to_temp(self, input_file: Path):
        """Copy the original input file to temp directory for reference."""
        input_copy = self.temp_dir / f"original_input_{input_file.name}"
        try:
            shutil.copy2(input_file, input_copy)
            logging.info(f"Original input file copied to temp directory: {input_copy.name}")
        except Exception as e:
            logging.warning(f"Failed to copy input file to temp directory: {e}")
    
    def _copy_output_to_temp(self, output_file: Path):
        """Copy the final output file to temp directory for reference."""
        output_copy = self.temp_dir / f"final_output_{output_file.name}"
        try:
            shutil.copy2(output_file, output_copy)
            logging.info(f"Final output file copied to temp directory: {output_copy.name}")
        except Exception as e:
            logging.warning(f"Failed to copy output file to temp directory: {e}")
    
    def _run_prompt_runner(self, prompt_config, input_file: Path, output_file: Path, step: int) -> bool:
        """
        Run prompt_runner.py with specified parameters.
        
        Args:
            prompt_config: Prompt configuration (string or dict with prompt_file, optional config_file, and optional model)
            input_file: Input file for this step
            output_file: Output file for this step
            step: Current step number for logging
            
        Returns:
            True if successful, False otherwise
        """
        # Extract file paths and model from config
        prompt_file = self._get_prompt_file(prompt_config)
        step_config_file = self._get_prompt_config_file(prompt_config)
        step_model = self._get_prompt_model(prompt_config)
        
        # Build command - use openrouter-runner entry point
        cmd = [
            "openrouter-runner",
            "-p", prompt_file,
            "-i", str(input_file),
            "-o", str(output_file),
            "-l", str(self.log_file)  # Use same log file
        ]
        
        # Create step-specific config file if needed (handles both step-specific model and global config)
        effective_config_file = None
        
        if step_config_file:
            # User specified a step-specific config file, use it
            effective_config_file = step_config_file
            logging.info(f"Step {step}: Using step-specific config file: {step_config_file}")
        elif step_model or self.prompt_runner_config or 'global_config' in self.config:
            # Create a temporary config file with step-specific model and/or global config
            effective_config_file = self._create_step_config_file(step, step_model)
            if effective_config_file:
                logging.info(f"Step {step}: Created temporary config file with model override")
        
        # Add config file if we have one
        if effective_config_file:
            cmd.extend(["-c", effective_config_file])
            if step_model:
                logging.info(f"Step {step}: Using model: {step_model}")
            else:
                logging.info(f"Step {step}: Using config file: {effective_config_file}")
        
        # Add temp directory to keep all files organized
        cmd.extend(["--temp-dir", str(self.temp_dir)])
        
        logging.info(f"Step {step}: Executing openrouter-runner")
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
                logging.info(f"Step {step}: SUCCESS - openrouter-runner completed")
                if result.stdout:
                    logging.debug(f"Step {step} stdout: {result.stdout}")
                return True
            else:
                logging.error(f"Step {step}: FAILED - openrouter-runner returned code {result.returncode}")
                if result.stderr:
                    logging.error(f"Step {step} stderr: {result.stderr}")
                if result.stdout:
                    logging.error(f"Step {step} stdout: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error(f"Step {step}: TIMEOUT - openrouter-runner timed out after 5 minutes")
            return False
        except FileNotFoundError:
            logging.error(f"Step {step}: ERROR - openrouter-runner not found in PATH")
            logging.error("Make sure openrouter-runner is installed and accessible in your system PATH")
            return False
        except Exception as e:
            logging.error(f"Step {step}: ERROR - Failed to execute openrouter-runner: {e}")
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
        Execute the prompt chain - supports both single file and multiple files.
        
        Returns:
            True if all steps completed successfully, False otherwise
        """
        logging.info("=" * 80)
        multiple_files = self._is_multiple_file_mode()
        if multiple_files:
            input_files = self._get_input_files()
            logging.info(f"Starting MULTI-FILE prompt chain execution - {len(input_files)} files, {self.total_prompts} prompts each")
        else:
            input_files = self._get_input_files()  # Returns single file as list
            logging.info(f"Starting prompt chain execution - {self.total_prompts} prompts")
        logging.info("=" * 80)
        
        try:
            # Get sorted prompt list
            prompts = self.config['prompts']
            logging.info(f"Processing {len(prompts)} prompts from config")
            
            # Check if we have prompts to execute
            if self.total_prompts == 0:
                logging.error("No prompts found to execute!")
                logging.error(f"Config prompts section: {prompts}")
                return False
            
            sorted_prompts = []
            for i in range(1, self.total_prompts + 1):
                prompt_key = f"prompt {i}"
                if prompt_key in prompts:
                    sorted_prompts.append((i, prompts[prompt_key]))
                else:
                    logging.error(f"Missing {prompt_key} in prompts configuration")
                    logging.error(f"Available keys: {list(prompts.keys())}")
            
            logging.info(f"Sorted prompts list has {len(sorted_prompts)} entries")
            
            if not sorted_prompts:
                logging.error("No prompts to execute - this should not happen after validation")
                return False
            
            # Process each input file through the entire prompt chain
            all_successful = True
            total_files_processed = 0
            
            for file_index, input_file in enumerate(input_files, 1):
                logging.info(f"\n{'='*60}")
                if multiple_files:
                    logging.info(f"PROCESSING FILE {file_index}/{len(input_files)}: {input_file.name}")
                else:
                    logging.info(f"PROCESSING FILE: {input_file.name}")
                logging.info(f"{'='*60}")
                
                # Copy original input file to temp directory
                self._copy_input_to_temp(input_file)
                
                # Get output file for this input
                final_output = self._get_output_file(input_file)
                logging.info(f"Final output for this file: {final_output}")
                
                # Execute prompts in sequence for this input file
                current_input = input_file
                file_successful = True
                
                for step, prompt_config in sorted_prompts:
                    prompt_file = self._get_prompt_file(prompt_config)
                    step_config = self._get_prompt_config_file(prompt_config)
                    
                    logging.info(f"\n--- File {file_index}, Step {step}/{self.total_prompts} ---")
                    logging.info(f"Executing prompt: {prompt_file}")
                    if step_config:
                        logging.info(f"Using step-specific config: {step_config}")
                    
                    # Determine output file for this step
                    if step == self.total_prompts:
                        # Last step - use final output file
                        current_output = final_output
                        logging.info(f"Final step - output to: {current_output}")
                    else:
                        # Intermediate step - use temp file with file-specific naming
                        temp_file_name = f"file{file_index:02d}_step{step:02d}_{Path(prompt_file).stem}.tmp"
                        current_output = self.temp_dir / temp_file_name
                        logging.info(f"Intermediate step - temp output: {current_output.name}")
                    
                    # Run prompt_runner.py
                    success = self._run_prompt_runner(prompt_config, current_input, current_output, step)
                    
                    if not success:
                        logging.error(f"Chain execution failed at File {file_index}, Step {step}")
                        file_successful = False
                        all_successful = False
                        break
                    
                    # Verify output file
                    if not self._verify_output_file(current_output, step):
                        logging.error(f"Output verification failed at File {file_index}, Step {step}")
                        file_successful = False
                        all_successful = False
                        break
                    
                    # Log temp file details for tracking
                    if step < self.total_prompts:
                        logging.info(f"Step {step} temp file created: {current_output}")
                        logging.info(f"Temp file size: {current_output.stat().st_size} bytes")
                    
                    # Update input for next iteration
                    current_input = current_output
                    self.prompts_executed += 1
                    
                    logging.info(f"File {file_index}, Step {step} completed successfully")
                
                if file_successful:
                    # Copy final output to temp directory for reference
                    self._copy_output_to_temp(final_output)
                    total_files_processed += 1
                    logging.info(f"✓ File {file_index} processing completed successfully")
                else:
                    logging.error(f"❌ File {file_index} processing failed")
            
            # Final summary
            logging.info("=" * 80)
            if all_successful:
                logging.info(f"✓ ALL FILES PROCESSED SUCCESSFULLY!")
                logging.info(f"Files processed: {total_files_processed}/{len(input_files)}")
                logging.info(f"Total prompt executions: {self.prompts_executed}")
            else:
                logging.error(f"❌ SOME FILES FAILED PROCESSING")
                logging.info(f"Files processed successfully: {total_files_processed}/{len(input_files)}")
                logging.info(f"Total prompt executions: {self.prompts_executed}")
            
            logging.info(f"Temporary files preserved in: {self.temp_dir}")
            logging.info(f"Log file: {self.log_file}")
            logging.info("=" * 80)
            
            return all_successful
            
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
            temp_files = list(self.temp_dir.glob("*"))
            if temp_files:
                logging.info("Files in temp directory:")
                for temp_file in temp_files:
                    if temp_file.is_file():
                        file_size = temp_file.stat().st_size
                        logging.info(f"  - {temp_file.name} ({file_size} bytes)")
                    else:
                        logging.info(f"  - {temp_file.name} (directory)")
            return
        
        try:
            # Remove temporary files
            temp_files = list(self.temp_dir.glob("*"))
            files_removed = 0
            for temp_file in temp_files:
                if temp_file.is_file():
                    temp_file.unlink()
                    files_removed += 1
                    logging.debug(f"Removed temp file: {temp_file}")
            
            logging.info(f"Cleaned up {files_removed} temporary files")
            
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
    
    # Pass config file to prompt_runner.py executions
    python prompt_chain_runner.py -c my_chain.yaml --prompt-runner-config openrouter_editor.yaml
    
    # Multi-file processing with output pattern
    python prompt_chain_runner.py -c multi_file_config.yaml
    
    # Multi-LLM chain with different configs per step  
    python prompt_chain_runner.py -c multi_llm_config.yaml
    
    # Keep temporary files for debugging (default behavior)
    python prompt_chain_runner.py -c my_chain.yaml
    
    # Clean up temporary files after execution
    python prompt_chain_runner.py -c my_chain.yaml --clean-temp
    
    # Create sample configuration
    python prompt_chain_runner.py --create-sample

Configuration File Formats (YAML):

Single File Processing:
    input_file: input_document.md
    output_file: final_output.md
    prompts:
        prompt 1: step1_analysis.json
        prompt 2: step2_refinement.json
        prompt 3: step3_finalization.json

Multiple Files Processing:
    input_files:
        - document1.md
        - document2.md  
        - document3.txt
    output_pattern: "processed_{input_name}_output{input_ext}"
    prompts:
        prompt 1: analysis.json
        prompt 2: refinement.json
        prompt 3: polish.json

Per-Prompt Configuration (Different LLMs):
    input_file: input_document.md
    output_file: final_output.md
    prompts:
        prompt 1:
            prompt_file: creative_task.json
            config_file: claude_config.yaml
        prompt 2:
            prompt_file: technical_task.json
            config_file: gpt4_config.yaml
        prompt 3: final_edit.json  # Uses global config

Execution Flow Examples:

Single File:
    1. input_document.md -> analysis.json -> temp/input_document_20250131_12345/step01_analysis.tmp
    2. temp/.../step01_analysis.tmp -> refinement.json -> temp/.../step02_refinement.tmp  
    3. temp/.../step02_refinement.tmp -> polish.json -> final_output.md

Multiple Files:
    For each file (document1.md, document2.md, document3.txt):
    1. documentN.md -> analysis.json -> temp/.../file01_step01_analysis.tmp
    2. temp/.../file01_step01_analysis.tmp -> refinement.json -> temp/.../file01_step02_refinement.tmp
    3. temp/.../file01_step02_refinement.tmp -> polish.json -> processed_documentN_output.md

New File Organization:
    Temp directory: temp/input_document_20250131_12345/
    Log file: temp/input_document_20250131_12345/input_document_20250131_12345.log
    Original input: temp/input_document_20250131_12345/original_input_input_document.md
    Final output copy: temp/input_document_20250131_12345/final_output_final_output.md
    Intermediate files: temp/input_document_20250131_12345/step01_analysis.tmp, etc.

Requirements:
    - prompt_runner.py must be installed and available in your system PATH
    - All prompt JSON files must exist
    - Input file must exist
    - OpenRouter API key must be set (OPENROUTER_API_KEY)

File Organization:
    All temporary files, logs, and intermediate outputs are stored in the same
    temporary directory (temp/input_filename_date_pid/) for easy management and
    debugging. Each prompt_runner.py execution will use this shared temp directory.
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
        '--prompt-runner-config',
        help='Configuration file to pass to each prompt_runner.py execution',
        metavar='CONFIG_FILE'
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
        runner = PromptChainRunner(args.config, args.input, args.output, 
                                 args.prompt_runner_config, args.debug)
        
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
    