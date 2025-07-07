#!/usr/bin/env python3
"""
Prompt Builder

Handles prompt creation for API calls in OpenRouter Text Editor.
"""

import logging
from typing import Dict, Any


class PromptBuilder:
    """Handles prompt creation for API calls."""
    
    def create_prompt(self, input_text: str, action: Dict[str, Any]) -> str:
        """Create prompt for the OpenRouter API based on action configuration."""
        action_type = action.get('type', 'edit')
        custom_instruction = action.get('instruction')
        
        logging.info("Creating prompt for action type: " + action_type)
        logging.debug("Full action configuration: " + str(action))
        
        # Create the main instruction based on action type
        if custom_instruction:
            # Use custom instruction if provided
            prompt = custom_instruction + "\n\n"
        else:
            # Use default instruction based on action type
            if action_type == 'edit':
                prompt = "Edit the following markdown text"
            elif action_type == 'rewrite':
                prompt = "Rewrite the following markdown text"
            elif action_type == 'summarize':
                prompt = "Summarize the following markdown text"
            elif action_type == 'translate':
                target_language = action.get('target_language', 'English')
                logging.info("Translation target language: " + target_language)
                prompt = "Translate the following markdown text to " + target_language
            else:
                # Custom action type
                logging.info("Using custom action type: " + action_type)
                prompt = "Process the following markdown text"
            
            prompt += ":\n\n"
        
        # Add explicit instruction to avoid commentary
        prompt += "IMPORTANT: Return ONLY the edited text. Do not include any explanatory notes, editorial comments, summaries of changes, or additional commentary before or after the text."
        
        # Add any additional context from action.json
        if 'additional_context' in action:
            logging.debug("Adding additional context: " + str(action['additional_context']))
            prompt += " with the following additional context: " + str(action['additional_context'])
        
        # Add any style or tone instructions
        if 'style' in action:
            logging.debug("Adding style instruction: " + str(action['style']))
            prompt += " using a " + str(action['style']) + " style"
        
        if 'tone' in action:
            logging.debug("Adding tone instruction: " + str(action['tone']))
            prompt += " with a " + str(action['tone']) + " tone"
        
        # Add any specific requirements
        if 'requirements' in action:
            requirements = action['requirements']
            if isinstance(requirements, list):
                requirements_text = "\n".join(["- " + str(req) for req in requirements])
            else:
                requirements_text = str(requirements)
            logging.debug("Adding requirements: " + str(requirements))
            prompt += "\n\nSpecific requirements:\n" + requirements_text
        
        # Add any constraints
        if 'constraints' in action:
            constraints = action['constraints']
            if isinstance(constraints, list):
                constraints_text = "\n".join(["- " + str(constraint) for constraint in constraints])
            else:
                constraints_text = str(constraints)
            logging.debug("Adding constraints: " + str(constraints))
            prompt += "\n\nConstraints:\n" + constraints_text
        
        # Add any examples if provided
        if 'examples' in action:
            examples = action['examples']
            logging.debug("Adding examples: " + str(examples))
            prompt += "\n\nExamples:\n" + str(examples)
        
        # Add any output format specifications
        if 'output_format' in action:
            output_format = action['output_format']
            logging.debug("Adding output format: " + str(output_format))
            prompt += "\n\nOutput format: " + str(output_format)
        
        # Add target audience if specified
        if 'target_audience' in action:
            target_audience = action['target_audience']
            logging.debug("Adding target audience: " + str(target_audience))
            prompt += "\n\nTarget audience: " + str(target_audience)
        
        # Add any other custom fields from action.json (excluding already processed ones)
        processed_fields = {
            'type', 'instruction', 'additional_context', 'target_language', 
            'style', 'tone', 'requirements', 'constraints', 'examples', 
            'output_format', 'target_audience'
        }
        
        custom_fields = {k: v for k, v in action.items() if k not in processed_fields}
        if custom_fields:
            logging.debug("Adding custom fields: " + str(custom_fields))
            prompt += "\n\nAdditional instructions:"
            for key, value in custom_fields.items():
                prompt += "\n- " + key.replace('_', ' ').title() + ": " + str(value)
        
        # Finally, add the actual text to process
        prompt += "\n\nText to process:\n\n" + input_text
        
        logging.debug("Final prompt length: " + str(len(prompt)) + " characters")
        logging.debug("Action fields included in prompt: " + str(list(action.keys())))
        
        return prompt