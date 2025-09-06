#!/usr/bin/env python3
"""
OpenRouter Text Editor

A Python program that uses the OpenRouter API to edit text files based on
configuration and action specifications.

Usage:
    python openrouter_editor.py [-c config.yaml]
"""

import argparse
import logging
import sys
from pathlib import Path

from .config_manager import ConfigManager
from .logging_manager import LoggingManager
from .file_handler import FileHandler
from .prompt_builder import PromptBuilder
from .api_client import APIClient


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
        
        config_name = config_file or 'openrouter_editor.yaml'
        logging.info("Configuration loaded from: " + config_name)
        logging.debug("Active configuration: " + str(self.config.config))
    
    def _process_single_file(self, input_file: str, output_file: str) -> str:
        """
        Process a single file through the editing workflow.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            
        Returns:
            The processed text content
        """
        # Create temporary config for this specific file
        temp_config = self.config.config.copy()
        temp_config['input_file'] = input_file
        temp_config['output_file'] = output_file
        
        # Create temporary file handler for this file
        temp_config_manager = ConfigManager()
        temp_config_manager.config = temp_config
        temp_file_handler = FileHandler(temp_config_manager)
        
        # Load input text
        input_text = temp_file_handler.load_input_text()
        logging.debug(f"Loaded {len(input_text)} characters from {input_file}")
        
        # Load action configuration (same for all chunks)
        action = self.file_handler.load_action()
        
        # Create prompt
        prompt = self.prompt_builder.create_prompt(input_text, action)
        
        # Call OpenRouter API
        result = self.api_client.call_api(prompt)
        logging.debug(f"API returned {len(result)} characters for {input_file}")
        
        # Save output
        temp_file_handler.save_output(result)
        
        return result
    
    def _process_with_chunking(self):
        """Process the input file using chunking."""
        try:
            logging.info("Chunking enabled - checking if chunking is needed")
            
            # Import the text chunker
            from text_chunker import TextChunker
            
            # Prepare chunker configuration
            chunker_config = {
                'input_file': self.config.get('input_file'),
                'output_file': self.config.get('output_file'),
                'chunk_size': self.config.get('chunk_size', 1000),
                'chunk_identifier': self.config.get('chunk_identifier', 'ch'),
                'cleanup_chunks': False  # Don't cleanup yet - we need files for compliance
            }
            
            # Create chunker and estimate chunks needed
            chunker = TextChunker(chunker_config)
            estimated_chunks = chunker.get_chunk_count_estimate()
            
            if estimated_chunks <= 1:
                logging.info("File is small enough, processing without chunking")
                return self._process_without_chunking()
            
            logging.info(f"Large file detected, splitting into approximately {estimated_chunks} chunks")
            
            # Split into chunks
            chunk_count = chunker.split_into_chunks()
            logging.info(f"File split into {chunk_count} chunks")
            
            # Process each chunk with the specified flow
            input_path = Path(self.config.get('input_file'))
            output_path = Path(self.config.get('output_file'))
            compliance_path = Path(self.config.get('compliance_output_file', 'compliance_analysis.md'))
            chunk_id = self.config.get('chunk_identifier', 'ch')
            
            for i in range(1, chunk_count + 1):
                logging.info(f"Processing chunk {i}/{chunk_count}")
                
                # Create chunk file names
                chunk_input = f"{input_path.stem}-{chunk_id}{i}.{input_path.suffix[1:]}"
                chunk_output = f"{output_path.stem}-{chunk_id}{i}.{output_path.suffix[1:]}"
                chunk_compliance = f"{compliance_path.stem}-{chunk_id}{i}.{compliance_path.suffix[1:]}"
                
                # Step 1: Process this chunk (input-ch1.md -> output-ch1.md)
                logging.info(f"  Editing chunk {i}: {chunk_input} -> {chunk_output}")
                self._process_single_file(chunk_input, chunk_output)
                
                # Step 2: Run compliance check on processed chunk (output-ch1.md -> compliance_analysis-ch1.md)
                if self.config.get('enable_compliance_check', True):
                    logging.info(f"  Compliance check for chunk {i}: {chunk_output} -> {chunk_compliance}")
                    self._run_compliance_check_for_file(chunk_output, chunk_compliance)
                
                logging.info(f"✓ Chunk {i} completed")
            
            # Combine all processed chunks
            logging.info("Combining processed output chunks")
            chunker.combine_chunks()
            logging.info(f"✓ Output chunks combined into: {output_path}")
            
            # Combine compliance analysis files if compliance checking is enabled
            if self.config.get('enable_compliance_check', True):
                logging.info("Combining compliance analysis chunks")
                compliance_pattern = f"{compliance_path.stem}-{chunk_id}*.{compliance_path.suffix[1:]}"
                chunker.combine_files(
                    file_pattern=compliance_pattern,
                    output_file=str(compliance_path),
                    cleanup=True  # Clean up compliance chunks
                )
                logging.info(f"✓ Compliance chunks combined into: {compliance_path}")
            
            # Clean up output chunks (but keep the final combined files)
            logging.info("Cleaning up intermediate output chunks")
            for i in range(1, chunk_count + 1):
                chunk_output = f"{output_path.stem}-{chunk_id}{i}.{output_path.suffix[1:]}"
                chunk_path = Path(chunk_output)
                if chunk_path.exists():
                    try:
                        chunk_path.unlink()
                        logging.debug(f"Removed output chunk: {chunk_output}")
                    except Exception as e:
                        logging.warning(f"Failed to remove output chunk {chunk_output}: {e}")
            
            # Clean up input chunks
            for i in range(1, chunk_count + 1):
                chunk_input = f"{input_path.stem}-{chunk_id}{i}.{input_path.suffix[1:]}"
                chunk_path = Path(chunk_input)
                if chunk_path.exists():
                    try:
                        chunk_path.unlink()
                        logging.debug(f"Removed input chunk: {chunk_input}")
                    except Exception as e:
                        logging.warning(f"Failed to remove input chunk {chunk_input}: {e}")
            
            return chunk_count
            
        except ImportError as e:
            logging.warning("Could not import text_chunker.py - processing without chunking")
            logging.debug(f"Import error details: {e}")
            return self._process_without_chunking()
        except Exception as e:
            logging.error(f"Chunking process failed: {e}")
            logging.info("Falling back to processing without chunking")
            return self._process_without_chunking()
    
    def _process_without_chunking(self):
        """Process the input file as a single unit (original behavior)."""
        # Load input text
        input_text = self.file_handler.load_input_text()
        logging.info("✓ Input text loaded: " + str(len(input_text)) + " characters")
        
        # Load action configuration
        action = self.file_handler.load_action()
        action_type = action.get('type', 'edit')
        logging.info("✓ Action loaded: " + action_type)
        
        # Create prompt
        prompt = self.prompt_builder.create_prompt(input_text, action)
        logging.info("✓ Prompt created: " + str(len(prompt)) + " characters")
        
        # Call OpenRouter API
        result = self.api_client.call_api(prompt)
        logging.info("✓ API call successful, received " + str(len(result)) + " characters")
        
        # Save output
        self.file_handler.save_output(result)
        logging.info("✓ Output saved successfully")
        
        return 1  # Return 1 to indicate single file processed
    
    def _run_compliance_check_for_file(self, input_file: str, output_file: str):
        """
        Run compliance check for a specific file.
        
        Args:
            input_file: The processed output file to analyze
            output_file: Where to save the compliance analysis
        """
        if not self.config.get('enable_compliance_check', True):
            return
            
        try:
            # Import the compliance checker
            from compliance_checker import ComplianceChecker
            
            # Prepare compliance check configuration
            compliance_config = {
                'input_file': input_file,  # The processed output to analyze
                'output_file': output_file,  # Where to save the analysis
                'action_file': self.config.get('action_file', 'action.json'),
                'original_input_file': self.config.get('input_file', 'input.md'),
                'model': self.config.get('model'),
                'api_base_url': self.config.get('api_base_url'),
                'temperature': 0.3,  # Lower temperature for consistent analysis
                'max_tokens': self.config.get('max_tokens', 10000),
                'api_key': self.config.get('api_key')
            }
            
            # Create and run compliance checker
            checker = ComplianceChecker(compliance_config)
            analysis = checker.check_compliance()
            
            logging.debug(f"Compliance check completed for {input_file}")
            
        except ImportError as e:
            logging.warning("Could not import compliance_checker.py - skipping compliance check")
            logging.debug("Import error details: " + str(e))
        except Exception as e:
            logging.warning(f"Compliance check failed for {input_file}: {e}")
            logging.debug("Compliance check error details:", exc_info=True)
    
    def _run_compliance_check(self):
        """Run compliance check if enabled in configuration."""
        if not self.config.get('enable_compliance_check', True):
            logging.info("Compliance check disabled in configuration")
            return
            
        try:
            logging.info("Step 6: Running compliance check")
            
            # Run compliance check for the final output file
            self._run_compliance_check_for_file(
                self.config.get('output_file', 'output.md'),
                self.config.get('compliance_output_file', 'compliance_analysis.md')
            )
            
            logging.info("✓ Compliance check completed successfully")
            logging.info("✓ Analysis saved to: " + str(self.config.get('compliance_output_file', 'compliance_analysis.md')))
            
        except Exception as e:
            logging.warning("Compliance check failed but main processing was successful: " + str(e))
            logging.debug("Compliance check error details:", exc_info=True)
    
    def process(self):
        """Main processing method."""
        separator = "=" * 60
        logging.info(separator)
        logging.info("Starting OpenRouter Text Editor processing")
        logging.info(separator)
        
        try:
            # Check if chunking is enabled
            if self.config.get('enable_chunking', False):
                logging.info("Step 1-5: Processing with chunking enabled")
                chunks_processed = self._process_with_chunking()
                if chunks_processed > 1:
                    logging.info(f"✓ Successfully processed {chunks_processed} chunks")
                else:
                    logging.info("✓ File processed as single unit")
            else:
                logging.info("Step 1: Loading input text")
                logging.info("Step 2: Loading action configuration") 
                logging.info("Step 3: Creating API prompt")
                logging.info("Step 4: Calling OpenRouter API")
                logging.info("Step 5: Saving output")
                
                self._process_without_chunking()
            
            # Run compliance check if enabled
            self._run_compliance_check()
            
            logging.info(separator)
            logging.info("Text editing completed successfully!")
            if self.config.get('enable_compliance_check', True):
                logging.info("Compliance analysis available in: " + str(self.config.get('compliance_output_file', 'compliance_analysis.md')))
            logging.info(separator)
            
        except Exception as e:
            error_separator = "=" * 60
            logging.error(error_separator)
            logging.error("✗ Error during processing: " + str(e))
            logging.error(error_separator)
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
        logging.error("Failed to initialize editor: " + str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()