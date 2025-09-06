#!/usr/bin/env python3
"""
Response Handler Module

Handles response output and file operations.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class ResponseHandler:
    """Handles response output and file operations."""
    
    def __init__(self, output_file: Optional[str] = None):
        """Initialize response handler."""
        self.output_file = Path(output_file) if output_file else None
        
        if self.output_file:
            logging.info(f"Output will be appended to: {self.output_file}")
    
    def stream_response(self, response: str, prompt_file: Path, input_file: Path):
        """
        Stream response to console and optionally to file.
        
        Args:
            response: API response content
            prompt_file: Path to the prompt file used
            input_file: Path to the input file processed
        """
        # Print to console
        self._print_response_header(prompt_file, input_file)
        print(response)
        print("\n" + "=" * 80)
        
        # Save to file if specified
        if self.output_file:
            self._append_to_file(response, prompt_file, input_file)
    
    def _print_response_header(self, prompt_file: Path, input_file: Path):
        """Print response header to console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "=" * 80)
        print(f"PROMPT RESPONSE")
        print(f"Timestamp: {timestamp}")
        print(f"Prompt: {prompt_file.name}")
        print(f"Input: {input_file.name}")
        print("=" * 80)
    
    def _append_to_file(self, response: str, prompt_file: Path, input_file: Path):
        """
        Append response to output file in markdown format.
        
        Args:
            response: API response content
            prompt_file: Path to the prompt file used
            input_file: Path to the input file processed
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create markdown entry
        markdown_entry = f"""
## Prompt Response - {timestamp}

**Prompt File:** `{prompt_file.name}`  
**Input File:** `{input_file.name}`  
**Timestamp:** {timestamp}

---

{response}

---

"""
        
        try:
            # Create directory if needed
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to file
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(markdown_entry)
            
            logging.info(f"✓ Response appended to {self.output_file}")
            
        except Exception as e:
            logging.error(f"Failed to append to output file {self.output_file}: {e}")