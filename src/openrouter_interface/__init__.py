"""
OpenRouter Interface - A comprehensive tool for executing JSON prompts using OpenRouter API.

This package provides:
- CLI interface for batch and interactive processing
- Web interface for user-friendly interaction  
- Prompt chain execution for multi-step workflows
- Book generation utilities
- Comprehensive configuration and logging
"""

__version__ = "1.0.0"
__author__ = "OpenRouter Interface Team"

# Core modules
from .prompt_runner import PromptRunner
from .config_manager import ConfigManager
from .logging_manager import LoggingManager

# API clients
from .prompt_runner_api_client import PromptAPIClient
from .api_client import APIClient

# Handlers
from .prompt_handler import PromptLoader, PromptProcessor
from .input_handler import InputFileHandler
from .response_handler import ResponseHandler
from .file_handler import FileHandler

# Utilities
from .prompt_scanner import PromptScanner

__all__ = [
    "PromptRunner",
    "ConfigManager", 
    "LoggingManager",
    "PromptAPIClient",
    "APIClient",
    "PromptLoader",
    "PromptProcessor", 
    "InputFileHandler",
    "ResponseHandler",
    "FileHandler",
    "PromptScanner",
]