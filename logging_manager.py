#!/usr/bin/env python3
"""
Logging Manager

Handles logging configuration and setup for OpenRouter Text Editor.
"""

import logging
import sys

from config_manager import ConfigManager


class LoggingManager:
    """Handles logging configuration and setup."""
    
    def __init__(self, config: ConfigManager):
        """Initialize logging manager with configuration."""
        self.config = config
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        
        # Configure logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Remove any existing handlers to avoid duplicates
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Determine where to log
        if self.config.get('log_to_file', False):
            # Log to file
            log_file = self.config.get('log_file', 'openrouter_editor.log')
            handler = logging.FileHandler(log_file, encoding='utf-8')
        else:
            # Log to STDOUT (default)
            handler = logging.StreamHandler(sys.stdout)
        
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        
        # Configure root logger
        logging.root.setLevel(log_level)
        logging.root.addHandler(handler)