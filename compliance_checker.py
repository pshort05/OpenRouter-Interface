#!/usr/bin/env python3
"""
Compliance Checker for OpenRouter Text Editor

A class that analyzes how well the output text conforms to the original
action specifications defined in action.json.

Usage:
    from compliance_checker import ComplianceChecker
    
    config = {'input_file': 'output.md', 'output_file': 'analysis.md'}
    checker = ComplianceChecker(config)
    checker.check_compliance()
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests


class ComplianceChecker:
    """
    Analyzes output text compliance against action specifications.
    
    This class loads the processed output text and the original action.json,
    then uses the OpenRouter API to generate a compliance analysis report.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the compliance checker with configuration.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        self.config = self._merge_with_defaults(config)
        self._validate_config()
        
    def _merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user configuration with default values.
        
        Args:
            user_config: User-provided configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        default_config = {
            'input_file': 'output.md',  # The processed output to analyze
            'output_file': 'analysis.md',  # Where to save the compliance report
            'action_file': 'action.json',  # Original action specifications
            'original_input_file': 'input.md',  # Original unprocessed input
            'payload_file': 'compliance_checker.payload.json',
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.3,  # Lower temperature for more consistent analysis
            'max_tokens': 8000,
            'api_key': None  # Will be retrieved from environment or config
        }
        
        # Merge user config with defaults
        merged_config = default_config.copy()
        merged_config.update(user_config)
        
        return merged_config
    
    def _validate_config(self):
        """Validate that required configuration parameters are present."""
        required_files = ['input_file', 'action_file', 'original_input_file']
        
        for file_key in required_files:
            file_path = Path(self.config[file_key])
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required file '{file_path}' not found for compliance checking"
                )
    
    def _get_api_key(self) -> str:
        """Get API key from environment variable or config."""
        import os
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            api_key = self.config.get('api_key')
        
        if not api_key:
            raise ValueError(
                "API key not found. Please set OPENROUTER_API_KEY environment "
                "variable or add 'api_key' to the configuration."
            )
        
        return api_key
    
    def _load_file_content(self, file_key: str) -> str:
        """
        Load content from a file specified in the configuration.
        
        Args:
            file_key: Configuration key for the file path
            
        Returns:
            File content as string
        """
        file_path = Path(self.config[file_key])
        
        logging.info(f"Loading content from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logging.debug(f"Loaded {len(content)} characters from {file_path}")
            return content
        except Exception as e:
            logging.error(f"Failed to read {file_path}: {e}")
            raise
    
    def _load_action_config(self) -> Dict[str, Any]:
        """
        Load action configuration from JSON file.
        
        Returns:
            Action configuration dictionary
        """
        action_file = Path(self.config['action_file'])
        
        logging.info(f"Loading action configuration from {action_file}")
        
        try:
            with open(action_file, 'r', encoding='utf-8') as f:
                action = json.load(f)
            logging.debug(f"Loaded action configuration: {action}")
            return action
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON in {action_file}: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to read {action_file}: {e}")
            raise
    
    def _create_compliance_prompt(
        self, 
        original_text: str, 
        processed_text: str, 
        action_config: Dict[str, Any]
    ) -> str:
        """
        Create a prompt for compliance analysis.
        
        Args:
            original_text: The original input text
            processed_text: The processed output text to analyze
            action_config: The action configuration that was supposed to be followed
            
        Returns:
            Compliance analysis prompt
        """
        action_type = action_config.get('type', 'edit')
        
        prompt = f"""You are a compliance analyst reviewing whether a text editing task was completed according to specifications.

TASK: Analyze how well the processed text follows the given action specifications.

ACTION SPECIFICATIONS:
- Action Type: {action_type}
"""
        
        # Add all action specifications to the prompt
        for key, value in action_config.items():
            if key != 'type':  # Already included above
                if isinstance(value, list):
                    value_str = '\n  ' + '\n  '.join(f"• {item}" for item in value)
                else:
                    value_str = str(value)
                prompt += f"- {key.replace('_', ' ').title()}: {value_str}\n"
        
        prompt += f"""
ORIGINAL TEXT:
{original_text}

PROCESSED TEXT:
{processed_text}

COMPLIANCE ANALYSIS INSTRUCTIONS:
Please provide a detailed compliance analysis that includes:

1. **OVERALL COMPLIANCE SCORE**: Rate compliance from 0-100% with justification

2. **ACTION TYPE COMPLIANCE**: 
   - Did the processed text fulfill the primary action type ({action_type})?
   - Provide specific examples of compliance or non-compliance

3. **SPECIFICATION ADHERENCE**: 
   - Analyze each specification from the action config
   - Note which requirements were met, partially met, or missed
   - Provide specific examples and evidence

4. **QUALITY ASSESSMENT**:
   - Assess the quality of the changes made
   - Note any improvements or degradations in the text
   - Evaluate appropriateness of the modifications

5. **EXCEPTIONS AND DEVIATIONS**:
   - List any requirements that were not followed
   - Identify any unauthorized changes or additions
   - Note any missing elements that should have been included

6. **RECOMMENDATIONS**:
   - Suggest improvements for better compliance
   - Recommend any corrective actions needed

Please be thorough, specific, and provide concrete examples from the text to support your analysis.
"""
        
        return prompt
    
    def _call_api(self, prompt: str) -> str:
        """
        Make API call to analyze compliance.
        
        Args:
            prompt: The compliance analysis prompt
            
        Returns:
            Compliance analysis response
        """
        url = f"{self.config['api_base_url']}/chat/completions"
        api_key = self._get_api_key()
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-repo',
            'X-Title': 'OpenRouter Compliance Checker'
        }
        
        data = {
            'model': self.config['model'],
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': self.config['temperature'],
            'max_tokens': self.config['max_tokens']
        }
        
        logging.info("Making API call for compliance analysis")
        logging.info(f"Model: {self.config['model']}")
        logging.debug(f"Prompt length: {len(prompt)} characters")
        
        # Save payload if configured
        if 'payload_file' in self.config:
            self._save_payload(data)
        
        start_time = time.time()
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            result = response.json()
            
            if 'error' in result:
                raise Exception(f"API Error: {result['error']}")
            
            content = result['choices'][0]['message']['content']
            
            logging.info(f"Compliance analysis completed in {elapsed_time:.2f} seconds")
            logging.info(f"Analysis length: {len(content)} characters")
            
            return content
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            raise
        except (KeyError, IndexError) as e:
            logging.error(f"Unexpected API response format: {e}")
            raise
    
    def _save_payload(self, payload: Dict[str, Any]):
        """Save the API payload to JSON file."""
        payload_file = Path(self.config['payload_file'])
        
        logging.info(f"Saving compliance check payload to {payload_file}")
        
        # Create directory if needed
        payload_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(payload_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save payload: {e}")
            # Don't raise - this is not critical
    
    def _save_analysis(self, analysis: str):
        """
        Save the compliance analysis to the output file.
        
        Args:
            analysis: The compliance analysis text
        """
        output_file = Path(self.config['output_file'])
        
        logging.info(f"Saving compliance analysis to {output_file}")
        
        # Create output directory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(analysis)
            logging.info(f"Compliance analysis saved: {len(analysis)} characters")
        except Exception as e:
            logging.error(f"Failed to save analysis to {output_file}: {e}")
            raise
    
    def check_compliance(self) -> str:
        """
        Perform complete compliance check and save analysis.
        
        Returns:
            The compliance analysis text
        """
        separator = "=" * 60
        logging.info(separator)
        logging.info("Starting Compliance Check")
        logging.info(separator)
        
        try:
            # Load all required files
            logging.info("Step 1: Loading files for analysis")
            original_text = self._load_file_content('original_input_file')
            processed_text = self._load_file_content('input_file')  # The output to analyze
            action_config = self._load_action_config()
            
            logging.info(f"✓ Original text: {len(original_text)} characters")
            logging.info(f"✓ Processed text: {len(processed_text)} characters")
            logging.info(f"✓ Action config: {action_config.get('type', 'edit')} action")
            
            # Create compliance analysis prompt
            logging.info("Step 2: Creating compliance analysis prompt")
            prompt = self._create_compliance_prompt(original_text, processed_text, action_config)
            logging.info(f"✓ Prompt created: {len(prompt)} characters")
            
            # Perform compliance analysis via API
            logging.info("Step 3: Performing compliance analysis")
            analysis = self._call_api(prompt)
            logging.info("✓ Compliance analysis completed")
            
            # Save analysis report
            logging.info("Step 4: Saving compliance report")
            self._save_analysis(analysis)
            logging.info("✓ Compliance report saved")
            
            logging.info(separator)
            logging.info("Compliance check completed successfully!")
            logging.info(separator)
            
            return analysis
            
        except Exception as e:
            error_separator = "=" * 60
            logging.error(error_separator)
            logging.error(f"✗ Error during compliance check: {e}")
            logging.error(error_separator)
            raise
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()


def main():
    """Example usage of the ComplianceChecker class."""
    import logging
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Example configuration
        config = {
            'input_file': 'output.md',
            'output_file': 'analysis.md',
            'action_file': 'action.json',
            'original_input_file': 'input.md'
        }
        
        # Create and run compliance checker
        checker = ComplianceChecker(config)
        analysis = checker.check_compliance()
        
        print(f"Compliance check completed. Analysis saved to {config['output_file']}")
        
    except Exception as e:
        logging.error(f"Compliance check failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())