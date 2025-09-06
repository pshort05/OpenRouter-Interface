#!/usr/bin/env python3
"""
Prompt Scanner Module

Handles scanning for JSON prompt files and user selection.
"""

import logging
from pathlib import Path
from typing import List, Optional


class PromptScanner:
    """Scans directory for JSON prompt files."""
    
    def __init__(self, directory: str = "."):
        """Initialize prompt scanner."""
        self.directory = Path(directory)
        
    def scan_for_prompts(self) -> List[Path]:
        """
        Scan directory for JSON files.
        
        Returns:
            List of JSON file paths
        """
        logging.info(f"Scanning directory: {self.directory.absolute()}")
        
        json_files = list(self.directory.glob("*.json"))
        json_files.sort(key=lambda x: x.name.lower())  # Sort alphabetically
        
        logging.info(f"Found {len(json_files)} JSON files")
        
        return json_files
    
    def display_prompt_menu(self, json_files: List[Path]) -> Optional[int]:
        """
        Display menu of JSON files and get user selection.
        
        Args:
            json_files: List of JSON file paths
            
        Returns:
            Selected index (0-based) or None if cancelled
        """
        if not json_files:
            print("No JSON files found in the current directory.")
            return None
        
        print("\nAvailable JSON prompt files:")
        print("=" * 40)
        
        for i, json_file in enumerate(json_files, 1):
            file_size = json_file.stat().st_size if json_file.exists() else 0
            print(f"{i:2d}. {json_file.name} ({file_size} bytes)")
        
        print("=" * 40)
        
        while True:
            try:
                choice = input(f"\nSelect a prompt file (1-{len(json_files)}) or 'q' to quit: ").strip()
                
                if choice.lower() in ['q', 'quit', 'exit']:
                    return None
                
                selection = int(choice)
                if 1 <= selection <= len(json_files):
                    return selection - 1  # Convert to 0-based index
                else:
                    print(f"Please enter a number between 1 and {len(json_files)}")
                    
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nCancelled by user")
                return None