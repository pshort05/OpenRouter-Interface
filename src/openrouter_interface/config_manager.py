#!/usr/bin/env python3
"""
Configuration Manager

Handles configuration loading and management for OpenRouter Text Editor.
Updated with higher default max_tokens for better prompt processing.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

import yaml


class ConfigManager:
    """Handles configuration loading and management."""
    
    def __init__(self, config_file: str = None):
        """Initialize configuration manager."""
        self.config_file = config_file or "openrouter_editor.yaml"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_path = Path(self.config_file)
        
        # Default configuration with updated max_tokens
        default_config = {
            'input_file': 'input.md',
            'output_file': 'output.md',
            'action_file': 'action.json',
            'payload_file': 'openrouter_editor.payload.json',
            'log_level': 'INFO',
            'log_to_file': False,
            'log_file': 'openrouter_editor.log',
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.8,
            'max_tokens': 25000,  # Updated from 10000 to 25000
            'enable_compliance_check': True,
            'compliance_output_file': 'compliance_analysis.md',
            'enable_chunking': False,
            'chunk_size': 1000,
            'chunk_identifier': 'ch'
        }
        
        if config_path.exists():
            logging.info("Loading configuration from " + self.config_file)
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
            default_config.update(user_config)
        else:
            logging.info("Configuration file " + self.config_file + " not found, using defaults")
            
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def get_api_key(self) -> str:
        """Get API key from environment variable or config file."""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            api_key = self.config.get('api_key')
        
        if not api_key:
            raise ValueError(
                "API key not found. Please set OPENROUTER_API_KEY environment "
                "variable or add 'api_key' to your configuration file."
            )
        
        logging.info("API key loaded successfully")
        return api_key