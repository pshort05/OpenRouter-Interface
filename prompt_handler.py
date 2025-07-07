#!/usr/bin/env python3
"""
Prompt Handler Module

Handles prompt loading, validation, and processing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any


class PromptLoader:
    """Loads and validates JSON prompt files."""
    
    def load_prompt(self, prompt_file: Path) -> Dict[str, Any]:
        """
        Load and validate a JSON prompt file.
        
        Args:
            prompt_file: Path to JSON prompt file
            
        Returns:
            Prompt configuration dictionary
        """
        logging.info(f"Loading prompt from: {prompt_file}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_data = json.load(f)
            
            logging.debug(f"Loaded prompt data: {prompt_data}")
            
            # Validate required fields
            self._validate_prompt(prompt_data, prompt_file)
            
            return prompt_data
            
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in prompt file {prompt_file}: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to load prompt file {prompt_file}: {e}")
            raise
    
    def _validate_prompt(self, prompt_data: Dict[str, Any], prompt_file: Path):
        """
        Validate prompt data structure.
        
        Args:
            prompt_data: Loaded prompt configuration
            prompt_file: Path to the prompt file (for error messages)
        """
        # List of possible prompt field names
        possible_prompt_fields = [
            'instruction', 'instructions', 'prompt', 'message', 'content', 'text', 
            'system', 'user_message', 'query', 'task', 'description'
        ]
        
        # Check if any prompt field exists
        found_prompt_field = None
        for field in possible_prompt_fields:
            if field in prompt_data and prompt_data[field]:
                found_prompt_field = field
                break
        
        if not found_prompt_field:
            # Show available fields to help user
            available_fields = list(prompt_data.keys())
            logging.error(f"No recognizable prompt field found in {prompt_file}")
            logging.error(f"Available fields: {available_fields}")
            logging.error(f"Expected one of: {possible_prompt_fields}")
            
            raise ValueError(
                f"Prompt file {prompt_file} must contain a prompt field. "
                f"Available fields: {available_fields}. "
                f"Expected one of: {possible_prompt_fields}"
            )
        
        logging.info(f"✓ Prompt validation passed for {prompt_file.name} (using field: '{found_prompt_field}')")
        logging.debug(f"Available fields in prompt: {list(prompt_data.keys())}")


class PromptProcessor:
    """Processes prompts with input content."""
    
    def create_full_prompt(self, prompt_data: Dict[str, Any], input_content: str) -> str:
        """
        Create full prompt by combining prompt template with input content.
        
        Args:
            prompt_data: Prompt configuration
            input_content: Content to process
            
        Returns:
            Complete prompt string
        """
        # List of possible prompt field names (in order of preference)
        possible_prompt_fields = [
            'instruction', 'instructions', 'prompt', 'message', 'content', 'text', 
            'system', 'user_message', 'query', 'task', 'description'
        ]
        
        # Find the main instruction/prompt field
        instruction = ''
        prompt_field_used = None
        
        for field in possible_prompt_fields:
            if field in prompt_data and prompt_data[field]:
                field_value = prompt_data[field]
                
                # Handle complex instruction objects
                if isinstance(field_value, dict):
                    # For instructions object, extract key fields
                    if field == 'instructions':
                        instruction_parts = []
                        if 'primary_task' in field_value:
                            instruction_parts.append(f"Primary Task: {field_value['primary_task']}")
                        if 'evaluation_process' in field_value:
                            instruction_parts.append(f"Evaluation Process: {field_value['evaluation_process']}")
                        if 'required_analysis' in field_value:
                            instruction_parts.append(f"Required Analysis: {field_value['required_analysis']}")
                        if 'deliverable' in field_value:
                            instruction_parts.append(f"Deliverable: {field_value['deliverable']}")
                        
                        # If no specific fields, convert the whole object
                        if not instruction_parts:
                            instruction = json.dumps(field_value, indent=2)
                        else:
                            instruction = '\n\n'.join(instruction_parts)
                    else:
                        # For other dict fields, convert to JSON
                        instruction = json.dumps(field_value, indent=2)
                else:
                    instruction = str(field_value)
                
                prompt_field_used = field
                break
        
        # Ensure instruction is not empty
        if not instruction:
            # Fallback: use the first non-empty string field
            for key, value in prompt_data.items():
                if isinstance(value, str) and value.strip():
                    instruction = value
                    prompt_field_used = key
                    logging.warning(f"Using field '{key}' as prompt instruction")
                    break
                elif isinstance(value, dict) and value:
                    instruction = json.dumps(value, indent=2)
                    prompt_field_used = key
                    logging.warning(f"Using field '{key}' as prompt instruction")
                    break
        
        logging.info(f"Using prompt field: '{prompt_field_used}' from JSON")
        
        # Build the full prompt starting with persona if available
        full_prompt = ""
        processed_fields = set()
        
        # Add persona first if present
        if 'persona' in prompt_data:
            full_prompt += f"Role: {prompt_data['persona']}\n\n"
            processed_fields.add('persona')
        
        # Add the main instruction
        full_prompt += instruction
        processed_fields.add(prompt_field_used)
        
        # Add evaluation directives if present
        if 'evaluation_directives' in prompt_data:
            eval_directives = prompt_data['evaluation_directives']
            if isinstance(eval_directives, dict):
                full_prompt += "\n\nEvaluation Guidelines:\n"
                for key, value in eval_directives.items():
                    full_prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
            else:
                full_prompt += f"\n\nEvaluation Directives: {eval_directives}"
            processed_fields.add('evaluation_directives')
        
        # Add review criteria if present
        if 'review_criteria' in prompt_data:
            criteria = prompt_data['review_criteria']
            if isinstance(criteria, dict):
                full_prompt += "\n\nReview Criteria:\n"
                for criterion_num, criterion_data in criteria.items():
                    if isinstance(criterion_data, dict):
                        full_prompt += f"\n{criterion_num} - {criterion_data.get('mistake', 'No description')}\n"
                        if 'why_problematic' in criterion_data:
                            full_prompt += f"Why problematic: {criterion_data['why_problematic']}\n"
                        if 'how_to_fix' in criterion_data:
                            full_prompt += f"How to fix: {criterion_data['how_to_fix']}\n"
                    else:
                        full_prompt += f"{criterion_num}: {criterion_data}\n"
            else:
                full_prompt += f"\n\nReview Criteria: {criteria}"
            processed_fields.add('review_criteria')
        
        # Add structured fields in specific order
        field_order = ['genre_adaptation', 'context', 'requirements', 'constraints', 'examples', 'output_format']
        for field_name in field_order:
            if field_name in prompt_data and field_name not in processed_fields:
                full_prompt = self._add_structured_field(full_prompt, prompt_data, field_name, processed_fields)
        
        # Add any remaining fields that haven't been processed
        remaining_fields = set(prompt_data.keys()) - processed_fields
        if remaining_fields:
            logging.debug(f"Adding additional fields: {remaining_fields}")
            for field in remaining_fields:
                value = prompt_data[field]
                if value:  # Only add non-empty values
                    value_text = self._format_field_value(value)
                    field_name = field.replace('_', ' ').title()
                    full_prompt += f"\n\n{field_name}:\n{value_text}"
        
        # Add the input content
        full_prompt += f"\n\nInput content to evaluate:\n\n{input_content}"
        
        logging.info(f"✓ Created full prompt: {len(full_prompt)} characters")
        logging.debug(f"Prompt fields used: {list(prompt_data.keys())}")
        
        return full_prompt
    
    def _add_structured_field(self, full_prompt: str, prompt_data: Dict[str, Any], 
                             field_name: str, processed_fields: set) -> str:
        """Add a structured field to the prompt if it exists."""
        if field_name in prompt_data and field_name not in processed_fields:
            value = prompt_data[field_name]
            value_text = self._format_field_value(value)
            full_prompt += f"\n\n{field_name.replace('_', ' ').title()}:\n{value_text}"
            processed_fields.add(field_name)
        return full_prompt
    
    def _format_field_value(self, value) -> str:
        """Format a field value for inclusion in the prompt."""
        if isinstance(value, dict):
            return json.dumps(value, indent=2)
        elif isinstance(value, list):
            return '\n'.join(f"- {item}" for item in value)
        else:
            return str(value)