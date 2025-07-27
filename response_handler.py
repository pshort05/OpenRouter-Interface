#!/usr/bin/env python3
"""
Response Handler Module

Handles response output and file operations.
Updated to output clean responses without metadata formatting.
All tracking information is logged instead of added to output files.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class ResponseHandler:
    """Handles response output and file operations with clean output formatting."""
    
    def __init__(self, output_file: Optional[str] = None):
        """Initialize response handler."""
        self.output_file = Path(output_file) if output_file else None
        
        if self.output_file:
            logging.info(f"Output will be saved to: {self.output_file}")
    
    def stream_response(self, response: str, prompt_file: Path, input_file: Path):
        """
        Stream response to console and optionally to file.
        
        Args:
            response: API response content
            prompt_file: Path to the prompt file used
            input_file: Path to the input file processed
        """
        # Print to console with header for user context
        self._print_response_header(prompt_file, input_file)
        print(response)
        print("\n" + "=" * 80)
        
        # Save to file if specified (clean output only)
        if self.output_file:
            self._save_clean_response(response, prompt_file, input_file)
    
    def _print_response_header(self, prompt_file: Path, input_file: Path):
        """Print response header to console for user context."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "=" * 80)
        print(f"PROMPT RESPONSE")
        print(f"Timestamp: {timestamp}")
        print(f"Prompt: {prompt_file.name}")
        print(f"Input: {input_file.name}")
        print("=" * 80)
    
    def _save_clean_response(self, response: str, prompt_file: Path, input_file: Path):
        """
        Save clean response to output file and log metadata separately.
        
        Args:
            response: API response content
            prompt_file: Path to the prompt file used
            input_file: Path to the input file processed
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Create directory if needed
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine if this is the first write to the file
            file_exists = self.output_file.exists() and self.output_file.stat().st_size > 0
            
            # Save clean response to file
            with open(self.output_file, 'a', encoding='utf-8') as f:
                # Add minimal separator if file already has content
                if file_exists:
                    f.write('\n\n' + '=' * 40 + '\n\n')
                
                # Write only the response content
                f.write(response)
                
                # Ensure file ends with newline
                if not response.endswith('\n'):
                    f.write('\n')
            
            # Log all metadata for tracking purposes
            logging.info(f"Response saved to: {self.output_file}")
            logging.info(f"Response metadata - Prompt: {prompt_file.name}, Input: {input_file.name}, Timestamp: {timestamp}")
            logging.info(f"Response length: {len(response)} characters")
            logging.info(f"Input file: {input_file.absolute()}")
            logging.info(f"Prompt file: {prompt_file.absolute()}")
            
            # Log response statistics
            line_count = response.count('\n') + 1
            word_count = len(response.split())
            logging.info(f"Response statistics - Lines: {line_count}, Words: {word_count}, Characters: {len(response)}")
            
        except Exception as e:
            logging.error(f"Failed to save response to {self.output_file}: {e}")
            raise
    
    def save_response_only(self, response: str, output_path: str, prompt_file: Path = None, input_file: Path = None):
        """
        Save only the response content to a specified file path.
        
        Args:
            response: API response content
            output_path: Path where to save the response
            prompt_file: Optional prompt file for logging
            input_file: Optional input file for logging
        """
        output_file = Path(output_path)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Create directory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write only the response content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response)
                
                # Ensure file ends with newline
                if not response.endswith('\n'):
                    f.write('\n')
            
            # Log metadata for tracking
            logging.info(f"Clean response saved to: {output_file}")
            if prompt_file:
                logging.info(f"Source prompt: {prompt_file.name} ({prompt_file.absolute()})")
            if input_file:
                logging.info(f"Source input: {input_file.name} ({input_file.absolute()})")
            logging.info(f"Save timestamp: {timestamp}")
            logging.info(f"Response length: {len(response)} characters")
            
        except Exception as e:
            logging.error(f"Failed to save response to {output_file}: {e}")
            raise
    
    def create_detailed_report(self, response: str, prompt_file: Path, input_file: Path, report_path: str):
        """
        Create a detailed report with metadata (for when detailed tracking is needed).
        
        Args:
            response: API response content
            prompt_file: Path to the prompt file used
            input_file: Path to the input file processed
            report_path: Path for the detailed report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_file = Path(report_path)
        
        # Create detailed report content
        report_content = f"""# Prompt Processing Report

**Generated:** {timestamp}  
**Prompt File:** `{prompt_file.name}`  
**Input File:** `{input_file.name}`  

## File Paths
- **Prompt:** `{prompt_file.absolute()}`
- **Input:** `{input_file.absolute()}`
- **Report:** `{report_file.absolute()}`

## Statistics
- **Response Length:** {len(response)} characters
- **Response Lines:** {response.count(chr(10)) + 1}
- **Response Words:** {len(response.split())}

## Response Content

{response}

---
*Report generated by OpenRouter Prompt Runner*
"""
        
        try:
            # Create directory if needed
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save detailed report
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logging.info(f"Detailed report saved to: {report_file}")
            
        except Exception as e:
            logging.error(f"Failed to save detailed report to {report_file}: {e}")
            raise