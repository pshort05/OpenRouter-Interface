#!/usr/bin/env python3
"""
Input Handler Module

Handles input file selection and loading.
"""

import logging
from pathlib import Path
from typing import Optional


class InputFileHandler:
    """Handles input file selection and loading."""
    
    def get_input_file(self) -> Optional[Path]:
        """
        Get input file from user.
        
        Returns:
            Path to input file or None if cancelled
        """
        while True:
            try:
                file_path = input("\nEnter the path to your input file: ").strip()
                
                if not file_path:
                    print("Please enter a file path")
                    continue
                
                # Remove quotes if present
                file_path = file_path.strip('"\'')
                
                input_file = Path(file_path)
                
                if not input_file.exists():
                    print(f"File not found: {input_file}")
                    print("Please check the path and try again")
                    continue
                
                if not input_file.is_file():
                    print(f"Path is not a file: {input_file}")
                    continue
                
                logging.info(f"Selected input file: {input_file.absolute()}")
                return input_file
                
            except KeyboardInterrupt:
                print("\nCancelled by user")
                return None
    
    def load_input_content(self, input_file: Path) -> str:
        """
        Load content from input file.
        
        Args:
            input_file: Path to input file
            
        Returns:
            File content as string
        """
        logging.info(f"Loading content from: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logging.info(f"✓ Loaded {len(content)} characters from {input_file.name}")
            return content
            
        except Exception as e:
            logging.error(f"Failed to load input file {input_file}: {e}")
            raise