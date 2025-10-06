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
    
    def _build_api_payload(self, prompt: str) -> dict:
        """Build API request payload with only explicitly configured parameters."""
        # Required parameters (model and messages are always required)
        data = {
            'model': self.config.get('model'),
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }

        # Core parameters (only include if explicitly configured by user)
        if self.config.is_user_specified('temperature'):
            data['temperature'] = self.config.get('temperature')
        if self.config.is_user_specified('max_tokens'):
            data['max_tokens'] = self.config.get('max_tokens')

        # Advanced sampling controls (only include if specified)
        if self.config.get('top_p') is not None:
            data['top_p'] = self.config.get('top_p')
        if self.config.get('top_k') is not None:
            data['top_k'] = self.config.get('top_k')
        if self.config.get('min_p') is not None:
            data['min_p'] = self.config.get('min_p')
        if self.config.get('seed') is not None:
            data['seed'] = self.config.get('seed')

        # Penalty parameters
        if self.config.get('frequency_penalty') is not None:
            data['frequency_penalty'] = self.config.get('frequency_penalty')
        if self.config.get('presence_penalty') is not None:
            data['presence_penalty'] = self.config.get('presence_penalty')
        if self.config.get('repetition_penalty') is not None:
            data['repetition_penalty'] = self.config.get('repetition_penalty')

        # Response control
        if self.config.get('stream') is not None:
            data['stream'] = self.config.get('stream')
        if self.config.get('response_format') is not None:
            data['response_format'] = self.config.get('response_format')
        if self.config.get('top_logprobs') is not None:
            data['top_logprobs'] = self.config.get('top_logprobs')

        # OpenRouter-specific features
        if self.config.get('models') is not None:
            data['models'] = self.config.get('models')
        if self.config.get('provider') is not None:
            data['provider'] = self.config.get('provider')
        if self.config.get('transforms') is not None:
            data['transforms'] = self.config.get('transforms')
        if self.config.get('usage') is not None:
            data['usage'] = self.config.get('usage')

        # Utility parameters
        if self.config.get('user') is not None:
            data['user'] = self.config.get('user')

        return data

    def _filter_incompatible_parameters(self, data: dict) -> dict:
        """
        Filter out parameters that are incompatible with specific model families.

        Args:
            data: Original API payload

        Returns:
            Filtered API payload with incompatible parameters removed
        """
        model = data.get('model', '').lower()
        filtered_data = data.copy()

        # Google Gemini models have specific parameter restrictions
        if 'google/' in model or 'gemini' in model:
            # Parameters known to be incompatible with Gemini models
            incompatible_params = [
                'user',  # Gemini doesn't support user parameter
                'top_k',  # Gemini uses different sampling approach
                'frequency_penalty',  # Not supported by Gemini
                'presence_penalty',   # Not supported by Gemini
                'repetition_penalty', # Not supported by Gemini
                'top_logprobs',      # Not supported by Gemini
                'seed',              # Not supported by Gemini
                'min_p',             # Not supported by Gemini
                'max_tokens'         # Gemini uses max_output_tokens instead
            ]

            removed_params = []
            gemini_converted_params = []

            # Handle max_tokens conversion for Gemini
            if 'max_tokens' in filtered_data:
                max_tokens_value = filtered_data['max_tokens']
                filtered_data['max_output_tokens'] = max_tokens_value
                del filtered_data['max_tokens']
                gemini_converted_params.append(f"max_tokens → max_output_tokens ({max_tokens_value})")

            # Remove other incompatible parameters
            for param in incompatible_params:
                if param in filtered_data and param != 'max_tokens':  # max_tokens already handled above
                    removed_params.append(f"{param}={filtered_data[param]}")
                    del filtered_data[param]

            if removed_params:
                logging.info(f"Removed parameters incompatible with {model}: {', '.join(removed_params)}")
            if gemini_converted_params:
                logging.info(f"Converted parameters for {model}: {', '.join(gemini_converted_params)}")

        # Claude models (Anthropic) are generally compatible with most parameters
        # OpenAI models are compatible with most parameters
        # Add other model-specific filtering as needed

        return filtered_data

    def _log_api_parameters(self, data: dict) -> None:
        """Log the API parameters being used."""
        # Always log core parameters
        logging.info(f"Model: {data.get('model')}")

        # Log core parameters only if they're included
        core_params = []
        if 'temperature' in data:
            core_params.append(f"Temperature: {data['temperature']}")
        if 'max_tokens' in data:
            core_params.append(f"Max tokens: {data['max_tokens']}")
        if 'max_output_tokens' in data:
            core_params.append(f"Max output tokens: {data['max_output_tokens']}")

        if core_params:
            logging.info(f"Core parameters: {', '.join(core_params)}")

        # Log optional parameters if present
        optional_params = []
        for param in ['top_p', 'top_k', 'min_p', 'seed', 'frequency_penalty',
                     'presence_penalty', 'repetition_penalty', 'stream',
                     'response_format', 'top_logprobs', 'models', 'provider',
                     'transforms', 'usage', 'user', 'max_output_tokens']:
            if param in data:
                optional_params.append(f"{param}={data[param]}")

        if optional_params:
            logging.info(f"Additional parameters: {', '.join(optional_params)}")

        # Log total parameter count
        param_count = len(data) - 2  # Subtract model and messages
        logging.info(f"Sending {param_count} optional parameters to API")

    def call_local_api(self, prompt: str, endpoint: str, model: str, temperature: float = 0.8) -> str:
        """
        Make API call to local LLM endpoint (Ollama, LM Studio, etc.).

        Args:
            prompt: The prompt to send
            endpoint: Local endpoint URL (e.g., http://localhost:11434)
            model: Local model name (e.g., dolphin-mistral)
            temperature: Temperature setting

        Returns:
            Raw API response
        """
        # Detect endpoint type and construct proper URL
        if 'ollama' in endpoint or ':11434' in endpoint:
            # Ollama format
            url = f"{endpoint}/api/generate" if endpoint.endswith('/') else f"{endpoint}/api/generate"
            is_ollama = True
        else:
            # OpenAI-compatible format (LM Studio, Text Gen WebUI, etc.)
            url = f"{endpoint}/v1/chat/completions" if endpoint.endswith('/') else f"{endpoint}/v1/chat/completions"
            is_ollama = False

        logging.info(f"Making API call to local endpoint: {endpoint}")
        logging.info(f"Local model: {model}")
        logging.info(f"Temperature: {temperature}")
        logging.debug(f"Endpoint URL: {url}")
        logging.debug(f"Endpoint type: {'Ollama' if is_ollama else 'OpenAI-compatible'}")

        start_time = time.time()

        try:
            if is_ollama:
                # Ollama API format
                data = {
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': temperature
                    }
                }

                logging.debug("Sending request to Ollama API...")
                response = requests.post(url, json=data, timeout=120)
                response.raise_for_status()

                result = response.json()
                raw_content = result.get('response', '')

            else:
                # OpenAI-compatible API format
                data = {
                    'model': model,
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'temperature': temperature
                }

                headers = {'Content-Type': 'application/json'}

                logging.debug("Sending request to OpenAI-compatible local API...")
                response = requests.post(url, headers=headers, json=data, timeout=120)
                response.raise_for_status()

                result = response.json()
                raw_content = result['choices'][0]['message']['content']

            end_time = time.time()
            elapsed_time = end_time - start_time

            logging.info(f"Local API call completed in {elapsed_time:.2f} seconds")
            logging.info(f"Response length: {len(raw_content)} characters")

            return raw_content

        except requests.exceptions.Timeout as e:
            logging.error(f"Local API request timed out: {e}")
            raise Exception(f"Local endpoint timed out. Make sure {model} is running at {endpoint}")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Local API connection error: {e}")
            raise Exception(f"Cannot connect to {endpoint}. Make sure the server is running.")
        except requests.exceptions.HTTPError as e:
            logging.error(f"Local API HTTP error {response.status_code}: {e}")
            try:
                error_detail = response.json()
                logging.error(f"API error response: {error_detail}")
            except:
                logging.error(f"API error response (raw): {response.text[:500]}")
            raise Exception(f"Local API error: {e}")
        except (KeyError, IndexError) as e:
            logging.error(f"Unexpected local API response format: {e}")
            logging.debug(f"Response content: {result}")
            raise Exception(f"Invalid response format from local endpoint")

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
        
        # Build API data payload with all supported parameters
        data = self._build_api_payload(prompt)

        # Filter out parameters incompatible with the selected model
        data = self._filter_incompatible_parameters(data)

        logging.info("Making API call to OpenRouter")
        self._log_api_parameters(data)
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
            try:
                error_detail = response.json()
                logging.error("API error response: " + str(error_detail))
            except:
                logging.error("API error response (raw): " + response.text[:500])
            logging.error("Request payload sent to API: " + str(data))
            raise
        except requests.exceptions.RequestException as e:
            logging.error("API request failed: " + str(e))
            raise
        except (KeyError, IndexError) as e:
            logging.error("Unexpected API response format: " + str(e))
            logging.debug("Response content: " + str(result))
            raise