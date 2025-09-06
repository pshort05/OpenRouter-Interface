#!/usr/bin/env python3
"""
API Client Module

Handles OpenRouter API communication for prompt runner.
"""

import logging
import time
from typing import Any

import requests

from .config_manager import ConfigManager
from .file_handler import FileHandler


class PromptAPIClient:
    """Handles OpenRouter API communication for prompt runner (preserves all AI commentary)."""
    
    def __init__(self, config: ConfigManager):
        """Initialize API client with configuration."""
        self.config = config
        self.api_key = config.get_api_key()
    
    def call_api(self, prompt: str) -> str:
        """
        Make API call to OpenRouter without removing AI commentary.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Raw API response (preserves all commentary)
        """
        url = self.config.get('api_base_url') + "/chat/completions"
        
        headers = {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-repo',
            'X-Title': 'OpenRouter Prompt Runner'
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
        
        logging.info("Making API call to OpenRouter")
        logging.info("Model: " + str(self.config.get('model')))
        logging.info("Temperature: " + str(self.config.get('temperature', 0.8)))
        logging.info("Max tokens: " + str(self.config.get('max_tokens', 10000)))
        logging.debug("Prompt length: " + str(len(prompt)) + " characters")
        logging.debug("API URL: " + url)
        
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
            
            logging.debug("HTTP response status: " + str(response.status_code))
            
            result = response.json()
            
            if 'error' in result:
                logging.error("API returned error: " + str(result['error']))
                raise Exception("API Error: " + str(result['error']))
            
            raw_content = result['choices'][0]['message']['content']
            
            logging.info("API call completed in " + "{:.2f}".format(elapsed_time) + " seconds")
            logging.info("Response length: " + str(len(raw_content)) + " characters")
            
            # For prompt runner, we preserve ALL content including AI commentary
            logging.info("✅ Preserving all AI commentary for prompt analysis")
            
            return raw_content
            
        except requests.exceptions.Timeout as e:
            logging.error("API request timed out after 30 seconds: " + str(e))
            raise
        except requests.exceptions.ConnectionError as e:
            logging.error("API connection error: " + str(e))
            raise
        except requests.exceptions.HTTPError as e:
            logging.error("API HTTP error " + str(response.status_code) + ": " + str(e))
            raise
        except requests.exceptions.RequestException as e:
            logging.error("API request failed: " + str(e))
            raise
        except (KeyError, IndexError) as e:
            logging.error("Unexpected API response format: " + str(e))
            logging.debug("Response content: " + str(result))
            raise