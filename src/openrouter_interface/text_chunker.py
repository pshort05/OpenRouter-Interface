#!/usr/bin/env python3
"""
Text Chunker for OpenRouter Text Editor

A class that splits large text files into smaller chunks for processing
and combines the processed chunks back into a single file.

Usage:
    from text_chunker import TextChunker
    
    config = {'input_file': 'input.md', 'output_file': 'output.md'}
    chunker = TextChunker(config)
    
    # Split into chunks
    chunk_files = chunker.split_into_chunks()
    
    # Process each chunk with your editor...
    
    # Combine processed chunks
    chunker.combine_chunks()
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


class TextChunker:
    """
    Handles splitting text files into chunks and combining processed chunks.
    
    This class provides functionality to:
    1. Split large text files into approximately 1000-word chunks at paragraph boundaries
    2. Combine processed chunk files back into a single output file
    3. Optionally clean up intermediate files
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the text chunker with configuration.
        
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
            'input_file': 'input.md',
            'output_file': 'output.md',
            'chunk_size': 1000,  # Target words per chunk
            'chunk_prefix': '',  # Prefix for chunk files (auto-generated from input file)
            'chunk_suffix': 'md',  # File extension for chunks
            'chunk_identifier': 'ch',  # Identifier used in chunk naming (input-ch1.md)
            'cleanup_chunks': True,  # Remove intermediate files after combining
            'chunk_separator': '\n\n---\n\n',  # Separator between chunks when combining
            'preserve_metadata': True  # Preserve front matter and metadata
        }
        
        # Merge user config with defaults
        merged_config = default_config.copy()
        merged_config.update(user_config)
        
        # Auto-generate chunk prefix if not provided
        if not merged_config['chunk_prefix']:
            input_path = Path(merged_config['input_file'])
            merged_config['chunk_prefix'] = input_path.stem
        
        return merged_config
    
    def _validate_config(self):
        """Validate that required configuration parameters are present."""
        if not Path(self.config['input_file']).exists():
            raise FileNotFoundError(
                f"Input file '{self.config['input_file']}' not found"
            )
    
    def _count_words(self, text: str) -> int:
        """
        Count words in a text string.
        
        Args:
            text: Text to count words in
            
        Returns:
            Number of words
        """
        # Simple word counting - split on whitespace and filter empty strings
        words = [word for word in text.split() if word.strip()]
        return len(words)
    
    def _find_paragraph_boundaries(self, text: str) -> List[int]:
        """
        Find paragraph boundaries in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of character positions where paragraphs end
        """
        boundaries = []
        
        # Look for double newlines (paragraph breaks)
        for match in re.finditer(r'\n\s*\n', text):
            boundaries.append(match.end())
        
        # Add the end of the text as a boundary
        boundaries.append(len(text))
        
        return boundaries
    
    def _extract_front_matter(self, text: str) -> tuple[str, str]:
        """
        Extract front matter (YAML/metadata) from the beginning of the text.
        
        Args:
            text: Full text content
            
        Returns:
            Tuple of (front_matter, remaining_text)
        """
        # Check for YAML front matter (--- at start and ---)
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(yaml_pattern, text, re.DOTALL)
        
        if match:
            front_matter = match.group(0)
            remaining_text = text[match.end():]
            return front_matter, remaining_text
        
        # Check for other metadata patterns (# Title at start, etc.)
        # For now, just handle YAML front matter
        return '', text
    
    def _create_chunk_filename(self, chunk_number: int) -> str:
        """
        Create filename for a chunk.
        
        Args:
            chunk_number: 1-based chunk number
            
        Returns:
            Chunk filename
        """
        prefix = self.config['chunk_prefix']
        suffix = self.config['chunk_suffix']
        chunk_id = self.config['chunk_identifier']
        return f"{prefix}-{chunk_id}{chunk_number}.{suffix}"
    
    def _get_output_chunk_filename(self, chunk_number: int) -> str:
        """
        Create output filename for a processed chunk.
        
        Args:
            chunk_number: 1-based chunk number
            
        Returns:
            Output chunk filename
        """
        output_path = Path(self.config['output_file'])
        output_prefix = output_path.stem
        output_suffix = output_path.suffix[1:]  # Remove the dot
        chunk_id = self.config['chunk_identifier']
        return f"{output_prefix}-{chunk_id}{chunk_number}.{output_suffix}"
    
    def split_into_chunks(self) -> int:
        """
        Split the input file into chunks.
        
        Returns:
            Number of chunks created
        """
        logging.info("Starting text chunking process")
        
        # Load input file
        input_file = Path(self.config['input_file'])
        logging.info(f"Loading input file: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                full_text = f.read()
        except Exception as e:
            logging.error(f"Failed to read input file: {e}")
            raise
        
        total_words = self._count_words(full_text)
        logging.info(f"Input file contains {total_words} words")
        
        # Extract front matter if present
        front_matter = ''
        text_to_chunk = full_text
        
        if self.config['preserve_metadata']:
            front_matter, text_to_chunk = self._extract_front_matter(full_text)
            if front_matter:
                logging.info("Front matter detected and will be preserved")
        
        # Find paragraph boundaries
        boundaries = self._find_paragraph_boundaries(text_to_chunk)
        logging.debug(f"Found {len(boundaries)} paragraph boundaries")
        
        # Create chunks
        chunks = []
        chunk_files = []
        current_pos = 0
        chunk_number = 1
        target_chunk_size = self.config['chunk_size']
        
        while current_pos < len(text_to_chunk):
            # Find the best boundary for this chunk
            words_so_far = 0
            best_boundary = len(text_to_chunk)  # Default to end of text
            
            for boundary in boundaries:
                if boundary <= current_pos:
                    continue
                    
                chunk_text = text_to_chunk[current_pos:boundary]
                chunk_words = self._count_words(chunk_text)
                
                if chunk_words >= target_chunk_size:
                    # This boundary gives us at least target_chunk_size words
                    best_boundary = boundary
                    break
                elif chunk_words > words_so_far:
                    # Keep track of the best boundary so far
                    words_so_far = chunk_words
                    best_boundary = boundary
            
            # Create the chunk
            chunk_text = text_to_chunk[current_pos:best_boundary]
            
            # Add front matter to first chunk if present
            if chunk_number == 1 and front_matter:
                chunk_content = front_matter + chunk_text
            else:
                chunk_content = chunk_text
            
            chunks.append(chunk_content)
            
            # Save chunk to file
            chunk_filename = self._create_chunk_filename(chunk_number)
            chunk_path = Path(chunk_filename)
            
            try:
                with open(chunk_path, 'w', encoding='utf-8') as f:
                    f.write(chunk_content)
                
                chunk_files.append(chunk_filename)
                chunk_words = self._count_words(chunk_content)
                logging.info(f"Created chunk {chunk_number}: {chunk_filename} ({chunk_words} words)")
                
            except Exception as e:
                logging.error(f"Failed to save chunk {chunk_number}: {e}")
                raise
            
            # Move to next chunk
            current_pos = best_boundary
            chunk_number += 1
            
            # Safety check to avoid infinite loops
            if chunk_number > 1000:
                logging.error("Too many chunks created (>1000), stopping to prevent infinite loop")
                break
        
        logging.info(f"Text splitting completed: {len(chunk_files)} chunks created")
        
        # Log all created chunk files
        logging.info("Created chunk files:")
        for chunk_file in chunk_files:
            logging.info(f"  - {chunk_file}")
        
        return len(chunk_files)
    
    def combine_files(self, file_pattern: str, output_file: str, cleanup: bool = True) -> str:
        """
        Combine multiple files matching a pattern into a single output file.
        
        Args:
            file_pattern: Pattern to match files (e.g., "output-ch*.md")
            output_file: Path to the combined output file
            cleanup: Whether to delete the intermediate files after combining
            
        Returns:
            Path to the combined output file
        """
        logging.info(f"Starting file combination for pattern: {file_pattern}")
        
        # Find files matching the pattern
        pattern_path = Path(file_pattern)
        
        # Handle glob patterns
        if '*' in file_pattern:
            # Use glob to find matching files
            search_dir = pattern_path.parent if pattern_path.parent != Path('.') else Path('.')
            pattern_name = pattern_path.name
            matching_files = list(search_dir.glob(pattern_name))
        else:
            # Direct file list
            matching_files = [pattern_path] if pattern_path.exists() else []
        
        # Convert to strings and filter existing files
        file_list = []
        for file_path in matching_files:
            if file_path.is_file():
                file_list.append(str(file_path))
        
        if not file_list:
            logging.warning(f"No files found matching pattern: {file_pattern}")
            return output_file
        
        # Sort files by chunk number to ensure correct order
        def extract_chunk_number(filename: str) -> int:
            chunk_id = self.config['chunk_identifier']
            pattern = f'-{chunk_id}(\\d+)\\.'
            match = re.search(pattern, filename)
            return int(match.group(1)) if match else 0
        
        file_list.sort(key=extract_chunk_number)
        logging.info(f"Combining {len(file_list)} files into: {output_file}")
        
        # Log the files being combined
        for file_path in file_list:
            logging.info(f"  - {file_path}")
        
        # Combine files
        combined_content = []
        separator = self.config['chunk_separator']
        
        for i, file_path in enumerate(file_list):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    combined_content.append(content)
                    logging.debug(f"Added file {i+1}: {len(content)} characters")
                
            except Exception as e:
                logging.error(f"Failed to read file {file_path}: {e}")
                raise
        
        # Join all content
        if separator and len(combined_content) > 1:
            final_content = separator.join(combined_content)
        else:
            final_content = '\n\n'.join(combined_content)
        
        # Save combined output
        output_path = Path(output_file)
        logging.info(f"Saving combined content to: {output_path}")
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            total_words = self._count_words(final_content)
            logging.info(f"Combined file saved: {len(final_content)} characters, {total_words} words")
            
        except Exception as e:
            logging.error(f"Failed to save combined file: {e}")
            raise
        
        # Clean up intermediate files if requested
        if cleanup:
            self._cleanup_file_list(file_list)
        
        return str(output_path)
    
    def _cleanup_file_list(self, file_list: List[str]):
        """
        Remove a list of files.
        
        Args:
            file_list: List of file paths to remove
        """
        logging.info("Cleaning up intermediate files")
        removed_count = 0
        
        for file_path in file_list:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    removed_count += 1
                    logging.debug(f"Removed file: {file_path}")
                    
            except Exception as e:
                logging.warning(f"Failed to remove file {file_path}: {e}")
        
        logging.info(f"Cleanup completed: {removed_count} files removed")
    def combine_chunks(self, chunk_files: Optional[List[str]] = None) -> str:
        """
        Combine processed chunk files back into a single output file.
        
        Args:
            chunk_files: Optional list of chunk files to combine.
                        If None, auto-discovers chunk files.
                        
        Returns:
            Path to the combined output file
        """
        logging.info("Starting chunk combination process")
        
        # Auto-discover chunk files if not provided
        if chunk_files is None:
            chunk_files = self._discover_output_chunks()
        
        if not chunk_files:
            raise ValueError("No chunk files found to combine")
        
        # Use the new combine_files method
        output_file = self.config['output_file']
        cleanup = self.config['cleanup_chunks']
        
        return self.combine_files(
            file_pattern=f"{Path(output_file).stem}-{self.config['chunk_identifier']}*.{Path(output_file).suffix[1:]}",
            output_file=output_file,
            cleanup=cleanup
        )
    
    def _discover_output_chunks(self) -> List[str]:
        """
        Auto-discover output chunk files based on the output file pattern.
        
        Returns:
            List of discovered chunk files
        """
        output_path = Path(self.config['output_file'])
        output_prefix = output_path.stem
        output_suffix = output_path.suffix[1:]  # Remove the dot
        chunk_id = self.config['chunk_identifier']
        
        # Look for files matching the pattern: output-ch*.md
        pattern = f"{output_prefix}-{chunk_id}*.{output_suffix}"
        chunk_files = []
        
        # Search in the current directory and output file directory
        search_dirs = [Path('.'), output_path.parent]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for file_path in search_dir.glob(pattern):
                    if file_path.is_file():
                        chunk_files.append(str(file_path))
        
        # Remove duplicates and sort
        chunk_files = list(set(chunk_files))
        logging.debug(f"Discovered {len(chunk_files)} output chunk files")
        
        return chunk_files
    
    def _cleanup_chunk_files(self, chunk_files: List[str]):
        """
        Remove intermediate chunk files.
        
        Args:
            chunk_files: List of chunk files to remove
        """
        if not self.config['cleanup_chunks']:
            return
            
        logging.info("Cleaning up intermediate chunk files")
        removed_count = 0
        
        for chunk_file in chunk_files:
            chunk_path = Path(chunk_file)
            
            try:
                if chunk_path.exists():
                    chunk_path.unlink()
                    removed_count += 1
                    logging.debug(f"Removed chunk file: {chunk_file}")
                    
            except Exception as e:
                logging.warning(f"Failed to remove chunk file {chunk_file}: {e}")
        
        logging.info(f"Cleanup completed: {removed_count} chunk files removed")
    
    def get_chunk_count_estimate(self) -> int:
        """
        Estimate how many chunks the input file will be split into.
        
        Returns:
            Estimated number of chunks
        """
        input_file = Path(self.config['input_file'])
        
        if not input_file.exists():
            return 0
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            total_words = self._count_words(text)
            chunk_size = self.config['chunk_size']
            
            estimated_chunks = max(1, (total_words + chunk_size - 1) // chunk_size)
            return estimated_chunks
            
        except Exception:
            return 0
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()


def main():
    """Example usage of the TextChunker class."""
    import logging
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Example configuration
        config = {
            'input_file': 'input.md',
            'output_file': 'output.md',
            'chunk_size': 1000,
            'cleanup_chunks': True
        }
        
        # Create chunker
        chunker = TextChunker(config)
        
        # Show estimate
        estimated_chunks = chunker.get_chunk_count_estimate()
        print(f"Estimated chunks: {estimated_chunks}")
        
        # Split into chunks
        chunk_count = chunker.split_into_chunks()
        logging.info(f"Created {chunk_count} chunk files")
        
        # In a real scenario, you would process each chunk here
        # For this example, we'll just assume output files exist
        
        # Combine chunks (this would normally be done after processing)
        # output_file = chunker.combine_chunks()
        # print(f"Combined output saved to: {output_file}")
        
        # Example of combining other file types
        # chunker.combine_files("compliance_analysis-ch*.md", "compliance_analysis.md")
        
    except Exception as e:
        logging.error(f"Chunking process failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())