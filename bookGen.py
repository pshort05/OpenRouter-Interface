# bookGen.py (Combined for Google Colaboratory)

import argparse
import yaml
import os
import logging
import time
import re
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Start of BookFileManager Class Definition ---
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

# --- End of BookFileManager Class Definition ---


def load_config(config_path):
    """Loads configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found at '{config_path}'")
        exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        exit(1)

def call_openrouter_api(config, chapter_content, action_prompt):
    """
    Calls the OpenRouter API with the provided chapter content and action prompt.
    Retrieves API key from environment variable first, then config file.
    Logs the duration of the API call.
    """
    # 1. Try to get API key from environment variable
    api_key = os.getenv('OPENROUTER_API_KEY')

    # 2. If not found in environment, try to get from config file
    if not api_key:
        api_key = config.get('openrouter_api_key')
        if api_key:
            logger.info("API key retrieved from config file.")
        else:
            logger.error("Error: OpenRouter API key not found. Please set the 'OPENROUTER_API_KEY' environment variable or provide it in 'bookGen.yaml'.")
            exit(1)
    else:
        logger.info("API key retrieved from environment variable 'OPENROUTER_API_KEY'.")


    model = config.get('model', 'anthropic/claude-3-opus') # Default to Claude 3 Opus
    api_base_url = config.get('api_base_url', 'https://openrouter.ai/api/v1/chat/completions')

    # Get temperature and max_tokens from config, with specified defaults
    temperature = config.get('temperature', 1.0)
    max_tokens = config.get('max_tokens', 10000)

    # Construct the prompt for the LLM
    system_message = "You are a professional book editor and writer. Your task is to assist in writing, editing, or analyzing book chapters based on the user's instructions."
    user_message = f"""
Current Chapter/Scene Details:
```markdown
{chapter_content}
Action to take: {action_prompt.get('action', 'write')}
Instructions: {action_prompt.get('instructions', 'Please continue writing the next section of the chapter.')}

Please provide the output in Markdown format.
"""

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-website-or-app-name.com", # Replace with your actual referer
    "X-Title": "Book Chapter Generator", # Replace with your actual app title
}

payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ],
    "temperature": temperature, # Use configurable temperature
    "max_tokens": max_tokens # Use configurable max_tokens
}

logger.info(f"Calling OpenRouter API with model: {model}, temperature: {temperature}, max_tokens: {max_tokens}...")
start_time = time.time() # Record start time
try:
    response = requests.post(api_base_url, headers=headers, json=payload)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    response_data = response.json()

    end_time = time.time() # Record end time
    duration = end_time - start_time
    logger.info(f"OpenRouter API call took {duration:.2f} seconds.")

    if response_data and response_data.get('choices'):
        generated_text = response_data['choices'][0]['message']['content']
        logger.info("Successfully received response from OpenRouter API.")
        return generated_text
    else:
        logger.error("Unexpected API response structure.")
        logger.error(f"Full response: {response_data}")
        return None
except requests.exceptions.RequestException as e:
    end_time = time.time() # Record end time even on error
    duration = end_time - start_time
    logger.error(f"Error calling OpenRouter API after {duration:.2f} seconds: {e}")
    if response is not None:
        logger.error(f"Response status code: {response.status_code}")
        logger.error(f"Response body: {response.text}")
    return None
except Exception as e:
    end_time = time.time() # Record end time even on error
    duration = end_time - start_time
    logger.error(f"An unexpected error occurred during API call after {duration:.2f} seconds: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Generate book chapters using an LLM via OpenRouter API.")
    parser.add_argument('-c', '--config', default='bookGen.yaml',
                        help='Path to the YAML configuration file (default: bookGen.yaml)')
    args = parser.parse_args()

    config = load_config(args.config)

    # Set logging level from config, default to INFO if not specified
    log_level_str = config.get('log_level', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)
    logger.info(f"Logging level set to {log_level_str}")

    # Initialize the BookFileManager
    file_manager = BookFileManager(config)

    chapter_content = file_manager.get_input_chapter_content()
    action_prompt = file_manager.get_action_prompt()

    # Clear output file content at the beginning
    file_manager.clear_output_file()

    word_count = len(chapter_content.split())
    if word_count > 1500:
        logger.info(f"Input chapter content is {word_count} words, which is longer than 1500 words. Chunking...")
        chunks = file_manager.chunk_text_by_paragraphs(chapter_content, max_words=1000, min_words_before_break=975)
        logger.info(f"Split into {len(chunks)} chunks.")
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)} (approx {len(chunk.split())} words)...")
            generated_chapter_chunk = call_openrouter_api(config, chunk, action_prompt)
            if generated_chapter_chunk:
                file_manager.append_to_output_file(generated_chapter_chunk)
            else:
                logger.error(f"Chapter generation failed for chunk {i+1}. Please check the errors above.")
    else:
        logger.info(f"Input chapter content is {word_count} words, no chunking needed.")
        generated_chapter = call_openrouter_api(config, chapter_content, action_prompt)
        if generated_chapter:
            file_manager.append_to_output_file(generated_chapter)
        else:
            logger.error("Chapter generation failed. Please check the errors above.")

if __name__ == "__main__":
    main()