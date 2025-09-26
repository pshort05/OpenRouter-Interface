"""
Unit tests for PromptHandler classes.

Tests PromptLoader and PromptProcessor functionality including single/multi-prompt
loading, validation, and prompt creation.
"""

import json
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from src.openrouter_interface.prompt_handler import PromptLoader, PromptProcessor


class TestPromptLoader:
    """Test suite for PromptLoader class."""

    def test_load_single_prompt_file(self, sample_prompt_file):
        """Test loading a single prompt file."""
        loader = PromptLoader()
        prompt_data = loader.load_prompt(sample_prompt_file)

        assert prompt_data['instruction'].startswith("You are a content quality evaluator")
        assert prompt_data['persona'] == "Professional Content Analyst"
        assert 'evaluation_directives' in prompt_data
        assert '_multi_prompt_info' not in prompt_data

    def test_load_single_prompt_by_string_path(self, sample_prompt_file):
        """Test loading a single prompt file using string path."""
        loader = PromptLoader()
        prompt_data = loader.load_prompt(str(sample_prompt_file))

        assert prompt_data['instruction'].startswith("You are a content quality evaluator")
        assert prompt_data['persona'] == "Professional Content Analyst"

    def test_load_multiple_prompt_files(self, multiple_prompt_files):
        """Test loading multiple prompt files."""
        loader = PromptLoader()
        file_paths = [str(f) for f in multiple_prompt_files]

        prompt_data = loader.load_prompt(file_paths)

        # Should create master system prompt
        assert 'MASTER SYSTEM PROMPT' in prompt_data['instruction']
        assert 'PROMPT SECTION 1' in prompt_data['instruction']
        assert 'PROMPT SECTION 2' in prompt_data['instruction']
        assert 'PROMPT SECTION 3' in prompt_data['instruction']

        # Should include multi-prompt metadata
        assert '_multi_prompt_info' in prompt_data
        assert prompt_data['_multi_prompt_info']['combined_count'] == 3
        assert len(prompt_data['_multi_prompt_info']['source_files']) == 3

    def test_load_comma_separated_prompt_files(self, multiple_prompt_files):
        """Test loading multiple prompt files using comma-separated string."""
        loader = PromptLoader()
        file_paths_str = ','.join(str(f) for f in multiple_prompt_files)

        prompt_data = loader.load_prompt(file_paths_str)

        # Should create master system prompt
        assert 'MASTER SYSTEM PROMPT' in prompt_data['instruction']
        assert '_multi_prompt_info' in prompt_data
        assert prompt_data['_multi_prompt_info']['combined_count'] == 3

    def test_load_comma_separated_with_spaces(self, multiple_prompt_files):
        """Test loading comma-separated files with extra spaces."""
        loader = PromptLoader()
        # Add spaces around commas
        file_paths_str = ' , '.join(str(f) for f in multiple_prompt_files)

        prompt_data = loader.load_prompt(file_paths_str)

        assert '_multi_prompt_info' in prompt_data
        assert prompt_data['_multi_prompt_info']['combined_count'] == 3

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading a non-existent prompt file."""
        loader = PromptLoader()
        nonexistent_file = temp_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            loader.load_prompt(nonexistent_file)

    def test_load_invalid_json_file(self, invalid_json_file):
        """Test loading a file with invalid JSON."""
        loader = PromptLoader()

        with pytest.raises(json.JSONDecodeError):
            loader.load_prompt(invalid_json_file)

    def test_load_empty_prompt_file(self, empty_prompt_file):
        """Test loading an empty prompt file."""
        loader = PromptLoader()

        with pytest.raises(ValueError) as exc_info:
            loader.load_prompt(empty_prompt_file)

        assert "must contain a prompt field" in str(exc_info.value)

    def test_validate_prompt_missing_instruction(self, temp_dir):
        """Test validation fails when prompt lacks instruction field."""
        loader = PromptLoader()

        invalid_prompt = {
            "persona": "Test Persona",
            "output_format": "Test format"
        }

        prompt_file = temp_dir / "invalid_prompt.json"
        with open(prompt_file, 'w') as f:
            json.dump(invalid_prompt, f)

        with pytest.raises(ValueError) as exc_info:
            loader.load_prompt(prompt_file)

        assert "must contain a prompt field" in str(exc_info.value)

    def test_validate_prompt_alternative_fields(self, temp_dir):
        """Test validation passes with alternative prompt field names."""
        loader = PromptLoader()

        # Test different valid field names
        valid_alternatives = [
            {"prompt": "Test prompt content"},
            {"message": "Test message content"},
            {"content": "Test content"},
            {"task": "Test task description"},
            {"system": "Test system message"}
        ]

        for i, prompt_data in enumerate(valid_alternatives):
            prompt_file = temp_dir / f"alt_prompt_{i}.json"
            with open(prompt_file, 'w') as f:
                json.dump(prompt_data, f)

            # Should not raise exception
            result = loader.load_prompt(prompt_file)
            assert result is not None

    def test_extract_prompt_content_from_dict(self, temp_dir):
        """Test extracting prompt content when instruction is a dict."""
        loader = PromptLoader()

        prompt_with_dict_instruction = {
            "instruction": {
                "primary_task": "Analyze content",
                "secondary_task": "Provide recommendations"
            },
            "persona": "Analyst"
        }

        prompt_file = temp_dir / "dict_instruction.json"
        with open(prompt_file, 'w') as f:
            json.dump(prompt_with_dict_instruction, f)

        result = loader.load_prompt(prompt_file)

        # Dict instruction is preserved as dict in single prompt mode
        assert isinstance(result['instruction'], dict)
        assert result['instruction']['primary_task'] == "Analyze content"
        assert result['instruction']['secondary_task'] == "Provide recommendations"

    def test_get_prompt_fields(self):
        """Test that recognized prompt fields are correctly defined."""
        loader = PromptLoader()
        prompt_fields = loader._get_prompt_fields()

        expected_fields = [
            'instruction', 'instructions', 'prompt', 'message', 'content', 'text',
            'system', 'user_message', 'query', 'task', 'description'
        ]

        assert prompt_fields == expected_fields

    def test_create_master_system_prompt_format(self, multiple_prompt_files):
        """Test the format of the master system prompt."""
        loader = PromptLoader()
        file_paths = [str(f) for f in multiple_prompt_files]

        prompt_data = loader.load_prompt(file_paths)
        master_prompt = prompt_data['instruction']

        # Check structure
        assert 'MASTER SYSTEM PROMPT' in master_prompt
        assert 'Combined from Multiple Sources' in master_prompt
        assert 'PROMPT SECTION 1:' in master_prompt
        assert 'PROMPT SECTION 2:' in master_prompt
        assert 'PROMPT SECTION 3:' in master_prompt
        assert 'END OF COMBINED PROMPTS' in master_prompt
        assert 'Apply all the above prompt sections in sequence' in master_prompt

    def test_multi_prompt_metadata_structure(self, multiple_prompt_files):
        """Test the structure of multi-prompt metadata."""
        loader = PromptLoader()
        file_paths = [str(f) for f in multiple_prompt_files]

        prompt_data = loader.load_prompt(file_paths)
        metadata = prompt_data['_multi_prompt_info']

        assert 'source_files' in metadata
        assert 'combined_count' in metadata
        assert 'individual_metadata' in metadata

        assert len(metadata['source_files']) == 3
        assert metadata['combined_count'] == 3
        assert len(metadata['individual_metadata']) == 3


class TestPromptProcessor:
    """Test suite for PromptProcessor class."""

    def test_create_full_prompt_single_prompt(self, sample_prompt, sample_input_content):
        """Test creating full prompt from single prompt data."""
        processor = PromptProcessor()

        full_prompt = processor.create_full_prompt(sample_prompt, sample_input_content)

        # Should include role/persona
        assert "Role: Professional Content Analyst" in full_prompt

        # Should include main instruction
        assert "You are a content quality evaluator" in full_prompt

        # Should include evaluation directives
        assert "Evaluation Guidelines:" in full_prompt
        assert "Clarity: Assess how clearly" in full_prompt

        # Should include input content
        assert "Input content to evaluate:" in full_prompt
        assert sample_input_content in full_prompt

    def test_create_full_prompt_multi_prompt(self, multiple_prompt_files, sample_input_content):
        """Test creating full prompt from multi-prompt structure."""
        loader = PromptLoader()
        processor = PromptProcessor()

        # Load multi-prompt data
        file_paths = [str(f) for f in multiple_prompt_files]
        prompt_data = loader.load_prompt(file_paths)

        full_prompt = processor.create_full_prompt(prompt_data, sample_input_content)

        # Should include master system prompt
        assert "MASTER SYSTEM PROMPT" in full_prompt

        # Should include input content
        assert "Input content to process:" in full_prompt
        assert sample_input_content in full_prompt

        # Should include multi-prompt note
        assert "combined from" in full_prompt
        assert "source files:" in full_prompt

    def test_create_full_prompt_with_review_criteria(self, temp_dir, sample_input_content):
        """Test creating full prompt with review criteria."""
        processor = PromptProcessor()

        prompt_with_criteria = {
            "instruction": "Review the content",
            "persona": "Reviewer",
            "review_criteria": {
                "grammar": {
                    "mistake": "Grammar errors",
                    "why_problematic": "Reduces readability",
                    "how_to_fix": "Apply grammar rules"
                },
                "style": {
                    "mistake": "Poor style",
                    "why_problematic": "Less engaging",
                    "how_to_fix": "Use consistent tone"
                }
            }
        }

        full_prompt = processor.create_full_prompt(prompt_with_criteria, sample_input_content)

        # Should include review criteria
        assert "Review Criteria:" in full_prompt
        assert "grammar - Grammar errors" in full_prompt
        assert "Why problematic: Reduces readability" in full_prompt
        assert "How to fix: Apply grammar rules" in full_prompt

    def test_create_full_prompt_with_complex_instruction(self, sample_input_content):
        """Test creating full prompt with complex instruction object."""
        processor = PromptProcessor()

        prompt_with_complex_instruction = {
            "instructions": {
                "primary_task": "Analyze content quality",
                "evaluation_process": "Use systematic approach",
                "required_analysis": "Check grammar and style",
                "deliverable": "Provide recommendations"
            },
            "persona": "Quality Analyst"
        }

        full_prompt = processor.create_full_prompt(prompt_with_complex_instruction, sample_input_content)

        # Should parse complex instruction structure
        assert "Primary Task: Analyze content quality" in full_prompt
        assert "Evaluation Process: Use systematic approach" in full_prompt
        assert "Required Analysis: Check grammar and style" in full_prompt
        assert "Deliverable: Provide recommendations" in full_prompt

    def test_create_full_prompt_with_additional_fields(self, sample_input_content):
        """Test creating full prompt with various additional fields."""
        processor = PromptProcessor()

        prompt_with_extras = {
            "instruction": "Analyze content",
            "persona": "Analyst",
            "context": "Academic writing review",
            "requirements": ["Check clarity", "Verify accuracy"],
            "constraints": "Maintain original meaning",
            "examples": "Use professional tone",
            "output_format": "Structured response"
        }

        full_prompt = processor.create_full_prompt(prompt_with_extras, sample_input_content)

        # Should include additional fields in correct order
        assert "Context:\nAcademic writing review" in full_prompt
        assert "Requirements:\n- Check clarity\n- Verify accuracy" in full_prompt
        assert "Constraints:\nMaintain original meaning" in full_prompt
        assert "Output Format:\nStructured response" in full_prompt

    def test_add_structured_field_with_list(self):
        """Test formatting of list fields."""
        processor = PromptProcessor()

        full_prompt = "Initial prompt"
        prompt_data = {"requirements": ["Item 1", "Item 2", "Item 3"]}
        processed_fields = set()

        result = processor._add_structured_field(
            full_prompt, prompt_data, "requirements", processed_fields
        )

        assert "Requirements:\n- Item 1\n- Item 2\n- Item 3" in result
        assert "requirements" in processed_fields

    def test_add_structured_field_with_dict(self):
        """Test formatting of dictionary fields."""
        processor = PromptProcessor()

        full_prompt = "Initial prompt"
        prompt_data = {"context": {"type": "academic", "domain": "science"}}
        processed_fields = set()

        result = processor._add_structured_field(
            full_prompt, prompt_data, "context", processed_fields
        )

        # Should convert dict to JSON
        assert "Context:" in result
        assert '"type": "academic"' in result
        assert '"domain": "science"' in result

    def test_format_field_value_types(self):
        """Test _format_field_value with different data types."""
        processor = PromptProcessor()

        # Test string
        assert processor._format_field_value("simple string") == "simple string"

        # Test list
        result = processor._format_field_value(["a", "b", "c"])
        assert result == "- a\n- b\n- c"

        # Test dict
        result = processor._format_field_value({"key": "value"})
        assert '"key": "value"' in result

    def test_create_single_prompt_fallback_fields(self, sample_input_content):
        """Test fallback behavior when standard fields are missing."""
        processor = PromptProcessor()

        # Prompt with non-standard field names
        prompt_with_fallback = {
            "custom_instruction": "This is the instruction",
            "persona": "Test Persona"
        }

        full_prompt = processor.create_full_prompt(prompt_with_fallback, sample_input_content)

        # Should use the custom field as instruction
        assert "This is the instruction" in full_prompt
        assert "Role: Test Persona" in full_prompt

    def test_create_full_prompt_preserves_field_processing(self, sample_input_content):
        """Test that processed fields are not duplicated."""
        processor = PromptProcessor()

        prompt_data = {
            "instruction": "Main instruction",
            "persona": "Test Persona",
            "evaluation_directives": {"clarity": "Check clarity"},
            "extra_field": "Should be included once"
        }

        full_prompt = processor.create_full_prompt(prompt_data, sample_input_content)

        # Count occurrences to ensure no duplication
        assert full_prompt.count("Main instruction") == 1
        assert full_prompt.count("Test Persona") == 1
        assert full_prompt.count("Should be included once") == 1


@pytest.mark.unit
class TestPromptHandlerEdgeCases:
    """Test edge cases and error conditions for prompt handling."""

    def test_load_prompt_with_permission_error(self, temp_dir):
        """Test handling of permission errors."""
        loader = PromptLoader()

        # Mock open to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                loader.load_prompt(temp_dir / "test.json")

    def test_load_mixed_valid_invalid_files(self, temp_dir, sample_prompt):
        """Test loading mix of valid and invalid files."""
        loader = PromptLoader()

        # Create one valid and one invalid file
        valid_file = temp_dir / "valid.json"
        invalid_file = temp_dir / "invalid.json"

        with open(valid_file, 'w') as f:
            json.dump(sample_prompt, f)

        with open(invalid_file, 'w') as f:
            f.write('invalid json content')

        # Should fail on the invalid file
        with pytest.raises(json.JSONDecodeError):
            loader.load_prompt([str(valid_file), str(invalid_file)])

    def test_create_full_prompt_empty_input(self, sample_prompt):
        """Test creating full prompt with empty input content."""
        processor = PromptProcessor()

        full_prompt = processor.create_full_prompt(sample_prompt, "")

        # Should still create valid prompt structure
        assert "You are a content quality evaluator" in full_prompt
        assert "Input content to evaluate:" in full_prompt

    def test_create_full_prompt_very_long_input(self, sample_prompt):
        """Test creating full prompt with very long input content."""
        processor = PromptProcessor()

        # Create very long input (10,000 characters)
        long_input = "A" * 10000

        full_prompt = processor.create_full_prompt(sample_prompt, long_input)

        # Should handle long input without issues
        assert long_input in full_prompt
        assert len(full_prompt) > 10000

    def test_prompt_with_unicode_content(self, temp_dir, sample_input_content):
        """Test handling of unicode characters in prompts."""
        loader = PromptLoader()
        processor = PromptProcessor()

        unicode_prompt = {
            "instruction": "Analysez le contenu 🔍",
            "persona": "Analyseur français 🇫🇷",
            "output_format": "Réponse structurée"
        }

        prompt_file = temp_dir / "unicode_prompt.json"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            json.dump(unicode_prompt, f, ensure_ascii=False)

        prompt_data = loader.load_prompt(prompt_file)
        full_prompt = processor.create_full_prompt(prompt_data, sample_input_content)

        # Should preserve unicode characters
        assert "Analysez le contenu 🔍" in full_prompt
        assert "Analyseur français 🇫🇷" in full_prompt