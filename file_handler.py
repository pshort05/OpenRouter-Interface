#!/usr/bin/env python3
"""
File Handler Module

Handles file operations for OpenRouter Text Editor.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from config_manager import ConfigManager


class FileHandler:
    """Handles file operations for the OpenRouter Text Editor."""
    
    def __init__(self, config: ConfigManager):
        """Initialize file handler with configuration."""
        self.config = config
    
    def save_payload(self, payload: Dict[str, Any]):
        """
        Save API payload to file for debugging purposes.
        
        Args:
            payload: API request payload to save
        """
        payload_file = self.config.get('payload_file', 'openrouter_editor.payload.json')
        payload_path = Path(payload_file)
        
        try:
            # Create parent directory if it doesn't exist
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save payload with pretty formatting
            with open(payload_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            
            logging.debug(f"Payload saved to: {payload_path}")
            
        except Exception as e:
            logging.warning(f"Failed to save payload to {payload_path}: {e}")
    
    def save_text_file(self, content: str, file_path: str):
        """
        Save text content to file.
        
        Args:
            content: Text content to save
            file_path: Path where to save the file
        """
        output_path = Path(file_path)
        
        try:
            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logging.info(f"Content saved to: {output_path}")
            
        except Exception as e:
            logging.error(f"Failed to save content to {output_path}: {e}")
            raise