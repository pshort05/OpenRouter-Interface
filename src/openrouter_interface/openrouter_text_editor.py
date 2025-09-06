#!/usr/bin/env python3
"""
OpenRouter Text Editor

A Python program that uses the OpenRouter API to edit text files based on
configuration and action specifications.

Usage:
    python openrouter_editor.py [-c config.yaml]
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

import requests
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
        
        # Default configuration
        default_config = {
            'input_file': 'input.md',
            'output_file': 'output.md',
            'action_file': 'action.json',
            'payload_file': 'openrouter_editor.payload.json',
            'commentary_file': 'ai_commentary.txt',
            'log_level': 'INFO',
            'log_to_file': False,
            'log_file': 'openrouter_editor.log',
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.8,
            'max_tokens': 10000
        }
        
        if config_path.exists():
            logging.info(f"Loading configuration from {self.config_file}")
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
            default_config.update(user_config)
        else:
            logging.info(f"Configuration file {self.config_file} not found, using defaults")
            
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


class FileHandler:
    """Handles file I/O operations."""
    
    def __init__(self, config: ConfigManager):
        """Initialize file handler with configuration."""
        self.config = config
    
    def load_input_text(self) -> str:
        """Load input text from markdown file."""
        input_file = Path(self.config.get('input_file'))
        
        logging.debug(f"Looking for input file: {input_file.absolute()}")
        
        if not input_file.exists():
            logging.error(f"Input file '{input_file}' not found at {input_file.absolute()}")
            raise FileNotFoundError(f"Input file '{input_file}' not found")
        
        logging.info(f"Loading input text from {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            logging.debug(f"Successfully loaded {len(content)} characters from input file")
            return content
        except Exception as e:
            logging.error(f"Failed to read input file '{input_file}': {e}")
            raise
    
    def load_action(self) -> Dict[str, Any]:
        """Load action configuration from JSON file."""
        action_file = Path(self.config.get('action_file'))
        
        logging.debug(f"Looking for action file: {action_file.absolute()}")
        
        if not action_file.exists():
            logging.error(f"Action file '{action_file}' not found at {action_file.absolute()}")
            raise FileNotFoundError(f"Action file '{action_file}' not found")
        
        logging.info(f"Loading action from {action_file}")
        
        try:
            with open(action_file, 'r', encoding='utf-8') as f:
                action = json.load(f)
            logging.debug(f"Loaded action configuration: {action}")
            return action
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON in action file '{action_file}': {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to read action file '{action_file}': {e}")
            raise
    
    def save_output(self, text: str):
        """Save the edited text to output file."""
        output_file = Path(self.config.get('output_file'))
        
        logging.info(f"Preparing to save output to {output_file}")
        logging.debug(f"Output file absolute path: {output_file.absolute()}")
        
        # Create output directory if it doesn't exist
        if output_file.parent != Path('.'):
            logging.debug(f"Creating output directory: {output_file.parent}")
            output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            logging.info(f"Successfully saved {len(text)} characters to {output_file}")
        except Exception as e:
            logging.error(f"Failed to save output file '{output_file}': {e}")
            raise
    
    def save_payload(self, payload: Dict[str, Any]):
        """Save the API payload to JSON file."""
        payload_file = Path(self.config.get('payload_file'))
        
        logging.info(f"Saving API payload to {payload_file}")
        logging.debug(f"Payload file absolute path: {payload_file.absolute()}")
        
        # Create payload directory if it doesn't exist
        if payload_file.parent != Path('.'):
            logging.debug(f"Creating payload directory: {payload_file.parent}")
            payload_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(payload_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully saved API payload to {payload_file}")
        except Exception as e:
            logging.error(f"Failed to save payload file '{payload_file}': {e}")
            raise


class PromptBuilder:
    """Handles prompt creation for API calls."""
    
    def create_prompt(self, input_text: str, action: Dict[str, Any]) -> str:
        """Create prompt for the OpenRouter API based on action configuration."""
        action_type = action.get('type', 'edit')
        instruction = action.get('instruction', 'Edit the following text:')
        
        logging.info(f"Creating prompt for action type: {action_type}")
        logging.debug(f"Full action configuration: {action}")
        
        # Start with the main instruction
        prompt = f"{instruction}\n\n"
        
        # Add action-specific instructions
        if action_type == 'edit':
            prompt += "Please edit the following markdown text"
        elif action_type == 'rewrite':
            prompt += "Please rewrite the following markdown text"
        elif action_type == 'summarize':
            prompt += "Please summarize the following markdown text"
        elif action_type == 'translate':
            target_language = action.get('target_language', 'English')
            logging.info(f"Translation target language: {target_language}")
            prompt += f"Please translate the following markdown text to {target_language}"
        else:
            # Custom action type
            logging.info(f"Using custom action type: {action_type}")
            prompt += "Please process the following markdown text"
        
        # Add any additional context from action.json
        if 'additional_context' in action:
            logging.debug(f"Adding additional context: {action['additional_context']}")
            prompt += f" with the following additional context: {action['additional_context']}"
        
        # Add any style or tone instructions
        if 'style' in action:
            logging.debug(f"Adding style instruction: {action['style']}")
            prompt += f" using a {action['style']} style"
        
        if 'tone' in action:
            logging.debug(f"Adding tone instruction: {action['tone']}")
            prompt += f" with a {action['tone']} tone"
        
        # Add any specific requirements
        if 'requirements' in action:
            requirements = action['requirements']
            if isinstance(requirements, list):
                requirements_text = "\n".join([f"- {req}" for req in requirements])
            else:
                requirements_text = str(requirements)
            logging.debug(f"Adding requirements: {requirements}")
            prompt += f"\n\nSpecific requirements:\n{requirements_text}"
        
        # Add any constraints
        if 'constraints' in action:
            constraints = action['constraints']
            if isinstance(constraints, list):
                constraints_text = "\n".join([f"- {constraint}" for constraint in constraints])
            else:
                constraints_text = str(constraints)
            logging.debug(f"Adding constraints: {constraints}")
            prompt += f"\n\nConstraints:\n{constraints_text}"
        
        # Add any examples if provided
        if 'examples' in action:
            examples = action['examples']
            logging.debug(f"Adding examples: {examples}")
            prompt += f"\n\nExamples:\n{examples}"
        
        # Add any output format specifications
        if 'output_format' in action:
            output_format = action['output_format']
            logging.debug(f"Adding output format: {output_format}")
            prompt += f"\n\nOutput format: {output_format}"
        
        # Add target audience if specified
        if 'target_audience' in action:
            target_audience = action['target_audience']
            logging.debug(f"Adding target audience: {target_audience}")
            prompt += f"\n\nTarget audience: {target_audience}"
        
        # Add any other custom fields from action.json (excluding already processed ones)
        processed_fields = {
            'type', 'instruction', 'additional_context', 'target_language', 
            'style', 'tone', 'requirements', 'constraints', 'examples', 
            'output_format', 'target_audience'
        }
        
        custom_fields = {k: v for k, v in action.items() if k not in processed_fields}
        if custom_fields:
            logging.debug(f"Adding custom fields: {custom_fields}")
            prompt += "\n\nAdditional instructions:"
            for key, value in custom_fields.items():
                prompt += f"\n- {key.replace('_', ' ').title()}: {value}"
        
        # Finally, add the actual text to process
        prompt += f"\n\nText to process:\n\n{input_text}"
        
        logging.debug(f"Final prompt length: {len(prompt)} characters")
        logging.debug(f"Action fields included in prompt: {list(action.keys())}")
        
        return prompt


class APIClient:
    """Handles OpenRouter API communication."""
    
    def __init__(self, config: ConfigManager):
        """Initialize API client with configuration."""
        self.config = config
        self.api_key = config.get_api_key()
    
    def _process_api_response(self, content: str) -> str:
        """Process API response to remove AI commentary and log it separately."""
        original_content = content.strip()
        processed_content = original_content
        removed_sections = []
        
        # List of common AI response prefixes to remove
        prefixes_to_remove = [
            "Here's the edited version with improvements to flow, dialogue, and narrative structure:",
            "Here's the edited version:",
            "Here's the improved text:",
            "Here's the rewritten text:",
            "Here's the revised version:",
            "Here is the edited text:",
            "Here is the improved version:",
            "Here's the text with improvements:",
            "Here's your edited text:",
            "Here's the enhanced version:",
            "I'll help you edit this text.",
            "I've made several improvements:",
            "I've edited the text to improve:",
            "The edited version is below:",
            "Here's a revised version:",
        ]
        
        # Remove prefix if found
        for prefix in prefixes_to_remove:
            if processed_content.startswith(prefix):
                removed_sections.append(f"PREFIX: {prefix}")
                logging.info(f"Removed AI response prefix: '{prefix}'")
                processed_content = processed_content[len(prefix):].lstrip()
                break
        
        # Look for and remove summary/commentary sections at the end
        summary_markers = [
            "Key improvements made:",
            "Key changes made:",
            "Summary of changes:",
            "Changes made:",
            "Improvements include:",
            "Main improvements:",
            "Notable changes:",
            "Key edits:",
            "Summary of edits:",
            "Primary changes:",
            "The main changes include:",
            "I've made the following improvements:",
            "Notable improvements:",
            "Key modifications:",
            "Primary edits:",
            "Main edits:",
            "Significant changes:",
            "Important changes:",
        ]
        
        for marker in summary_markers:
            marker_pos = processed_content.rfind(marker)
            if marker_pos != -1:
                # Extract the summary for logging
                summary_section = processed_content[marker_pos:].strip()
                removed_sections.append(f"SUMMARY: {summary_section}")
                
                # Log the summary that was removed
                logging.info(f"Removed AI response summary starting with: '{marker}'")
                
                # Remove the summary from the content
                processed_content = processed_content[:marker_pos].rstrip()
                break
        
    def call_api(self, prompt: str) -> str:
        """Make API call to OpenRouter."""
        url = f"{self.config.get('api_base_url')}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-repo',  # Optional: for tracking
            'X-Title': 'OpenRouter Text Editor'  # Optional: for tracking
        }
        
        data = {
            'model': self.config.get('model'),
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': self.config.get('temperature', 0.8),
            'max_tokens': self.config.get('max_tokens', 10000)
        }
        
        logging.info(f"Making API call to OpenRouter")
        logging.info(f"Model: {self.config.get('model')}")
        logging.info(f"Temperature: {self.config.get('temperature', 0.8)}")
        logging.info(f"Max tokens: {self.config.get('max_tokens', 10000)}")
        logging.debug(f"Prompt length: {len(prompt)} characters")
        logging.debug(f"API URL: {url}")
        
        # Save payload before making the call
        file_handler = FileHandler(self.config)
        file_handler.save_payload(data)
        
        start_time = time.time()
        
        try:
            logging.debug("Sending request to OpenRouter API...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            logging.debug(f"HTTP response status: {response.status_code}")
            
            result = response.json()
            
            if 'error' in result:
                logging.error(f"API returned error: {result['error']}")
                raise Exception(f"API Error: {result['error']}")
            
            raw_content = result['choices'][0]['message']['content']
            
            logging.info(f"API call completed in {elapsed_time:.2f} seconds")
            logging.info(f"Raw response length: {len(raw_content)} characters")
            
            # Check for and remove common AI response prefixes
            processed_content = self._process_api_response(raw_content)
            
            if processed_content != raw_content:
                logging.info(f"Processed response length: {len(processed_content)} characters")
            
            return processed_content
            
        except requests.exceptions.Timeout as e:
            logging.error(f"API request timed out after 30 seconds: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logging.error(f"API connection error: {e}")
            raise
        except requests.exceptions.HTTPError as e:
            logging.error(f"API HTTP error {response.status_code}: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            raise
        except (KeyError, IndexError) as e:
            logging.error(f"Unexpected API response format: {e}")
            logging.debug(f"Response content: {result}")
            raise


class OpenRouterEditor:
    """Main orchestrator class for text editing operations."""
    
    def __init__(self, config_file: str = None):
        """Initialize the editor with configuration."""
        logging.info("Initializing OpenRouter Text Editor")
        
        # Initialize components
        self.config = ConfigManager(config_file)
        self.logging_manager = LoggingManager(self.config)
        self.file_handler = FileHandler(self.config)
        self.prompt_builder = PromptBuilder()
        self.api_client = APIClient(self.config)
        
        logging.info(f"Configuration loaded from: {config_file or 'openrouter_editor.yaml'}")
        logging.debug(f"Active configuration: {self.config.config}")
    
    def process(self):
        """Main processing method."""
        logging.info("=" * 60)
        logging.info("Starting OpenRouter Text Editor processing")
        logging.info("=" * 60)
        
        try:
            # Load input text
            logging.info("Step 1: Loading input text")
            input_text = self.file_handler.load_input_text()
            logging.info(f"✓ Input text loaded: {len(input_text)} characters")
            
            # Load action configuration
            logging.info("Step 2: Loading action configuration")
            action = self.file_handler.load_action()
            action_type = action.get('type', 'edit')
            logging.info(f"✓ Action loaded: {action_type}")
            
            # Create prompt
            logging.info("Step 3: Creating API prompt")
            prompt = self.prompt_builder.create_prompt(input_text, action)
            logging.info(f"✓ Prompt created: {len(prompt)} characters")
            
            # Call OpenRouter API
            logging.info("Step 4: Calling OpenRouter API")
            result = self.api_client.call_api(prompt)
            logging.info(f"✓ API call successful, received {len(result)} characters")
            
            # Save output
            logging.info("Step 5: Saving output")
            self.file_handler.save_output(result)
            logging.info("✓ Output saved successfully")
            
            logging.info("=" * 60)
            logging.info("Text editing completed successfully!")
            logging.info("=" * 60)
            
        except Exception as e:
            logging.error("=" * 60)
            logging.error(f"✗ Error during processing: {e}")
            logging.error("=" * 60)
            logging.debug("Full error details:", exc_info=True)
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Edit text using OpenRouter API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python openrouter_editor.py
    python openrouter_editor.py -c my_config.yaml
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to YAML configuration file (default: openrouter_editor.yaml)',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        editor = OpenRouterEditor(args.config)
        editor.process()
    except Exception as e:
        logging.error(f"Failed to initialize editor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
