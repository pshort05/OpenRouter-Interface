
#!/usr/bin/env python3
"""
File Handler

Handles file I/O operations for OpenRouter Text Editor.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from config_manager import ConfigManager


class FileHandler:
    """Handles file I/O operations."""
    
    def __init__(self, config: ConfigManager):
        """Initialize file handler with configuration."""
        self.config = config
    
    def load_input_text(self) -> str:
        """Load input text from markdown file."""
        input_file = Path(self.config.get('input_file'))
        
        logging.debug("Looking for input file: " + str(input_file.absolute()))
        
        if not input_file.exists():
            logging.error("Input file '" + str(input_file) + "' not found at " + str(input_file.absolute()))
            raise FileNotFoundError("Input file '" + str(input_file) + "' not found")
        
        logging.info("Loading input text from " + str(input_file))
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            logging.debug("Successfully loaded " + str(len(content)) + " characters from input file")
            return content
        except Exception as e:
            logging.error("Failed to read input file '" + str(input_file) + "': " + str(e))
            raise
    
    def load_action(self) -> Dict[str, Any]:
        """Load action configuration from JSON file."""
        action_file = Path(self.config.get('action_file'))
        
        logging.debug("Looking for action file: " + str(action_file.absolute()))
        
        if not action_file.exists():
            logging.error("Action file '" + str(action_file) + "' not found at " + str(action_file.absolute()))
            raise FileNotFoundError("Action file '" + str(action_file) + "' not found")
        
        logging.info("Loading action from " + str(action_file))
        
        try:
            with open(action_file, 'r', encoding='utf-8') as f:
                action = json.load(f)
            logging.debug("Loaded action configuration: " + str(action))
            return action
        except json.JSONDecodeError as e:
            logging.error("Failed to parse JSON in action file '" + str(action_file) + "': " + str(e))
            raise
        except Exception as e:
            logging.error("Failed to read action file '" + str(action_file) + "': " + str(e))
            raise
    
    def save_output(self, text: str):
        """Save the edited text to output file."""
        output_file = Path(self.config.get('output_file'))
        
        logging.info("Preparing to save output to " + str(output_file))
        logging.debug("Output file absolute path: " + str(output_file.absolute()))
        
        # Create output directory if it doesn't exist
        if output_file.parent != Path('.'):
            logging.debug("Creating output directory: " + str(output_file.parent))
            output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            logging.info("Successfully saved " + str(len(text)) + " characters to " + str(output_file))
        except Exception as e:
            logging.error("Failed to save output file '" + str(output_file) + "': " + str(e))
            raise
    
    def save_payload(self, payload: Dict[str, Any]):
        """Save the API payload to JSON file."""
        payload_file = Path(self.config.get('payload_file'))
        
        logging.info("Saving API payload to " + str(payload_file))
        logging.debug("Payload file absolute path: " + str(payload_file.absolute()))
        
        # Create payload directory if it doesn't exist
        if payload_file.parent != Path('.'):
            logging.debug("Creating payload directory: " + str(payload_file.parent))
            payload_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(payload_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            logging.info("Successfully saved API payload to " + str(payload_file))
        except Exception as e:
            logging.error("Failed to save payload file '" + str(payload_file) + "': " + str(e))
            raise