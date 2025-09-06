# BookGen Utilities

AI-powered book generation utilities for creating and editing book chapters using the OpenRouter API.

## Overview

This package provides two main utilities for book writing and editing:

- **`bookGen.py`** - Main application for generating book chapters using AI models
- **`bookFileManager.py`** - Standalone file management class for book content operations

## Features

- **AI-Powered Generation**: Use any OpenRouter-supported AI model (Claude, GPT-4, Gemini, etc.)
- **Smart Text Chunking**: Automatically breaks large chapters into processable chunks
- **Flexible Configuration**: YAML-based configuration with environment variable support
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Action-Based Prompts**: JSON-defined prompts for specific editing actions
- **Markdown Support**: Native Markdown input/output format

## Installation

### Prerequisites

```bash
# Install required Python dependencies
pip install requests PyYAML
```

### Environment Setup

Set your OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

Alternatively, configure it in `bookGen.yaml` (less secure).

## Usage

### Basic Usage

```bash
# Generate chapter with default configuration
python bookGen.py

# Use custom configuration file
python bookGen.py -c my_config.yaml
```

### Required Files

1. **Configuration File** (`bookGen.yaml`)
2. **Input Chapter** (`chapter_input.md`) - Existing chapter content or outline
3. **Action Prompt** (`action_prompt.json`) - Instructions for the AI

### Configuration File (`bookGen.yaml`)

```yaml
# API Configuration
openrouter_api_key: "sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Optional if using env var
model: "anthropic/claude-4-sonnet-20250522"
api_base_url: "https://openrouter.ai/api/v1/chat/completions"

# File Paths
input_chapter_file: "chapter_input.md"
action_prompt_file: "action_prompt.json" 
output_chapter_file: "chapter_output.md"

# Model Parameters
temperature: 1.0
max_tokens: 10000

# Logging
log_level: "INFO"
```

### Action Prompt File (`action_prompt.json`)

```json
{
  "action": "write",
  "instructions": "Continue writing the next section of this chapter, maintaining the established tone and style. Focus on character development and advancing the plot."
}
```

Available actions:
- `write` - Generate new content
- `edit` - Revise existing content
- `expand` - Add detail to existing content
- `summarize` - Create chapter summaries
- `analyze` - Analyze writing style or structure

## Key Features

### Smart Text Chunking

For chapters longer than 1500 words, the system automatically:
- Splits text at natural paragraph breaks
- Maintains context between chunks
- Processes each chunk individually
- Reassembles output seamlessly

**Chunking Parameters:**
- `max_words`: 1000 (maximum words per chunk)
- `min_words_before_break`: 975 (minimum words before looking for break point)

### File Management

The `BookFileManager` class handles:
- Reading Markdown and JSON files
- Writing/appending to output files
- Text chunking operations
- Error handling and validation

### Logging and Monitoring

- **API Call Timing**: Logs duration of each API request
- **Chunk Processing**: Progress tracking for multi-chunk operations
- **Error Handling**: Comprehensive error logging with context
- **Configurable Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Supported Models

Works with 400+ AI models via OpenRouter, including:
- **Anthropic**: Claude 3/4 (Opus, Sonnet, Haiku)
- **OpenAI**: GPT-4, GPT-3.5
- **Google**: Gemini Pro, PaLM
- **Meta**: Llama 2/3
- **Cohere**: Command
- **And many more**

## File Structure

```
project/
├── bookGen.py              # Main application
├── bookFileManager.py      # File management utilities
├── bookGen.yaml           # Configuration file
├── chapter_input.md       # Input chapter content
├── action_prompt.json     # AI instructions
└── chapter_output.md      # Generated output
```

## Advanced Usage

### Custom File Paths

Modify `bookGen.yaml` to use different file paths:

```yaml
input_chapter_file: "drafts/chapter_01.md"
action_prompt_file: "prompts/editing_prompt.json"
output_chapter_file: "output/chapter_01_revised.md"
```

### Model Parameters

Fine-tune AI behavior:

```yaml
temperature: 0.7    # More focused output (0.1-2.0)
max_tokens: 5000   # Shorter responses
```

### Logging Configuration

Enable debug logging for troubleshooting:

```yaml
log_level: "DEBUG"
```

## Standalone BookFileManager

The `BookFileManager` class can be used independently:

```python
from bookFileManager import BookFileManager

config = {
    'input_chapter_file': 'my_chapter.md',
    'output_chapter_file': 'output.md'
}

manager = BookFileManager(config)
content = manager.get_input_chapter_content()
chunks = manager.chunk_text_by_paragraphs(content)
```

## Error Handling

The system handles:
- **Missing Files**: Clear error messages with file paths
- **Invalid JSON**: JSON parsing error details
- **API Failures**: Network error handling with retry information
- **Configuration Errors**: YAML parsing and validation
- **Authentication**: API key validation

## Security

- **API Key Protection**: Prioritizes environment variables over config files
- **Input Validation**: Validates all file inputs and configurations
- **Error Isolation**: Prevents sensitive information from appearing in logs

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   Error: OpenRouter API key not found
   ```
   Solution: Set `OPENROUTER_API_KEY` environment variable

2. **File Not Found**
   ```
   Input Markdown file not found at 'chapter_input.md'
   ```
   Solution: Ensure all required files exist in the specified paths

3. **JSON Parse Error**
   ```
   Error parsing JSON prompt file
   ```
   Solution: Validate JSON syntax using `python -m json.tool action_prompt.json`

### Debug Mode

Enable detailed logging:

```bash
# Set debug level in config
log_level: "DEBUG"

# Run with verbose output
python bookGen.py -c bookGen.yaml
```

## Integration

This utility integrates with the broader OpenRouter Interface ecosystem and can be combined with other prompt management tools in the system.