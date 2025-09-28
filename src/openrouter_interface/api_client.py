#!/usr/bin/env python3
"""
API Client

Handles OpenRouter API communication for OpenRouter Text Editor.
"""

import json
import logging
import re
import time
from typing import Dict, Any

import requests

from .config_manager import ConfigManager
from .file_handler import FileHandler


class APIClient:
    """Handles OpenRouter API communication."""
    
    def __init__(self, config: ConfigManager):
        """Initialize API client with configuration."""
        self.config = config
        self.api_key = config.get_api_key()
    
    def _build_api_payload(self, prompt: str) -> dict:
        """Build API request payload with all configured parameters."""
        # Core required parameters
        data = {
            'model': self.config.get('model'),
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': self.config.get('temperature', 0.8),
            'max_tokens': self.config.get('max_tokens', 25000)
        }

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

    def _process_streaming_response(self, response) -> str:
        """Process a streaming SSE response and extract the content."""
        content_parts = []

        try:
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                # Handle different SSE line formats
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                elif line.startswith('data:'):
                    data_str = line[5:]  # Remove 'data:' prefix
                else:
                    continue

                data_str = data_str.strip()

                if data_str == '[DONE]':
                    break

                if not data_str:
                    continue

                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            content_parts.append(delta['content'])
                except json.JSONDecodeError as e:
                    logging.debug(f"Skipping malformed JSON chunk: {data_str[:100]}...")
                    continue
                except Exception as e:
                    logging.debug(f"Error processing streaming chunk: {e}")
                    continue

        except Exception as e:
            logging.error(f"Error processing streaming response: {e}")
            # Fallback: try to parse as regular JSON
            try:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            except:
                pass
            raise Exception(f"Failed to process streaming response: {e}")

        return ''.join(content_parts)

    def _log_api_parameters(self, data: dict) -> None:
        """Log the API parameters being used."""
        # Always log core parameters
        logging.info(f"Model: {data.get('model')}")
        logging.info(f"Temperature: {data.get('temperature')}")
        logging.info(f"Max tokens: {data.get('max_tokens')}")

        # Log optional parameters if present
        optional_params = []
        for param in ['top_p', 'top_k', 'min_p', 'seed', 'frequency_penalty',
                     'presence_penalty', 'repetition_penalty', 'stream',
                     'response_format', 'top_logprobs', 'models', 'provider',
                     'transforms', 'usage', 'user']:
            if param in data:
                optional_params.append(f"{param}={data[param]}")

        if optional_params:
            logging.info(f"Additional parameters: {', '.join(optional_params)}")

    def _process_api_response(self, content: str) -> str:
        """Process API response to remove AI commentary and log it to console."""
        original_content = content.strip()
        processed_content = original_content
        
        # Remove editorial notes at the beginning (like the one in your example)
        editorial_patterns = [
            r'^\*\*Editorial Note:\*\*.*?\n\n',
            r'^\*Editorial Note:\*.*?\n\n',
            r'^\[Editorial Note\].*?\n\n',
            r'^\*\*Note:\*\*.*?\n\n',
            r'^\*Note:\*.*?\n\n',
            r'^\[Note\].*?\n\n',
        ]
        
        for pattern in editorial_patterns:
            match = re.search(pattern, processed_content, re.DOTALL | re.IGNORECASE)
            if match:
                removed_text = match.group(0).strip()
                logging.info("🤖 AI COMMENTARY - Editorial note removed: " + removed_text[:100] + "...")
                processed_content = re.sub(pattern, '', processed_content, flags=re.DOTALL | re.IGNORECASE)
                break
        
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
        
        # Remove prefix if found and log it
        for prefix in prefixes_to_remove:
            if processed_content.startswith(prefix):
                logging.info("🤖 AI COMMENTARY - Prefix: " + prefix)
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
            "**Key Edits Made:**",
            "**Changes Made:**",
            "**Summary:**",
            "**Improvements:**",
        ]
        
        # Find the last occurrence of any summary marker
        last_summary_pos = -1
        found_marker = None
        
        for marker in summary_markers:
            marker_pos = processed_content.rfind(marker)
            if marker_pos > last_summary_pos:
                last_summary_pos = marker_pos
                found_marker = marker
        
        # If we found a summary section, remove it and log it
        if last_summary_pos != -1:
            summary_section = processed_content[last_summary_pos:].strip()
            
            # Log the summary to console (truncated for readability)
            logging.info("🤖 AI COMMENTARY - Summary section removed:")
            summary_lines = summary_section.split('\n')[:10]  # Show first 10 lines
            for line in summary_lines:
                if line.strip():
                    logging.info("    " + line.strip())
            if len(summary_section.split('\n')) > 10:
                logging.info("    ... (truncated)")
            
            # Remove the summary from the content
            processed_content = processed_content[:last_summary_pos].rstrip()
        
        # Remove any trailing "---" separators that might be left over
        processed_content = re.sub(r'\n---\s*$', '', processed_content)
        
        # Look for obvious commentary at the very end (last 1-2 lines only)
        lines = processed_content.split('\n')
        if len(lines) > 1:
            # Check only the last line or two for commentary patterns
            last_line = lines[-1].strip()
            second_to_last = lines[-2].strip() if len(lines) > 1 else ""
            
            # Check last line for commentary patterns
            if (last_line.startswith('*') and last_line.endswith('*') and len(last_line) > 2) or \
               (last_line.startswith('(') and last_line.endswith(')')) or \
               last_line.startswith('Note:'):
                logging.info("🤖 AI COMMENTARY - End note: " + last_line)
                lines = lines[:-1]  # Remove last line
                processed_content = '\n'.join(lines).rstrip()
            
            # Check second to last line if it looks like commentary
            elif (second_to_last.startswith('*') and second_to_last.endswith('*') and len(second_to_last) > 2) or \
                 (second_to_last.startswith('(') and second_to_last.endswith(')')):
                logging.info("🤖 AI COMMENTARY - End note: " + second_to_last)
                lines = lines[:-2] + lines[-1:]  # Remove second to last line
                processed_content = '\n'.join(lines).rstrip()
        
        # Log processing results
        if processed_content != original_content:
            chars_removed = len(original_content) - len(processed_content)
            logging.info("📝 Removed " + str(chars_removed) + " characters of AI commentary from output")
        else:
            logging.info("✅ No AI commentary detected in response")
        
        return processed_content
    
    def call_api(self, prompt: str) -> str:
        """Make API call to OpenRouter."""
        url = self.config.get('api_base_url') + "/chat/completions"
        
        headers = {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-repo',  # Optional: for tracking
            'X-Title': 'OpenRouter Text Editor'  # Optional: for tracking
        }
        
        # Build API data payload with all supported parameters
        data = self._build_api_payload(prompt)
        
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
            is_streaming = data.get('stream', False)
            logging.debug(f"Streaming mode: {is_streaming}")

            if is_streaming:
                # For streaming requests, we need to handle SSE
                logging.debug("Making streaming request...")
                response = requests.post(url, headers=headers, json=data, timeout=30, stream=True)
            else:
                logging.debug("Making regular request...")
                response = requests.post(url, headers=headers, json=data, timeout=30)

            logging.debug(f"Response status: {response.status_code}")
            logging.debug(f"Response headers: {dict(response.headers)}")
            response.raise_for_status()

            end_time = time.time()
            elapsed_time = end_time - start_time

            logging.debug("HTTP response status: " + str(response.status_code))

            if is_streaming:
                # Process streaming response
                raw_content = self._process_streaming_response(response)
                if not raw_content:
                    raise Exception("Streaming API returned empty content")
            else:
                # Process regular JSON response
                result = response.json()

                if 'error' in result:
                    logging.error("API returned error: " + str(result['error']))
                    raise Exception("API Error: " + str(result['error']))

                raw_content = result['choices'][0]['message']['content']
            
            logging.info("API call completed in " + "{:.2f}".format(elapsed_time) + " seconds")
            logging.info("Raw response length: " + str(len(raw_content)) + " characters")
            
            # Check for and remove common AI response prefixes
            processed_content = self._process_api_response(raw_content)
            
            if processed_content != raw_content:
                logging.info("Processed response length: " + str(len(processed_content)) + " characters")
            
            return processed_content
            
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
        except json.JSONDecodeError as e:
            logging.error("API request failed: " + str(e))
            raise
        except (KeyError, IndexError) as e:
            logging.error("Unexpected API response format: " + str(e))
            logging.debug("Response content: " + str(result))
            raise