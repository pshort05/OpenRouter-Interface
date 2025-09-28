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
import time
import uuid
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class ConsoleOutputManager:
    """Manages clean console output with colored status indicators."""

    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def __init__(self):
        self.step_results = []

    def print_header(self, config_name: str, temp_dir: Path):
        """Print the initial header with basic setup info."""
        print(f"Prompt Chain Runner initialized - using Temp directory: {temp_dir}")
        print(f"Using Configuration file: {config_name}")
        print("Verifying prompts and input file\n")

    def print_step_start(self, step, prompt_name: str = None, passes: int = 1, append: bool = False):
        """Print step execution start with passes and append information."""
        info_parts = []
        if passes > 1:
            info_parts.append(f"{passes} passes")
        if append:
            info_parts.append("append mode")

        info_str = f" ({', '.join(info_parts)})" if info_parts else ""

        if prompt_name:
            print(f"Executing Prompt {step}: {prompt_name}{info_str}")
        else:
            print(f"Executing Prompt {step}:{info_str}")

    def print_step_result(self, step, prompt_name: str, file_size: str, success: bool, execution_time: float, error_message: str = None, skipped: bool = False, passes: int = 1, append: bool = False):
        """Print step execution result with colored status indicator, timing, passes/append info, and optional error or skip status."""
        info_parts = []
        if passes > 1:
            info_parts.append(f"{passes} passes")
        if append:
            info_parts.append("append")

        info_str = f" ({', '.join(info_parts)})" if info_parts else ""

        if skipped:
            status = f"{self.YELLOW}⚠️{self.RESET}"
            if prompt_name:
                print(f"Result:   {status} prompt {step} {prompt_name}{info_str} {self.YELLOW}SKIPPED{self.RESET} (on_error: continue) time: {execution_time:.1f} seconds")
            else:
                print(f"Result:   {status} prompt {step}{info_str} {self.YELLOW}SKIPPED{self.RESET} (on_error: continue) time: {execution_time:.1f} seconds")
        elif success:
            status = f"{self.GREEN}✅{self.RESET}"
            if prompt_name:
                print(f"Result:   {status} prompt {step} {prompt_name}{info_str} output size: {file_size} time: {execution_time:.1f} seconds")
            else:
                print(f"Result:   {status} prompt {step}{info_str} output size: {file_size} time: {execution_time:.1f} seconds")
        else:
            status = f"{self.RED}❌{self.RESET}"
            if prompt_name:
                print(f"Result:   {status} prompt {step} {prompt_name}{info_str} {self.RED}FAILED{self.RESET} time: {execution_time:.1f} seconds")
            else:
                print(f"Result:   {status} prompt {step}{info_str} {self.RED}FAILED{self.RESET} time: {execution_time:.1f} seconds")

            # Show error message on the next line if provided
            if error_message:
                print(f"          {self.RED}Error: {error_message}{self.RESET}")

        print()  # Add blank line after each result

        # Store result for final report
        self.step_results.append({
            'step': step,
            'name': prompt_name,
            'file_size': file_size,
            'success': success,
            'execution_time': execution_time,
            'skipped': skipped,
            'passes': passes,
            'append': append
        })

    def print_final_report(self, config_name: str, original_file_name: str, original_file_size: str, overall_success: bool):
        """Print the final report with all step results."""
        print(f"Final Report {config_name}")

        if overall_success:
            print(f"{self.GREEN}✅ Prompt chain completed successfully!{self.RESET}")
        else:
            print(f"{self.RED}❌ Prompt chain Failed!{self.RESET}")

        # Show original input file
        print(f"       {self.GREEN}✅{self.RESET} original_input_{original_file_name} size: {original_file_size}")

        # Show each step result
        for result in self.step_results:
            step = result['step']
            name = result['name']
            file_size = result['file_size']
            success = result['success']
            execution_time = result.get('execution_time', 0)
            skipped = result.get('skipped', False)
            passes = result.get('passes', 1)
            append = result.get('append', False)

            info_parts = []
            if passes > 1:
                info_parts.append(f"{passes} passes")
            if append:
                info_parts.append("append")

            info_str = f" ({', '.join(info_parts)})" if info_parts else ""

            if skipped:
                status_icon = f"{self.YELLOW}⚠️{self.RESET}"
                display_size = "skipped"
            elif success:
                status_icon = f"{self.GREEN}✅{self.RESET}"
                display_size = f"size: {file_size}"
            else:
                status_icon = f"{self.RED}❌{self.RESET}"
                display_size = "failed"

            if name:
                print(f"       {status_icon} prompt {step} {name}{info_str} {display_size}")
            else:
                print(f"       {status_icon} prompt {step}{info_str} {display_size}")


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

        # Track detailed execution results for final report
        self.execution_results = []  # List of execution details for each file
        
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

        # Initialize console output manager
        self.console = ConsoleOutputManager()

        # Print clean console header
        self.console.print_header(self.config_file.name, self.temp_dir)

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
        """Create temporary directory using YAML config filename: <config_filename>_<date>_<pid>"""
        # Get config file name (without extension)
        config_basename = self.config_file.stem  # filename without extension

        # Create temp directory name: configname_date_pid
        temp_dirname = f"{config_basename}_{self.timestamp}_{self.process_id}"

        temp_base = Path.cwd() / "temp"
        temp_base.mkdir(exist_ok=True)

        temp_subdir = temp_base / temp_dirname
        temp_subdir.mkdir(exist_ok=True)

        return temp_subdir
    
    def _create_log_file(self) -> Path:
        """Create log file in temp directory using same naming convention."""
        # Get config file name (without extension)
        config_basename = self.config_file.stem

        # Create log filename using same convention as directory
        log_filename = f"{config_basename}_{self.timestamp}_{self.process_id}.log"
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
        
        # Console handler - only show minimal output unless debug mode
        if self.debug:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.DEBUG)
            logging.root.addHandler(console_handler)

        # Configure root logger
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(file_handler)
        
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
        
        # Validate prompt numbering (1-99) and substeps (N.1-N.9)
        valid_numbers = set(range(1, 100))
        prompt_numbers = set()
        substep_numbers = set()  # Track substeps like 6.1, 6.2, etc.

        for key, prompt_config in prompts.items():
            if not key.startswith('prompt '):
                raise ValueError(f"Invalid prompt key format: {key}. Expected 'prompt N' or 'prompt N.S' where N is 1-99 and S is 1-9")

            try:
                number_part = key.split()[1]  # Get the number part after 'prompt '

                if '.' in number_part:
                    # Handle substeps like "6.1", "6.2"
                    main_num, sub_num = number_part.split('.')
                    main_number = int(main_num)
                    sub_number = int(sub_num)

                    if main_number not in valid_numbers:
                        raise ValueError(f"Main prompt number must be 1-99, got: {main_number}")
                    if sub_number < 1 or sub_number > 9:
                        raise ValueError(f"Substep number must be 1-9, got: {sub_number}")

                    substep_numbers.add((main_number, sub_number))
                else:
                    # Handle regular prompts like "6"
                    number = int(number_part)
                    if number not in valid_numbers:
                        raise ValueError(f"Prompt number must be 1-99, got: {number}")
                    prompt_numbers.add(number)

            except (IndexError, ValueError) as e:
                if isinstance(e, ValueError) and "Substep number must be" in str(e):
                    raise e
                if isinstance(e, ValueError) and "Main prompt number must be" in str(e):
                    raise e
                raise ValueError(f"Invalid prompt key format: {key}. Expected 'prompt N' or 'prompt N.S' where N is 1-99 and S is 1-9")

            # Validate prompt configuration (can be string or dict)
            self._validate_prompt_config(prompt_config, key)
        
        # Check for sequential numbering starting from 1 (main prompts only)
        if prompt_numbers:  # Only validate if there are main prompts
            sorted_numbers = sorted(prompt_numbers)
            expected_numbers = list(range(1, len(sorted_numbers) + 1))

            if sorted_numbers != expected_numbers:
                raise ValueError(f"Main prompts must be numbered sequentially starting from 1. Found: {sorted_numbers}")

        # Validate substeps - substeps can only exist if their main prompt exists
        for main_num, sub_num in substep_numbers:
            if main_num not in prompt_numbers:
                raise ValueError(f"Substep {main_num}.{sub_num} requires main prompt {main_num} to exist")

        # Update total prompts count to include substeps
        total_main_prompts = len(prompt_numbers)
        total_substeps = len(substep_numbers)
        self.total_prompts = total_main_prompts + total_substeps
        
        # Validate ALL prompt files exist before any execution (supports comma-separated files)
        missing_prompts = []
        for prompt_key, prompt_config in prompts.items():
            # Extract prompt file path (handle both string and dict formats)
            prompt_file = self._get_prompt_file(prompt_config)

            # Handle comma-separated prompt files
            if ',' in prompt_file:
                prompt_paths = [Path(p.strip()) for p in prompt_file.split(',')]
                for i, prompt_path in enumerate(prompt_paths, 1):
                    if not prompt_path.exists():
                        missing_prompts.append(f"{prompt_key} (file {i}): {prompt_path}")
                    elif not prompt_path.is_file():
                        missing_prompts.append(f"{prompt_key} (file {i}): {prompt_path} (exists but is not a file)")
            else:
                # Single prompt file
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
        
        # total_prompts is already set in the validation logic above
    
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

    def _get_prompt_settings(self, prompt_config) -> Dict[str, Any]:
        """Extract all setting overrides from prompt config."""
        if isinstance(prompt_config, dict):
            # Extract all settings except the special keys (prompt_file, config_file, name, on_error, passes, append)
            special_keys = {'prompt_file', 'config_file', 'name', 'on_error', 'passes', 'append'}
            settings = {k: v for k, v in prompt_config.items() if k not in special_keys}
            return settings
        return {}

    def _build_sorted_prompt_list(self, prompts: Dict[str, Any]) -> List[tuple]:
        """Build sorted list of prompts including substeps in proper order."""
        prompt_items = []

        for key, prompt_config in prompts.items():
            number_part = key.split()[1]

            if '.' in number_part:
                main_num, sub_num = number_part.split('.')
                main_number = int(main_num)
                sub_number = int(sub_num)
                sort_key = main_number + (sub_number / 10.0)
                display_step = f"{main_number}.{sub_number}"
            else:
                main_number = int(number_part)
                sort_key = float(main_number)
                display_step = str(main_number)

            prompt_items.append((sort_key, display_step, prompt_config))

        prompt_items.sort(key=lambda x: x[0])
        return [(item[1], item[2]) for item in prompt_items]

    def _get_prompt_name(self, prompt_config) -> Optional[str]:
        """Extract name from prompt config (returns None if not specified)."""
        if isinstance(prompt_config, dict):
            return prompt_config.get('name')
        return None

    def _get_on_error_behavior(self, prompt_config) -> str:
        """Extract on_error behavior from prompt config (defaults to 'stop')."""
        if isinstance(prompt_config, dict):
            on_error = prompt_config.get('on_error', 'stop')
            if on_error not in ['stop', 'continue']:
                logging.warning(f"Invalid on_error value '{on_error}', defaulting to 'stop'")
                return 'stop'
            return on_error
        return 'stop'

    def _get_passes(self, prompt_config) -> int:
        """Extract passes count from prompt config (defaults to 1, max 99, 0 or less means skip)."""
        if isinstance(prompt_config, dict):
            passes = prompt_config.get('passes', 1)

            # Validate passes value
            if not isinstance(passes, int):
                try:
                    passes = int(passes)
                except (ValueError, TypeError):
                    logging.warning(f"Invalid passes value '{passes}', defaulting to 1")
                    return 1

            # Enforce maximum limit
            if passes > 99:
                logging.warning(f"Passes value {passes} exceeds maximum of 99, capping at 99")
                return 99

            # Return actual value (including 0 or negative for skipping)
            return passes
        return 1

    def _get_append(self, prompt_config) -> bool:
        """Extract append behavior from prompt config (defaults to False)."""
        if isinstance(prompt_config, dict):
            append = prompt_config.get('append', False)

            # Validate append value
            if not isinstance(append, bool):
                if isinstance(append, str):
                    append_lower = append.lower()
                    if append_lower in ['yes', 'true', '1']:
                        return True
                    elif append_lower in ['no', 'false', '0']:
                        return False
                    else:
                        logging.warning(f"Invalid append value '{append}', defaulting to False")
                        return False
                else:
                    logging.warning(f"Invalid append value type '{type(append)}', defaulting to False")
                    return False

            return append
        return False

    def _get_output_append(self) -> bool:
        """Get output_append setting from config (defaults to False)."""
        return self.config.get('output_append', False)

    def _get_output_format(self) -> str:
        """Get output_format setting from config (defaults to 'markdown')."""
        return self.config.get('output_format', 'markdown')

    def _format_file_size(self, file_path: Path) -> str:
        """Format file size in human-readable format with 1 decimal place (e.g., 13.5k, 1.2M)."""
        try:
            size_bytes = file_path.stat().st_size

            if size_bytes < 1024:
                return f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f}k"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f}M"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f}G"
        except Exception:
            return "unknown"

    def _generate_final_report(self) -> str:
        """
        Generate the detailed final report showing all prompt executions and file sizes.

        Returns:
            Formatted report string
        """
        config_name = self.config_file.stem
        report_lines = [f"\nFinal Report {config_name}"]

        for file_result in self.execution_results:
            input_file_name = file_result['input_file']
            prompts = file_result['prompts']
            original_file_size = file_result['original_file_size']

            # Check if all prompts succeeded for this file
            all_prompts_succeeded = all(p['success'] for p in prompts)

            if all_prompts_succeeded:
                report_lines.append(f"✅ Prompt chain completed successfully!")
            else:
                report_lines.append(f"❌ Prompt chain Failed!")

            # Show original input file
            report_lines.append(f"       ✅ original_input_{input_file_name} size: {original_file_size}")

            # Show each prompt step
            for prompt_info in prompts:
                step_num = prompt_info['step']
                prompt_name = prompt_info['name']
                file_size = prompt_info['file_size']
                success = prompt_info['success']

                status_icon = "✅" if success else "❌"

                if prompt_name:
                    report_lines.append(f"       {status_icon} prompt {step_num} {prompt_name} size: {file_size}")
                else:
                    report_lines.append(f"       {status_icon} prompt {step_num} size: {file_size}")

        return "\n".join(report_lines)
    
    def _create_step_config_file(self, step: int, step_settings: Dict[str, Any] = None) -> Optional[str]:
        """
        Create a temporary config file for this step with the specified settings.

        Args:
            step: Step number for filename uniqueness
            step_settings: Dictionary of settings to override for this step

        Returns:
            Path to temporary config file, or None if no step-specific config needed
        """
        if not step_settings and not self.prompt_runner_config and 'global_config' not in self.config:
            return None

        # Create a temporary config file in the temp directory
        step_formatted = str(step).replace('.', '_')
        step_config_path = self.temp_dir / f"step_{step_formatted}_config.yaml"

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

        # Override with step-specific settings if provided
        if step_settings:
            step_config.update(step_settings)

            # Log the overrides
            override_list = []
            for key, value in step_settings.items():
                override_list.append(f"{key}: {value}")
            if override_list:
                logging.info(f"Step {step}: Using step-specific settings: {', '.join(override_list)}")

        # Ensure payload file is created in temp directory
        import os
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = os.getpid()
        step_formatted = str(step).replace('.', '_')
        temp_payload_filename = f'step_{step_formatted}_payload_{timestamp}_{process_id}.json'
        temp_payload_path = self.temp_dir / temp_payload_filename
        step_config['payload_file'] = str(temp_payload_path)
        logging.debug(f"Step {step}: Using temp payload file: {temp_payload_filename}")

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
    
    def _get_intermediate_filename(self, input_file: Path, step: int, prompt_name: str = None) -> str:
        """
        Generate intermediate filename using new naming convention.
        Format: {input_name}_step_{step_number}{_prompt_name}{input_ext}

        Args:
            input_file: Original input file to get name and extension from
            step: Current step number
            prompt_name: Optional prompt name from YAML config

        Returns:
            Filename string for intermediate file
        """
        input_name = input_file.stem
        input_ext = input_file.suffix

        # Build filename components - handle substeps by replacing . with _
        step_str = str(step)
        step_formatted = step_str.replace('.', '_')
        filename_parts = [input_name, "step", step_formatted]

        # Add prompt name if provided
        if prompt_name:
            # Clean up the prompt name (replace special characters with underscores)
            clean_name = "".join(c if c.isalnum() else "_" for c in prompt_name)
            filename_parts.append(clean_name)

        # Combine parts with underscores and add extension
        filename = "_".join(filename_parts) + input_ext
        return filename

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
            step_formatted = str(step).replace('.', '_')
            temp_filename = f"step{step_formatted}_{clean_name}.tmp"
        else:
            step_formatted = str(step).replace('.', '_')
            temp_filename = f"step{step_formatted}.tmp"

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

    def _save_initial_file(self, input_file: Path) -> Path:
        """
        Save the initial file using the new naming convention.
        This is step 0 in the chain process.

        Args:
            input_file: Original input file

        Returns:
            Path to the saved initial file
        """
        initial_filename = self._get_intermediate_filename(input_file, "00")
        initial_file_path = self.temp_dir / initial_filename

        try:
            shutil.copy2(input_file, initial_file_path)
            logging.info(f"Initial file saved: {initial_filename}")
            return initial_file_path
        except Exception as e:
            logging.error(f"Failed to save initial file: {e}")
            raise
    
    def _copy_output_to_temp(self, output_file: Path):
        """Copy the final output file to temp directory for reference."""
        output_copy = self.temp_dir / f"final_output_{output_file.name}"
        try:
            shutil.copy2(output_file, output_copy)
            logging.info(f"Final output file copied to temp directory: {output_copy.name}")
        except Exception as e:
            logging.warning(f"Failed to copy output file to temp directory: {e}")

    def _append_to_output(self, step_output_file: Path, final_output_file: Path, step: int, prompt_name: str = None):
        """
        Append the output from a step to the final output file.

        Args:
            step_output_file: Path to the step's output file
            final_output_file: Path to the final accumulated output file
            step: Step number for section headers
            prompt_name: Optional prompt name for section headers
        """
        try:
            # Read the step output
            with open(step_output_file, 'r', encoding='utf-8') as f:
                step_content = f.read().strip()

            if not step_content:
                logging.warning(f"Step {step} output file is empty, skipping append")
                return

            # Create section header
            if prompt_name:
                section_header = f"# Step {step}: {prompt_name}"
            else:
                section_header = f"# Step {step}"

            # Determine if this is the first append (file doesn't exist or is empty)
            is_first_append = not final_output_file.exists() or final_output_file.stat().st_size == 0

            # Append to final output file
            with open(final_output_file, 'a', encoding='utf-8') as f:
                if not is_first_append:
                    f.write('\n\n---\n\n')  # Add separator between sections

                f.write(f"{section_header}\n\n")
                f.write(step_content)
                f.write('\n')

            logging.info(f"Step {step} output appended to final file: {final_output_file}")

        except Exception as e:
            logging.error(f"Failed to append step {step} output to final file: {e}")
            raise

    def _create_final_output_header(self, final_output_file: Path, input_file: Path):
        """
        Create a header for the final output file in append mode.

        Args:
            final_output_file: Path to the final output file
            input_file: Path to the input file being processed
        """
        try:
            # Create header content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header_content = f"""# Prompt Chain Output

**Input File:** {input_file.name}
**Generated:** {timestamp}
**Config:** {self.config_file.name}
**Chain Steps:** {self.total_prompts}

---

"""

            # Write header to file
            with open(final_output_file, 'w', encoding='utf-8') as f:
                f.write(header_content)

            logging.info(f"Created final output header: {final_output_file}")

        except Exception as e:
            logging.error(f"Failed to create final output header: {e}")
            raise
    
    def _run_prompt_runner(self, prompt_config, input_file: Path, output_file: Path, step: int) -> tuple[bool, str]:
        """
        Run prompt_runner.py with specified parameters.

        Args:
            prompt_config: Prompt configuration (string or dict with prompt_file, optional config_file, and optional model)
            input_file: Input file for this step
            output_file: Output file for this step
            step: Current step number for logging

        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        # Extract file paths and settings from config
        prompt_file = self._get_prompt_file(prompt_config)
        step_config_file = self._get_prompt_config_file(prompt_config)
        step_settings = self._get_prompt_settings(prompt_config)
        
        # Build command - use openrouter-runner entry point
        cmd = [
            "openrouter-runner",
            "-p", prompt_file,
            "-i", str(input_file),
            "-o", str(output_file),
            "-l", str(self.log_file)  # Use same log file
        ]
        
        # Create step-specific config file if needed (handles step-specific settings and global config)
        effective_config_file = None

        if step_config_file:
            # User specified a step-specific config file, use it
            effective_config_file = step_config_file
            logging.info(f"Step {step}: Using step-specific config file: {step_config_file}")
        elif step_settings or self.prompt_runner_config or 'global_config' in self.config:
            # Create a temporary config file with step-specific settings and/or global config
            effective_config_file = self._create_step_config_file(step, step_settings)
            if effective_config_file:
                logging.info(f"Step {step}: Created temporary config file with setting overrides")
        
        # Add config file if we have one
        if effective_config_file:
            cmd.extend(["-c", effective_config_file])
            if step_settings:
                settings_summary = []
                for key, value in step_settings.items():
                    settings_summary.append(f"{key}={value}")
                logging.info(f"Step {step}: Using settings: {', '.join(settings_summary)}")
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
                return True, None
            else:
                logging.error(f"Step {step}: FAILED - openrouter-runner returned code {result.returncode}")
                error_message = "Unknown error"
                if result.stderr:
                    logging.error(f"Step {step} stderr: {result.stderr}")
                    # Extract a concise error message from stderr
                    error_lines = result.stderr.strip().split('\n')
                    for line in reversed(error_lines):
                        if line.strip() and not line.startswith('  '):
                            error_message = line.strip()
                            break
                if result.stdout:
                    logging.error(f"Step {step} stdout: {result.stdout}")
                return False, error_message
                
        except subprocess.TimeoutExpired:
            error_message = "openrouter-runner timed out after 5 minutes"
            logging.error(f"Step {step}: TIMEOUT - {error_message}")
            return False, error_message
        except FileNotFoundError:
            error_message = "openrouter-runner not found in PATH"
            logging.error(f"Step {step}: ERROR - {error_message}")
            logging.error("Make sure openrouter-runner is installed and accessible in your system PATH")
            return False, error_message
        except Exception as e:
            error_message = f"Failed to execute openrouter-runner: {e}"
            logging.error(f"Step {step}: ERROR - {error_message}")
            return False, error_message
    
    def _validate_file_size(self, input_file: Path, output_file: Path, step: str, step_config: dict = None) -> bool:
        """
        Validate that output file size is within acceptable range compared to input.

        Args:
            input_file: Original input file for comparison
            output_file: Output file to validate
            step: Current step number (can be "1", "6.1", "6.2", etc.) for logging
            step_config: Optional step-specific configuration for overrides

        Returns:
            True if file size is acceptable, False otherwise
        """
        # Start with base config
        validation_config = self.config.get('file_size_validation', {})

        # Override with global_config if present
        if 'global_config' in self.config and 'file_size_validation' in self.config['global_config']:
            validation_config.update(self.config['global_config']['file_size_validation'])

        # Override with step-specific config if present
        if step_config and 'file_size_validation' in step_config:
            validation_config.update(step_config['file_size_validation'])

        # Check for individual step-level settings (max_size_difference_percent can be set directly)
        if step_config and 'max_size_difference_percent' in step_config:
            validation_config['max_size_difference_percent'] = step_config['max_size_difference_percent']

        # Default values if not configured (updated default from 30% to 50%)
        enabled = validation_config.get('enabled', True)
        max_diff_percent = validation_config.get('max_size_difference_percent', 50)
        min_file_size = validation_config.get('min_file_size_bytes', 100)

        if not enabled:
            logging.debug(f"Step {step}: File size validation disabled")
            return True

        try:
            input_size = input_file.stat().st_size
            output_size = output_file.stat().st_size

            # Check minimum file size threshold
            if output_size < min_file_size:
                logging.error(f"Step {step}: Output file too small ({output_size} bytes < {min_file_size} bytes minimum)")
                return False

            # Calculate size difference percentage
            if input_size == 0:
                # Handle edge case of empty input file
                logging.warning(f"Step {step}: Input file is empty, skipping size comparison")
                return output_size >= min_file_size

            size_diff_percent = abs(output_size - input_size) / input_size * 100

            if size_diff_percent > max_diff_percent:
                direction = "larger" if output_size > input_size else "smaller"
                logging.error(f"Step {step}: Output file is {size_diff_percent:.1f}% {direction} than input "
                             f"(input: {input_size} bytes, output: {output_size} bytes, max allowed: {max_diff_percent}%)")
                return False

            logging.info(f"Step {step}: File size validation passed - {size_diff_percent:.1f}% difference "
                        f"(input: {input_size} bytes, output: {output_size} bytes)")
            return True

        except Exception as e:
            logging.error(f"Step {step}: File size validation failed due to error: {e}")
            return False

    def _verify_output_file(self, file_path: Path, step: str, input_file: Path = None, step_config: dict = None) -> bool:
        """Verify that output file was created and has content."""
        if not file_path.exists():
            logging.error(f"Step {step}: Output file not created: {file_path}")
            return False

        file_size = file_path.stat().st_size
        if file_size == 0:
            logging.error(f"Step {step}: Output file is empty: {file_path}")
            return False

        # Perform file size validation if input file is provided
        if input_file and not self._validate_file_size(input_file, file_path, step, step_config):
            logging.error(f"Step {step}: File size validation failed")
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
            # Get sorted prompt list (including substeps)
            prompts = self.config['prompts']
            logging.info(f"Processing {len(prompts)} prompts from config")

            # Check if we have prompts to execute
            if self.total_prompts == 0:
                logging.error("No prompts found to execute!")
                logging.error(f"Config prompts section: {prompts}")
                return False

            # Build sorted list that includes both main prompts and substeps
            sorted_prompts = self._build_sorted_prompt_list(prompts)

            logging.info(f"Sorted prompts list has {len(sorted_prompts)} entries")

            if not sorted_prompts:
                logging.error("No prompts to execute - this should not happen after validation")
                return False

            # Execute preprocessing scripts before chain execution
            if not self._run_preprocessing():
                logging.error("Preprocessing scripts failed - aborting chain execution")
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

                # Save initial file with new naming convention (step 0)
                initial_file = self._save_initial_file(input_file)

                # Get output file for this input
                final_output = self._get_output_file(input_file)
                logging.info(f"Final output for this file: {final_output}")

                # Check if output appending is enabled
                output_append = self._get_output_append()
                if output_append:
                    logging.info("Output appending enabled - will accumulate all step outputs")
                    # Create header for final output file
                    self._create_final_output_header(final_output, input_file)

                # Initialize tracking for this file
                file_result = {
                    'input_file': input_file.name,
                    'original_file_size': self._format_file_size(input_file),
                    'prompts': []
                }

                # Execute prompts in sequence for this input file
                current_input = input_file
                file_successful = True
                
                for step_display, prompt_config in sorted_prompts:
                    prompt_file = self._get_prompt_file(prompt_config)
                    step_config = self._get_prompt_config_file(prompt_config)
                    step_settings = self._get_prompt_settings(prompt_config)
                    prompt_name = self._get_prompt_name(prompt_config)

                    # Get passes count for this step
                    passes = self._get_passes(prompt_config)

                    # Get append behavior for this step
                    step_append = self._get_append(prompt_config)

                    # Skip step if passes is 0 or negative
                    if passes <= 0:
                        logging.info(f"Step {step_display}: Skipping step (passes={passes})")
                        # Show skipped status in console
                        self.console.print_step_result(step_display, prompt_name, "skipped", True, 0.0, skipped=True)
                        # Track this step as skipped
                        file_result['prompts'].append({
                            'step': step_display,
                            'name': prompt_name,
                            'file_size': 'skipped',
                            'success': True,
                            'skipped': True
                        })
                        continue

                    # Clean console output with passes and append info
                    if passes > 1 and step_append:
                        self.console.print_step_start(step_display, prompt_name, passes, append=True)
                    elif passes > 1:
                        self.console.print_step_start(step_display, prompt_name, passes)
                    elif step_append:
                        self.console.print_step_start(step_display, prompt_name, append=True)
                    else:
                        self.console.print_step_start(step_display, prompt_name)

                    # Start timing this step (including all passes)
                    step_start_time = time.time()

                    # Detailed logging to file
                    logging.info(f"\n--- File {file_index}, Step {step_display}/{self.total_prompts} ---")
                    logging.info(f"Executing prompt: {prompt_file}")
                    if prompt_name:
                        logging.info(f"Using prompt name: {prompt_name}")
                    if step_config:
                        logging.info(f"Using step-specific config: {step_config}")
                    if step_settings:
                        settings_list = [f"{k}={v}" for k, v in step_settings.items()]
                        logging.info(f"Using step-specific settings: {', '.join(settings_list)}")
                    if passes > 1:
                        logging.info(f"Step will run {passes} passes")

                    # Execute multiple passes for this step
                    step_pass_input = current_input
                    step_success = True
                    step_error_message = None
                    final_output_for_step = None

                    for pass_num in range(1, passes + 1):
                        # Determine output file for this pass
                        if passes > 1:
                            pass_suffix = f"_pass_{pass_num}"
                        else:
                            pass_suffix = ""

                        if output_append:
                            # In append mode, all steps output to intermediate files
                            intermediate_filename = self._get_intermediate_filename(input_file, step_display, prompt_name, pass_suffix)
                            current_output = self.temp_dir / intermediate_filename
                            logging.info(f"Step {step_display} pass {pass_num}/{passes} temp output (append mode): {current_output.name}")
                        else:
                            # All steps (including final) create intermediate files in temp directory
                            intermediate_filename = self._get_intermediate_filename(input_file, step_display, prompt_name, pass_suffix)
                            current_output = self.temp_dir / intermediate_filename
                            # Check if this is the final step (last in sorted list)
                            is_final_step = (step_display, prompt_config) == sorted_prompts[-1]
                            if is_final_step:
                                logging.info(f"Final step - pass {pass_num}/{passes} temp output: {current_output.name}")
                            else:
                                logging.info(f"Intermediate step - pass {pass_num}/{passes} temp output: {current_output.name}")

                        # Run prompt_runner.py for this pass
                        if passes > 1:
                            logging.info(f"Step {step_display}: Executing pass {pass_num}/{passes}")

                        success, error_message = self._run_prompt_runner(prompt_config, step_pass_input, current_output, step_display)

                        if not success:
                            # Pass failed - handle based on on_error behavior
                            step_success = False
                            step_error_message = error_message
                            logging.error(f"Step {step_display}: Pass {pass_num}/{passes} failed")
                            break
                        else:
                            # Pass succeeded
                            logging.info(f"Step {step_display}: Pass {pass_num}/{passes} completed successfully")

                            # Verify output file
                            if not self._verify_output_file(current_output, step_display, step_pass_input, step_settings):
                                step_success = False
                                step_error_message = "Output file verification failed"
                                logging.error(f"Step {step_display}: Pass {pass_num}/{passes} verification failed")
                                break

                            # Handle append behavior
                            if step_append:
                                # Append mode: append output to input
                                logging.info(f"Step {step_display}: Append mode enabled - appending output to input")
                                try:
                                    # Read the current pass output
                                    with open(current_output, 'r', encoding='utf-8') as f:
                                        output_content = f.read()

                                    # Read the current input
                                    with open(step_pass_input, 'r', encoding='utf-8') as f:
                                        input_content = f.read()

                                    # Create appended content
                                    appended_content = input_content + "\n\n" + output_content

                                    # Create a new file with appended content for the next pass
                                    if pass_num < passes:
                                        # Create intermediate appended file for next pass
                                        append_suffix = f"_pass_{pass_num}_appended"
                                        intermediate_filename = self._get_intermediate_filename(input_file, step_display, prompt_name, append_suffix)
                                        appended_file = self.temp_dir / intermediate_filename

                                        with open(appended_file, 'w', encoding='utf-8') as f:
                                            f.write(appended_content)

                                        step_pass_input = appended_file
                                        logging.info(f"Step {step_display}: Pass {pass_num} appended content saved to {appended_file.name}")
                                    else:
                                        # Final pass - overwrite the output file with appended content
                                        with open(current_output, 'w', encoding='utf-8') as f:
                                            f.write(appended_content)
                                        logging.info(f"Step {step_display}: Final pass appended content saved to output")

                                except Exception as e:
                                    logging.error(f"Step {step_display}: Failed to append content: {e}")
                                    # Continue with normal processing on append failure
                                    step_append = False

                            # Set final output and prepare input for next pass
                            final_output_for_step = current_output
                            if pass_num < passes and not step_append:
                                # Use this pass's output as input for next pass (normal mode)
                                step_pass_input = current_output
                                logging.info(f"Step {step_display}: Pass {pass_num} output will be input for pass {pass_num + 1}")
                            elif pass_num < passes and step_append:
                                # step_pass_input already set above in append mode
                                logging.info(f"Step {step_display}: Pass {pass_num} appended content will be input for pass {pass_num + 1}")

                    # Calculate execution time (for all passes)
                    step_execution_time = time.time() - step_start_time

                    # Handle step results (after all passes)
                    if not step_success:
                        # Check on_error behavior for this step
                        on_error_behavior = self._get_on_error_behavior(prompt_config)

                        if on_error_behavior == 'continue':
                            # Skip this step and pass input file through unchanged
                            logging.warning(f"Step {step_display} failed, but on_error=continue - skipping step")
                            logging.info(f"Copying input file unchanged: {current_input} -> {final_output_for_step}")

                            try:
                                # Copy input file to output location unchanged
                                import shutil
                                if final_output_for_step:
                                    shutil.copy2(current_input, final_output_for_step)
                                    output_to_use = final_output_for_step
                                else:
                                    # If no output was created, create one
                                    intermediate_filename = self._get_intermediate_filename(input_file, step_display, prompt_name)
                                    output_to_use = self.temp_dir / intermediate_filename
                                    shutil.copy2(current_input, output_to_use)

                                # Get formatted file size for display (from input file since we copied it)
                                formatted_size = self._format_file_size(current_input)

                                # Show skipped status in console
                                self.console.print_step_result(step_display, prompt_name, formatted_size, True, step_execution_time, skipped=True)

                                # Track this step's execution result as skipped
                                file_result['prompts'].append({
                                    'step': step_display,
                                    'name': prompt_name,
                                    'file_size': formatted_size,
                                    'success': True,  # Consider it successful since we handled it
                                    'skipped': True
                                })

                                # Update input for next iteration
                                current_input = output_to_use
                                self.prompts_executed += 1
                                logging.info(f"File {file_index}, Step {step_display} skipped successfully")
                                continue  # Continue to next step

                            except Exception as e:
                                logging.error(f"Failed to copy input file for skipped step: {e}")
                                # If we can't even copy the file, treat as a regular failure
                                self.console.print_step_result(step_display, prompt_name, 'failed', False, step_execution_time, f"Copy failed: {e}")
                                logging.error(f"Chain execution failed at File {file_index}, Step {step_display}")
                                # Track this failed step
                                file_result['prompts'].append({
                                    'step': step_display,
                                    'name': prompt_name,
                                    'file_size': 'failed',
                                    'success': False
                                })
                                file_successful = False
                                all_successful = False
                                break
                        else:
                            # Default behavior: stop on error
                            # Clean console output with timing and error
                            self.console.print_step_result(step_display, prompt_name, 'failed', False, step_execution_time, step_error_message)

                            logging.error(f"Chain execution failed at File {file_index}, Step {step_display}")
                            # Track this failed step
                            file_result['prompts'].append({
                                'step': step_display,
                                'name': prompt_name,
                                'file_size': 'failed',
                                'success': False
                            })
                            file_successful = False
                            all_successful = False
                            break
                    else:
                        # Step succeeded (all passes completed successfully)
                        # Handle output appending if enabled
                        if output_append:
                            self._append_to_output(final_output_for_step, final_output, step_display, prompt_name)

                        # Copy final step output to the actual final output location (non-append mode)
                        is_final_step = (step_display, prompt_config) == sorted_prompts[-1]
                        if not output_append and is_final_step:
                            try:
                                shutil.copy2(final_output_for_step, final_output)
                                logging.info(f"Final step output copied to: {final_output}")
                            except Exception as e:
                                logging.error(f"Failed to copy final output: {e}")

                        # Get formatted file size for display
                        formatted_size = self._format_file_size(final_output_for_step)

                        # Clean console output with timing, passes, and append info
                        self.console.print_step_result(step_display, prompt_name, formatted_size, True, step_execution_time, passes=passes, append=step_append)

                        # Track this step's execution result
                        file_result['prompts'].append({
                            'step': step_display,
                            'name': prompt_name,
                            'file_size': formatted_size,
                            'success': True,
                            'passes': passes,
                            'append': step_append
                        })

                        # Update input for next iteration
                        current_input = final_output_for_step
                        self.prompts_executed += 1
                        logging.info(f"File {file_index}, Step {step_display} completed successfully ({passes} passes)")

                    # Continue to next step - this is the end of the main step loop

                # Add this file's results to the overall execution results
                self.execution_results.append(file_result)
                if file_successful:
                    # Copy final output to temp directory for reference
                    self._copy_output_to_temp(final_output)
                    total_files_processed += 1
                    logging.info(f"✓ File {file_index} processing completed successfully")
                else:
                    logging.error(f"❌ File {file_index} processing failed")

            # Execute postprocessing scripts after all files are processed
            if not self._run_postprocessing():
                logging.error("Postprocessing scripts failed - chain execution completed with errors")
                return False

            # Final summary after processing all files
            success_rate = (total_files_processed / len(input_files)) * 100 if input_files else 0

            if success_rate == 100:
                logging.info(f"🎉 All {total_files_processed} files processed successfully!")
                return True
            elif success_rate > 0:
                logging.warning(f"⚠️ Partial success: {total_files_processed}/{len(input_files)} files processed ({success_rate:.1f}%)")
                return False
            else:
                logging.error(f"❌ No files processed successfully")
                return False

        except KeyboardInterrupt:
            logging.info("Chain execution interrupted by user")
            return False
        except Exception as e:
            logging.error(f"Unexpected error during chain execution: {e}")
            return False

    def _get_intermediate_filename(self, input_file: Path, step: str, prompt_name: str = None, pass_suffix: str = "") -> str:
        """
        Generate intermediate filename using new naming convention with pass support.
        Format: {input_name}_step_{step_number}{_prompt_name}{pass_suffix}{input_ext}
        Args:
            input_file: Original input file to get name and extension from
            step: Current step number (can be "1", "6.1", "6.2", etc.)
            prompt_name: Optional prompt name from YAML config
            pass_suffix: Optional suffix for multi-pass execution (e.g., "_pass_2")
        Returns:
            Filename string for intermediate file
        """
        input_name = input_file.stem
        input_ext = input_file.suffix

        # Build filename components - handle substeps by replacing . with _
        step_str = str(step)
        step_formatted = step_str.replace('.', '_')
        filename_parts = [input_name, "step", step_formatted]

        # Add prompt name if provided
        if prompt_name:
            filename_parts.append(prompt_name)

        # Add pass suffix if provided
        if pass_suffix:
            filename_parts.append(pass_suffix.lstrip('_'))  # Remove leading underscore if present

        # Join parts with underscores and add extension
        filename = "_".join(filename_parts) + input_ext
        return filename

    def _get_preprocessing_scripts(self) -> List[Dict[str, str]]:
        """Extract preprocessing scripts from configuration (supports script01-script99 with optional name01)."""
        scripts = []
        preprocessing_config = self.config.get('preprocessing', {})

        if not isinstance(preprocessing_config, dict):
            return scripts

        # Extract scripts with numeric suffixes (script01-script99)
        script_commands = {}
        script_names = {}

        for key, value in preprocessing_config.items():
            if not isinstance(key, str) or not isinstance(value, str):
                continue

            # Check if key matches pattern: script + 2-digit number
            if key.startswith('script') and len(key) == 8:
                suffix = key[6:]  # Get the numeric part
                if suffix.isdigit() and len(suffix) == 2:
                    script_num = int(suffix)
                    if 1 <= script_num <= 99:
                        script_commands[suffix] = value

            # Check if key matches pattern: name + 2-digit number
            elif key.startswith('name') and len(key) == 6:
                suffix = key[4:]  # Get the numeric part
                if suffix.isdigit() and len(suffix) == 2:
                    script_num = int(suffix)
                    if 1 <= script_num <= 99:
                        script_names[suffix] = value

        # Combine scripts and names, sorted by number
        for suffix in sorted(script_commands.keys()):
            script_info = {
                'number': suffix,
                'command': script_commands[suffix],
                'name': script_names.get(suffix, f"Script {suffix}")
            }
            scripts.append(script_info)

        return scripts

    def _get_postprocessing_scripts(self) -> List[Dict[str, str]]:
        """Extract postprocessing scripts from configuration (supports script01-script99 with optional name01)."""
        scripts = []
        postprocessing_config = self.config.get('postprocessing', {})

        if not isinstance(postprocessing_config, dict):
            return scripts

        # Extract scripts with numeric suffixes (script01-script99)
        script_commands = {}
        script_names = {}

        for key, value in postprocessing_config.items():
            if not isinstance(key, str) or not isinstance(value, str):
                continue

            # Check if key matches pattern: script + 2-digit number
            if key.startswith('script') and len(key) == 8:
                suffix = key[6:]  # Get the numeric part
                if suffix.isdigit() and len(suffix) == 2:
                    script_num = int(suffix)
                    if 1 <= script_num <= 99:
                        script_commands[suffix] = value

            # Check if key matches pattern: name + 2-digit number
            elif key.startswith('name') and len(key) == 6:
                suffix = key[4:]  # Get the numeric part
                if suffix.isdigit() and len(suffix) == 2:
                    script_num = int(suffix)
                    if 1 <= script_num <= 99:
                        script_names[suffix] = value

        # Combine scripts and names, sorted by number
        for suffix in sorted(script_commands.keys()):
            script_info = {
                'number': suffix,
                'command': script_commands[suffix],
                'name': script_names.get(suffix, f"Script {suffix}")
            }
            scripts.append(script_info)

        return scripts

    def _execute_scripts(self, scripts: List[Dict[str, str]], phase: str) -> bool:
        """
        Execute scripts in numerical order with minimal console output.

        Args:
            scripts: List of script dictionaries with 'number', 'command', and 'name'
            phase: 'preprocessing' or 'postprocessing' for logging

        Returns:
            True if all scripts executed successfully, False otherwise
        """
        if not scripts:
            logging.info(f"No {phase} scripts configured")
            return True

        logging.info(f"Executing {len(scripts)} {phase} scripts")

        # Print phase header for console
        phase_title = "Pre Processing:" if phase == "preprocessing" else "Post Processing:"
        print(f"{phase_title}")

        for script_info in scripts:
            script_num = script_info['number']
            script_command = script_info['command']
            script_name = script_info['name']

            # Detailed logging to file
            logging.info(f"Executing {phase} script {script_num}: {script_command}")
            logging.info(f"Script {script_num} name: {script_name}")

            # Minimal console output - start
            print(f"Executing script {int(script_num)}: {script_name}")

            # Track execution time
            start_time = time.time()

            try:
                # Execute the script
                result = subprocess.run(
                    script_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                # Calculate execution time
                execution_time = time.time() - start_time

                if result.returncode == 0:
                    # Detailed logging to file
                    logging.info(f"Script {script_num} completed successfully in {execution_time:.1f} seconds")
                    if result.stdout.strip():
                        logging.info(f"Script {script_num} stdout: {result.stdout.strip()}")
                    if result.stderr.strip():
                        logging.info(f"Script {script_num} stderr: {result.stderr.strip()}")

                    # Minimal console output - success
                    print(f"Result:   ✅ complete:  time {execution_time:.1f} seconds\n")
                else:
                    # Detailed logging to file
                    logging.error(f"Script {script_num} failed with exit code {result.returncode} in {execution_time:.1f} seconds")
                    if result.stdout.strip():
                        logging.error(f"Script {script_num} stdout: {result.stdout.strip()}")
                    if result.stderr.strip():
                        logging.error(f"Script {script_num} stderr: {result.stderr.strip()}")

                    # Minimal console output - failure
                    print(f"Result:   ❌ failed: exit code {result.returncode}  time {execution_time:.1f} seconds\n")
                    return False

            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                logging.error(f"Script {script_num} timed out after {execution_time:.1f} seconds")
                print(f"Result:   ❌ timeout after {execution_time:.1f} seconds\n")
                return False
            except Exception as e:
                execution_time = time.time() - start_time
                logging.error(f"Failed to execute script {script_num}: {e}")
                print(f"Result:   ❌ error: {e}  time {execution_time:.1f} seconds\n")
                return False

        logging.info(f"All {phase} scripts completed successfully")
        return True

    def _run_preprocessing(self) -> bool:
        """Execute preprocessing scripts before chain execution."""
        scripts = self._get_preprocessing_scripts()
        return self._execute_scripts(scripts, "preprocessing")

    def _run_postprocessing(self) -> bool:
        """Execute postprocessing scripts after chain execution."""
        scripts = self._get_postprocessing_scripts()
        return self._execute_scripts(scripts, "postprocessing")

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

    # Multi-prompt chain (NEW) - Combines multiple prompts per step
    python prompt_chain_runner.py -c multi_prompt_chain.yaml

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

Per-Prompt Configuration (Different LLMs, Custom Names, and Setting Overrides):
    input_file: input_document.md
    output_file: final_output.md
    global_config:                    # Global settings applied to all prompts
        temperature: 0.7
        max_tokens: 20000
    prompts:
        prompt 1:
            name: dialogue
            prompt_file: creative_task.json
            config_file: claude_config.yaml     # Override with config file
        prompt 2:
            prompt_file: technical_task.json
            model: openai/gpt-4-turbo          # Override just the model
            temperature: 0.3                   # Override temperature for precision
            max_tokens: 30000                  # Override max_tokens for longer output
        prompt 3:
            name: final_polish
            prompt_file: final_edit.json
            temperature: 0.5                   # Override temperature for balance
            # Uses global model and max_tokens

Multi-Prompt Configuration (Combine Multiple Prompts Per Step):
    input_file: manuscript.md
    output_file: polished_output.md
    prompts:
        prompt 1:
            name: quality_analysis
            prompt_file: "quality_check.json,grammar_check.json"  # Combine two prompts
        prompt 2:
            name: style_improvement
            prompt_file: "style_guide.json,tone_adjustment.json,clarity_check.json"  # Combine three prompts
        prompt 3:
            prompt_file: final_polish.json  # Single prompt for final step

Output Appending Configuration:
    input_file: input_document.md
    output_file: combined_output.md
    output_append: true
    output_format: markdown  # Optional, defaults to markdown
    prompts:
        prompt 1:
            name: analysis
            prompt_file: analyze_content.json
        prompt 2:
            name: enhancement
            prompt_file: enhance_content.json
        prompt 3:
            name: finalization
            prompt_file: finalize_content.json

Execution Flow Examples (New Naming Convention):

Single File (Normal Mode):
    0. input_document.md -> saved as -> input_document_step_00.md (initial file)
    1. input_document.md -> analysis.json -> input_document_step_01_dialogue.md (with name)
    2. input_document_step_01_dialogue.md -> refinement.json -> input_document_step_02.md (without name)
    3. input_document_step_02.md -> polish.json -> final_output.md

Single File (Append Mode - output_append: true):
    0. input_document.md -> saved as -> input_document_step_00.md (initial file)
    1. input_document.md -> analysis.json -> input_document_step_01_analysis.md (appended to final)
    2. input_document.md -> enhancement.json -> input_document_step_02_enhancement.md (appended to final)
    3. input_document.md -> finalization.json -> input_document_step_03_finalization.md (appended to final)
    Final: combined_output.md contains all step outputs with headers

Multiple Files:
    For each file (document1.md, document2.md, document3.txt):
    0. documentN.md -> saved as -> documentN_step_00.md (initial file)
    1. documentN.md -> analysis.json -> documentN_step_01_dialogue.md (with name)
    2. documentN_step_01_dialogue.md -> refinement.json -> documentN_step_02.md (without name)
    3. documentN_step_02.md -> polish.json -> processed_documentN_output.md

New File Organization:
    Temp directory: temp/my_chain_config_20250131_12345/
    Log file: temp/my_chain_config_20250131_12345/my_chain_config_20250131_12345.log
    Original input: temp/my_chain_config_20250131_12345/original_input_input_document.md
    Initial file: temp/my_chain_config_20250131_12345/input_document_step_00.md
    Intermediate files: temp/my_chain_config_20250131_12345/input_document_step_01_dialogue.md, etc.
    Final output copy: temp/my_chain_config_20250131_12345/final_output_final_output.md

Requirements:
    - prompt_runner.py must be installed and available in your system PATH
    - All prompt JSON files must exist
    - Input file must exist
    - OpenRouter API key must be set (OPENROUTER_API_KEY)

File Organization:
    All temporary files, logs, and intermediate outputs are stored in the same
    temporary directory (temp/config_filename_date_pid/) for easy management and
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
        
        # Exit with appropriate code (console already shows final report)
        if success:
            return 0
        else:
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
    