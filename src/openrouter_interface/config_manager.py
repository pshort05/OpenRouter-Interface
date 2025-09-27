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
        
        # Default configuration with all API parameters
        default_config = {
            # Core application settings
            'input_file': 'input.md',
            'output_file': 'output.md',
            'action_file': 'action.json',
            'payload_file': 'openrouter_editor.payload.json',
            'log_level': 'INFO',
            'log_to_file': False,
            'log_file': 'openrouter_editor.log',
            'enable_compliance_check': True,
            'compliance_output_file': 'compliance_analysis.md',
            'enable_chunking': False,
            'chunk_size': 1000,
            'chunk_identifier': 'ch',

            # Core API parameters (always included)
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.8,
            'max_tokens': 25000,

            # Advanced sampling controls (optional - only sent if specified)
            # 'top_p': None,              # (double, range: (0, 1]) - Top-p nucleus sampling
            # 'top_k': None,              # (integer, range: [1, ∞)) - Top-k sampling
            # 'min_p': None,              # (double, range: [0, 1]) - Minimum probability threshold
            # 'seed': None,               # (integer) - Deterministic output control

            # Penalty parameters (optional)
            # 'frequency_penalty': None,   # (double, range: [-2, 2]) - Reduce repetition by frequency
            # 'presence_penalty': None,    # (double, range: [-2, 2]) - Reduce repetition by presence
            # 'repetition_penalty': None,  # (double, range: (0, 2]) - Alternative repetition control

            # Response control (optional)
            # 'stream': None,             # (boolean) - Enable streaming responses
            # 'response_format': None,    # (object) - Force structured JSON output
            # 'top_logprobs': None,       # (integer) - Return token probabilities

            # OpenRouter-specific features (optional)
            # 'models': None,             # (array) - Fallback model list
            # 'provider': None,           # (object) - Provider routing preferences
            # 'transforms': None,         # (array) - OpenRouter prompt transformations
            # 'usage': None,              # (object) - Get detailed usage statistics

            # Utility parameters (optional)
            # 'user': None,               # (string) - User identifier for tracking
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