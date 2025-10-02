#!/usr/bin/env python3
"""
Console Output Manager for Prompt Chain Runner

Manages clean console output with colored status indicators.
"""

from pathlib import Path


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

    def print_file_start(self, file_name: str, file_size: str):
        """Print the file processing start message with name and size."""
        print(f"Working on file {file_name} size: {file_size}\n")

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