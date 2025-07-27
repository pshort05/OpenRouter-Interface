#!/usr/bin/env python3
"""
Logging Manager

Handles logging configuration and setup for OpenRouter Text Editor.
Supports appending to existing log files for batch processing.
"""

import logging
import sys
from pathlib import Path

from config_manager import ConfigManager


class LoggingManager:
    """Handles logging configuration and setup."""
    
    def __init__(self, config: ConfigManager):
        """Initialize logging manager with configuration."""
        self.config = config
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration with append support for batch processing."""
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
            # Log to file with append mode for batch processing
            log_file = self.config.get('log_file', 'prompt_runner.log')
            log_path = Path(log_file)
            
            # Create parent directory if it doesn't exist
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use append mode ('a') instead of write mode ('w')
            handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            
            # Add a session separator for batch processing clarity
            if log_path.exists() and log_path.stat().st_size > 0:
                # Add separator if file already has content
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write('\n' + '='*80 + '\n')
                    f.write('NEW SESSION STARTED\n')
                    f.write('='*80 + '\n')
            
            logging.info(f"Logging to file: {log_path.absolute()} (append mode)")
        else:
            # Log to STDOUT (default)
            handler = logging.StreamHandler(sys.stdout)
        
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        
        # Configure root logger
        logging.root.setLevel(log_level)
        logging.root.addHandler(handler)