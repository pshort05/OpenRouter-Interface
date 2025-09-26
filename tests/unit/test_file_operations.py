"""
Unit tests for file operation classes.

Tests FileHandler, InputFileHandler, and ResponseHandler functionality.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, Mock

import pytest

from src.openrouter_interface.file_handler import FileHandler
from src.openrouter_interface.input_handler import InputFileHandler
from src.openrouter_interface.response_handler import ResponseHandler
from src.openrouter_interface.config_manager import ConfigManager


class TestFileHandler:
    """Test suite for FileHandler class."""

    def test_init_with_config(self, sample_config_file):
        """Test FileHandler initialization with configuration."""
        config = ConfigManager(str(sample_config_file))
        file_handler = FileHandler(config)

        assert file_handler.config == config

    def test_save_payload(self, sample_config_file, temp_dir):
        """Test saving API payload to file."""
        config = ConfigManager(str(sample_config_file))

        # Override payload file location to temp directory
        config.config['payload_file'] = str(temp_dir / "test_payload.json")

        file_handler = FileHandler(config)

        test_payload = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "test prompt"}],
            "temperature": 0.8
        }

        file_handler.save_payload(test_payload)

        # Verify file was created and contains correct data
        payload_file = Path(config.config['payload_file'])
        assert payload_file.exists()

        with open(payload_file, 'r') as f:
            saved_payload = json.load(f)

        assert saved_payload == test_payload

    def test_save_payload_creates_directory(self, sample_config_file, temp_dir):
        """Test that save_payload creates directory if it doesn't exist."""
        config = ConfigManager(str(sample_config_file))

        # Set payload file in non-existent directory
        nested_dir = temp_dir / "nested" / "directory"
        config.config['payload_file'] = str(nested_dir / "payload.json")

        file_handler = FileHandler(config)

        test_payload = {"test": "data"}
        file_handler.save_payload(test_payload)

        # Verify directory was created and file exists
        assert nested_dir.exists()
        assert (nested_dir / "payload.json").exists()

    def test_save_payload_overwrite_existing(self, sample_config_file, temp_dir):
        """Test that save_payload overwrites existing file."""
        config = ConfigManager(str(sample_config_file))
        payload_file = temp_dir / "payload.json"
        config.config['payload_file'] = str(payload_file)

        file_handler = FileHandler(config)

        # Save first payload
        first_payload = {"version": 1}
        file_handler.save_payload(first_payload)

        # Save second payload
        second_payload = {"version": 2}
        file_handler.save_payload(second_payload)

        # Verify file contains latest payload
        with open(payload_file, 'r') as f:
            saved_payload = json.load(f)

        assert saved_payload == second_payload

    def test_save_payload_with_permission_error(self, sample_config_file):
        """Test handling of permission errors when saving payload."""
        config = ConfigManager(str(sample_config_file))
        config.config['payload_file'] = "/root/restricted/payload.json"

        file_handler = FileHandler(config)

        with pytest.raises(PermissionError):
            file_handler.save_payload({"test": "data"})

    def test_save_payload_json_serialization_error(self, sample_config_file, temp_dir):
        """Test handling of JSON serialization errors."""
        config = ConfigManager(str(sample_config_file))
        config.config['payload_file'] = str(temp_dir / "payload.json")

        file_handler = FileHandler(config)

        # Object that can't be JSON serialized
        class NonSerializable:
            pass

        non_serializable_payload = {"object": NonSerializable()}

        with pytest.raises(TypeError):
            file_handler.save_payload(non_serializable_payload)


class TestInputFileHandler:
    """Test suite for InputFileHandler class."""

    def test_init(self):
        """Test InputFileHandler initialization."""
        handler = InputFileHandler()
        assert handler is not None

    def test_load_input_content_text_file(self, sample_input_file):
        """Test loading content from a text file."""
        handler = InputFileHandler()
        content = handler.load_input_content(sample_input_file)

        assert "Sample Test Document" in content
        assert isinstance(content, str)
        assert len(content) > 0

    def test_load_input_content_markdown_file(self, temp_dir):
        """Test loading content from a markdown file."""
        handler = InputFileHandler()

        markdown_content = """# Markdown Test

This is a markdown file with:
- Bullet points
- **Bold text**
- *Italic text*

## Section 2

More content here."""

        md_file = temp_dir / "test.md"
        with open(md_file, 'w') as f:
            f.write(markdown_content)

        content = handler.load_input_content(md_file)
        assert content == markdown_content

    def test_load_input_content_empty_file(self, temp_dir):
        """Test loading content from an empty file."""
        handler = InputFileHandler()

        empty_file = temp_dir / "empty.txt"
        empty_file.touch()

        content = handler.load_input_content(empty_file)
        assert content == ""

    def test_load_input_content_nonexistent_file(self, temp_dir):
        """Test loading content from non-existent file."""
        handler = InputFileHandler()
        nonexistent_file = temp_dir / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            handler.load_input_content(nonexistent_file)

    def test_load_input_content_unicode_file(self, temp_dir):
        """Test loading content with unicode characters."""
        handler = InputFileHandler()

        unicode_content = "Content with émojis 🚀 and français text 🇫🇷"
        unicode_file = temp_dir / "unicode.txt"

        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write(unicode_content)

        content = handler.load_input_content(unicode_file)
        assert content == unicode_content

    def test_load_input_content_large_file(self, temp_dir):
        """Test loading content from a large file."""
        handler = InputFileHandler()

        # Create large content (50,000 characters)
        large_content = "A" * 50000
        large_file = temp_dir / "large.txt"

        with open(large_file, 'w') as f:
            f.write(large_content)

        content = handler.load_input_content(large_file)
        assert len(content) == 50000
        assert content == large_content

    def test_get_input_file_interactive_mode(self):
        """Test interactive file selection (mocked)."""
        handler = InputFileHandler()

        # Mock user input and file scanning
        with patch('builtins.input', return_value='1'), \
             patch.object(handler, '_scan_for_input_files', return_value=['test1.md', 'test2.txt']), \
             patch('pathlib.Path.exists', return_value=True):

            result = handler.get_input_file()
            assert result == Path('test1.md')

    def test_get_input_file_no_files_found(self):
        """Test interactive mode when no files are found."""
        handler = InputFileHandler()

        with patch.object(handler, '_scan_for_input_files', return_value=[]):
            result = handler.get_input_file()
            assert result is None

    def test_get_input_file_invalid_selection(self):
        """Test interactive mode with invalid user selection."""
        handler = InputFileHandler()

        with patch('builtins.input', side_effect=['999', '0', '1']), \
             patch.object(handler, '_scan_for_input_files', return_value=['test.md']), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.print'):  # Suppress print output

            result = handler.get_input_file()
            assert result == Path('test.md')

    def test_scan_for_input_files(self, temp_dir):
        """Test scanning for input files in directory."""
        handler = InputFileHandler()

        # Create various file types
        (temp_dir / "document.md").touch()
        (temp_dir / "readme.txt").touch()
        (temp_dir / "script.py").touch()
        (temp_dir / "config.json").touch()
        (temp_dir / "hidden.tmp").touch()

        # Change to temp directory for scanning
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_dir)

            files = handler._scan_for_input_files()

            # Should find text and markdown files
            file_names = [f.name for f in files]
            assert "document.md" in file_names
            assert "readme.txt" in file_names
            # Should not include non-text files
            assert "script.py" not in file_names
            assert "config.json" not in file_names
            assert "hidden.tmp" not in file_names
        finally:
            os.chdir(original_cwd)


class TestResponseHandler:
    """Test suite for ResponseHandler class."""

    def test_init_without_output_file(self):
        """Test ResponseHandler initialization without output file."""
        handler = ResponseHandler()
        assert handler.output_file is None

    def test_init_with_output_file(self, temp_dir):
        """Test ResponseHandler initialization with output file."""
        output_file = temp_dir / "output.md"
        handler = ResponseHandler(str(output_file))
        assert handler.output_file == Path(str(output_file))

    def test_stream_response_console_only(self, sample_prompt_file, sample_input_file):
        """Test streaming response to console only."""
        handler = ResponseHandler()

        test_response = "This is the AI response content."

        with patch('builtins.print') as mock_print:
            handler.stream_response(test_response, sample_prompt_file, sample_input_file)

            # Verify response was printed to console
            print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
            response_printed = any(test_response in call for call in print_calls)
            assert response_printed

    def test_stream_response_to_file(self, temp_dir, sample_prompt_file, sample_input_file):
        """Test streaming response to file."""
        output_file = temp_dir / "output.md"
        handler = ResponseHandler(str(output_file))

        test_response = "This is the AI response content for file output."

        with patch('builtins.print'):  # Suppress console output
            handler.stream_response(test_response, sample_prompt_file, sample_input_file)

        # Verify file was created and contains response
        assert output_file.exists()

        with open(output_file, 'r') as f:
            file_content = f.read()

        assert test_response in file_content
        assert sample_prompt_file.name in file_content
        assert sample_input_file.name in file_content

    def test_stream_response_append_to_existing_file(self, temp_dir, sample_prompt_file, sample_input_file):
        """Test appending response to existing file."""
        output_file = temp_dir / "output.md"

        # Create file with existing content
        existing_content = "# Existing Content\n\nThis was already here.\n\n"
        with open(output_file, 'w') as f:
            f.write(existing_content)

        handler = ResponseHandler(str(output_file))
        test_response = "New response content."

        with patch('builtins.print'):
            handler.stream_response(test_response, sample_prompt_file, sample_input_file)

        # Verify content was appended
        with open(output_file, 'r') as f:
            file_content = f.read()

        assert existing_content in file_content
        assert test_response in file_content

    def test_stream_response_file_format(self, temp_dir, sample_prompt_file, sample_input_file):
        """Test the format of response written to file."""
        output_file = temp_dir / "output.md"
        handler = ResponseHandler(str(output_file))

        test_response = "Test response for format checking."

        with patch('builtins.print'):
            handler.stream_response(test_response, sample_prompt_file, sample_input_file)

        with open(output_file, 'r') as f:
            content = f.read()

        # Check format structure
        assert "## Response" in content
        assert "**Prompt File:**" in content
        assert "**Input File:**" in content
        assert "**Timestamp:**" in content
        assert test_response in content

    def test_stream_response_unicode_content(self, temp_dir, sample_prompt_file, sample_input_file):
        """Test streaming response with unicode characters."""
        output_file = temp_dir / "output.md"
        handler = ResponseHandler(str(output_file))

        unicode_response = "Réponse en français avec émojis 🚀 🇫🇷"

        with patch('builtins.print'):
            handler.stream_response(unicode_response, sample_prompt_file, sample_input_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert unicode_response in content

    def test_stream_response_large_content(self, temp_dir, sample_prompt_file, sample_input_file):
        """Test streaming large response content."""
        output_file = temp_dir / "output.md"
        handler = ResponseHandler(str(output_file))

        # Large response (100,000 characters)
        large_response = "A" * 100000

        with patch('builtins.print'):
            handler.stream_response(large_response, sample_prompt_file, sample_input_file)

        with open(output_file, 'r') as f:
            content = f.read()

        assert large_response in content
        assert len(content) > 100000

    def test_stream_response_creates_output_directory(self, temp_dir, sample_prompt_file, sample_input_file):
        """Test that streaming creates output directory if it doesn't exist."""
        nested_dir = temp_dir / "nested" / "directory"
        output_file = nested_dir / "output.md"
        handler = ResponseHandler(str(output_file))

        test_response = "Response for directory creation test."

        with patch('builtins.print'):
            handler.stream_response(test_response, sample_prompt_file, sample_input_file)

        # Verify directory was created and file exists
        assert nested_dir.exists()
        assert output_file.exists()

    def test_stream_response_permission_error(self, sample_prompt_file, sample_input_file):
        """Test handling of permission errors when writing to file."""
        handler = ResponseHandler("/root/restricted/output.md")

        with pytest.raises(PermissionError):
            handler.stream_response("Test response", sample_prompt_file, sample_input_file)


@pytest.mark.unit
class TestFileOperationsEdgeCases:
    """Test edge cases and error conditions for file operations."""

    def test_file_handler_invalid_json_payload(self, sample_config_file, temp_dir):
        """Test FileHandler with payload containing circular references."""
        config = ConfigManager(str(sample_config_file))
        config.config['payload_file'] = str(temp_dir / "payload.json")

        file_handler = FileHandler(config)

        # Create circular reference
        circular_dict = {"self": None}
        circular_dict["self"] = circular_dict

        with pytest.raises(ValueError):
            file_handler.save_payload(circular_dict)

    def test_input_handler_binary_file(self, temp_dir):
        """Test InputFileHandler with binary file."""
        handler = InputFileHandler()

        # Create binary file
        binary_file = temp_dir / "binary.bin"
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03\xFF')

        # Should handle gracefully or raise appropriate error
        with pytest.raises(UnicodeDecodeError):
            handler.load_input_content(binary_file)

    def test_response_handler_concurrent_access(self, temp_dir, sample_prompt_file, sample_input_file):
        """Test ResponseHandler with concurrent file access."""
        output_file = temp_dir / "concurrent.md"
        handler = ResponseHandler(str(output_file))

        # Mock file opening to raise a file access error
        with patch('builtins.open', side_effect=OSError("File locked")):
            with pytest.raises(OSError):
                handler.stream_response("Test", sample_prompt_file, sample_input_file)