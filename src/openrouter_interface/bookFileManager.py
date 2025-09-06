import os
import re
import json
import yaml
import logging

logger = logging.getLogger(__name__)

class BookFileManager:
    """
    Handles file operations for reading, writing, and chunking book content.
    """
    def __init__(self, config):
        self.config = config
        self.input_chapter_file = config.get('input_chapter_file', 'chapter_input.md')
        self.action_prompt_file = config.get('action_prompt_file', 'action_prompt.json')
        self.output_chapter_file = config.get('output_chapter_file', 'chapter_output.md')

    def read_markdown_file(self, file_path):
        """Reads content from a Markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Input Markdown file not found at '{file_path}'")
            exit(1)
        except Exception as e:
            logger.error(f"Error reading Markdown file '{file_path}': {e}")
            exit(1)

    def read_json_file(self, file_path):
        """Reads content from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"JSON prompt file not found at '{file_path}'")
            exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON prompt file '{file_path}': {e}")
            exit(1)
        except Exception as e:
            logger.error(f"Error reading JSON file '{file_path}': {e}")
            exit(1)

    def write_markdown_file(self, content, mode='a'):
        """
        Writes content to the output Markdown file.
        Mode 'w' clears existing content, 'a' appends.
        """
        try:
            # Add a newline character at the end of the content
            final_content = content + "\n"
            with open(self.output_chapter_file, mode, encoding='utf-8') as f:
                f.write(final_content)
            if mode == 'w':
                logger.info(f"Output successfully written to '{self.output_chapter_file}' (file cleared first).")
            else:
                logger.info(f"Output successfully appended to '{self.output_chapter_file}'.")
        except Exception as e:
            logger.error(f"Error writing output to Markdown file '{self.output_chapter_file}': {e}")
            exit(1)

    def chunk_text_by_paragraphs(self, text, max_words=1000, min_words_before_break=975):
        """
        Splits text into chunks, aiming for max_words but breaking at paragraph ends.
        Ensures chunks are at least min_words_before_break before looking for a paragraph end.
        """
        paragraphs = re.split(r'(\n\s*\n)', text) # Split by paragraph breaks, keeping delimiters
        chunks = []
        current_chunk_words = []
        current_chunk_text = []

        for i, part in enumerate(paragraphs):
            is_delimiter = bool(re.match(r'\n\s*\n', part))
            words_in_part = part.split()

            # If adding this part exceeds max_words and we've reached min_words_before_break,
            # or if it's a delimiter and we have content in the current chunk,
            # finalize the current chunk.
            if (len(current_chunk_words) + len(words_in_part) > max_words and len(current_chunk_words) >= min_words_before_break) or \
               (is_delimiter and current_chunk_words):
                chunks.append("".join(current_chunk_text).strip())
                current_chunk_words = []
                current_chunk_text = []

            current_chunk_words.extend(words_in_part)
            current_chunk_text.append(part)

        # Add any remaining content as the last chunk
        if current_chunk_words:
            chunks.append("".join(current_chunk_text).strip())

        return chunks

    def get_input_chapter_content(self):
        """Reads and returns the content of the input chapter file."""
        logger.info(f"Reading chapter details from: {self.input_chapter_file}")
        return self.read_markdown_file(self.input_chapter_file)

    def get_action_prompt(self):
        """Reads and returns the action prompt from the JSON file."""
        logger.info(f"Reading action prompt from: {self.action_prompt_file}")
        return self.read_json_file(self.action_prompt_file)

    def clear_output_file(self):
        """Clears the content of the output chapter file."""
        self.write_markdown_file("", mode='w')

    def append_to_output_file(self, content):
        """Appends content to the output chapter file."""
        self.write_markdown_file(content, mode='a')