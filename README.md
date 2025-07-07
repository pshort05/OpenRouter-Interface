# OpenRouter Interface Suite - Modular Architecture

This suite provides two main applications for working with the OpenRouter API: a text editor for processing files and a prompt runner for executing JSON-based prompts. Both applications have been refactored into modular architectures for better maintainability and organization.

## Applications Overview

### 1. OpenRouter Text Editor
Processes text files based on action specifications using the OpenRouter API. Includes advanced features like text chunking for large files and compliance checking.

### 2. OpenRouter Prompt Runner
Scans for JSON prompt files and executes them against input files using the OpenRouter API. Designed for interactive prompt testing and analysis with comprehensive output handling.

## File Structure

```
openrouter_interface/
├── openrouter_editor.py           # Text editor main orchestrator
├── prompt_runner.py               # Prompt runner main application
├── config_manager.py              # Configuration handling (shared)
├── logging_manager.py             # Logging setup and management (shared)
├── file_handler.py               # File I/O operations (shared)
├── prompt_builder.py             # API prompt creation (editor)
├── api_client.py                 # OpenRouter API communication (editor)
├── prompt_runner_api_client.py   # Prompt runner API client
├── text_chunker.py               # Large file chunking functionality (editor)
├── compliance_checker.py         # Output compliance analysis (editor)
├── prompt_scanner.py             # JSON prompt file scanning (runner)
├── prompt_handler.py             # Prompt loading and processing (runner)
├── input_handler.py              # Input file selection (runner)
├── response_handler.py           # Response output management (runner)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## OpenRouter Text Editor Modules

### `openrouter_editor.py`
- Main orchestrator and entry point for text editing operations
- Coordinates all modules for file processing workflows

### `config_manager.py` (Shared)
- Loads configuration from YAML files
- Manages default configuration values
- Handles API key retrieval from environment variables or config files
- Provides configuration access methods

### `logging_manager.py` (Shared)
- Sets up logging configuration based on config settings
- Supports both file and console logging
- Configurable log levels and formatting

### `file_handler.py` (Shared)
- Handles all file I/O operations
- Loads input text files and action configurations
- Saves output files and API payloads
- Creates directories as needed

### `prompt_builder.py`
- Creates API prompts based on action configurations
- Handles different action types (edit, rewrite, summarize, translate)
- Processes custom instructions and requirements
- Adds constraints, examples, and formatting instructions

### `api_client.py`
- Manages OpenRouter API communication for text editing
- Handles request/response processing
- Removes AI commentary from responses
- Provides detailed logging of API interactions
- Manages error handling and timeouts

### `text_chunker.py`
- Splits large text files into manageable chunks for processing
- Maintains paragraph boundaries and preserves document structure
- Combines processed chunks back into a single output file
- Configurable chunk size and intelligent text splitting
- Supports front matter preservation and metadata handling
- Provides cleanup options for intermediate files

### `compliance_checker.py`
- Analyzes how well the output conforms to original action specifications
- Compares processed text against the requirements in action.json
- Generates detailed compliance reports with scoring and recommendations
- Uses AI analysis to evaluate specification adherence
- Provides quality assessment and deviation analysis
- Supports batch compliance checking for chunked files

## OpenRouter Prompt Runner Modules

### `prompt_runner.py`
- Main application for interactive prompt execution
- Orchestrates all prompt runner modules
- Provides interactive session management with user menus
- Handles workflow from prompt selection to response output

### `prompt_scanner.py`
- Scans directories for JSON prompt files
- Displays interactive menus for prompt selection
- Provides user-friendly file browsing and selection interface
- Supports alphabetical sorting and file size display

### `prompt_handler.py`
- **PromptLoader**: Loads and validates JSON prompt files
- **PromptProcessor**: Processes complex prompt structures and creates full prompts
- Handles multiple prompt field formats (instruction, instructions, prompt, etc.)
- Supports complex JSON structures with nested objects
- Processes structured fields like persona, evaluation_directives, review_criteria
- Validates prompt file structure and provides helpful error messages

### `input_handler.py`
- **InputFileHandler**: Manages input file selection and loading
- Interactive file path input with validation
- Handles file existence checking and error reporting
- Supports quoted paths and various file formats
- Provides user-friendly error messages and retry logic

### `prompt_runner_api_client.py`
- **PromptAPIClient**: Handles OpenRouter API communication for prompt runner
- Preserves all AI commentary and output (unlike the editor's API client)
- Provides detailed API interaction logging
- Saves request payloads for debugging and analysis
- Manages timeouts, error handling, and response processing

### `response_handler.py`
- **ResponseHandler**: Manages response output to console and files
- Streams responses to console with formatted headers
- Optionally appends responses to markdown output files
- Adds timestamps, prompt file names, and input file references
- Creates markdown-formatted entries with proper separation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure all module files are in the same directory as the main applications

3. Set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

## Usage

### OpenRouter Text Editor

```bash
# Basic usage with default config
python openrouter_editor.py

# With custom configuration
python openrouter_editor.py -c my_config.yaml
```

### OpenRouter Prompt Runner

```bash
# Basic interactive session
python prompt_runner.py

# Save responses to markdown file
python prompt_runner.py -o responses.md

# Save to specific output file
python prompt_runner.py --output-file analysis_results.md
```

### Prompt Runner Workflow

The prompt runner follows this interactive workflow:

1. **Scan for JSON files**: Automatically finds all .json files in the current directory
2. **Display menu**: Shows numbered list of available prompt files with file sizes
3. **Prompt selection**: User selects a prompt file by number or quits with 'q'
4. **Input file selection**: User provides path to input file for processing
5. **Validation**: Validates both prompt structure and input file existence
6. **API execution**: Sends combined prompt and input to OpenRouter API
7. **Response streaming**: Displays response to console with formatted headers
8. **File output**: Optionally saves responses to markdown file with timestamps
9. **Continue option**: Asks user if they want to run another prompt

### JSON Prompt File Structure

The prompt runner supports flexible JSON prompt structures. Here are the recognized fields:

#### Primary Prompt Fields (in order of preference):
- `instruction` / `instructions`
- `prompt`
- `message`
- `content`
- `text`
- `system`
- `user_message`
- `query`
- `task`
- `description`

#### Special Structure Fields:
- `persona` - Added as role definition at the beginning
- `instructions` - Can be a complex object with `primary_task`, `evaluation_process`, etc.
- `evaluation_directives` - Formatted as guidelines
- `review_criteria` - Structured criteria with explanations
- `genre_adaptation` - Context-specific adaptations
- `context`, `requirements`, `constraints`, `examples`, `output_format` - Standard structured fields

#### Example JSON Prompt Structure:
```json
{
  "title": "Example Prompt",
  "persona": "You are an expert...",
  "instructions": {
    "primary_task": "Analyze the following...",
    "evaluation_process": "Systematically assess...",
    "deliverable": "Provide a comprehensive..."
  },
  "evaluation_directives": {
    "tone": "Be honest and incisive...",
    "output_goal": "Provide clear recommendations..."
  },
  "review_criteria": {
    "1. First Criterion": {
      "mistake": "Description of what to look for",
      "why_problematic": "Why this is an issue",
      "how_to_fix": "How to address it"
    }
  }
}
```

## Configuration Examples

### Text Editor Configuration
```yaml
# openrouter_editor.yaml
input_file: 'input.md'
output_file: 'output.md'
action_file: 'action.json'
model: 'anthropic/claude-4-sonnet-20250522'
temperature: 0.8
max_tokens: 10000
enable_chunking: true
chunk_size: 1500
enable_compliance_check: true
compliance_output_file: 'quality_report.md'
```

### Prompt Runner Configuration
The prompt runner uses minimal configuration and primarily operates interactively:
```yaml
# Not typically needed - prompt runner auto-configures
model: 'anthropic/claude-4-sonnet-20250522'
api_base_url: 'https://openrouter.ai/api/v1'
temperature: 0.8
max_tokens: 10000
```

## Benefits of Modular Structure

1. **Single Responsibility**: Each module has a clear, focused purpose
2. **Maintainability**: Easier to modify individual components without affecting others
3. **Testability**: Each module can be tested independently
4. **Reusability**: Modules can be shared between applications and reused in other projects
5. **Readability**: Smaller files are easier to understand and navigate
6. **Extensibility**: New features can be added by creating new modules or extending existing ones
7. **Separation of Concerns**: Text editing and prompt running have distinct workflows and requirements

## Dependencies

### Core Dependencies
- `requests>=2.25.0` - For API communication
- `PyYAML>=5.4.0` - For configuration file parsing

### Optional Features (Text Editor)
- **Text Chunking**: Requires `text_chunker.py` for large file processing
- **Compliance Checking**: Requires `compliance_checker.py` for output analysis

### Shared Modules
The following modules are shared between both applications:
- `config_manager.py`
- `logging_manager.py`
- `file_handler.py`

## Workflow Examples

### Text Editor Workflows

#### Basic Processing
```bash
python openrouter_editor.py
```

#### Processing with Chunking
```yaml
# openrouter_editor.yaml
enable_chunking: true
chunk_size: 1500
input_file: 'large_document.md'
output_file: 'processed_document.md'
```

#### Complete Workflow (Chunking + Compliance)
```yaml
# openrouter_editor.yaml
enable_chunking: true
enable_compliance_check: true
chunk_size: 1000
input_file: 'large_book.md'
output_file: 'edited_book.md'
compliance_output_file: 'editing_analysis.md'
```

### Prompt Runner Workflows

#### Interactive Analysis Session
```bash
python prompt_runner.py -o session_results.md
```

The system will:
1. Show available JSON prompt files
2. Let you select prompts and input files interactively
3. Execute prompts against inputs
4. Save all responses with timestamps to `session_results.md`
5. Allow multiple prompt executions in one session

#### Batch Analysis
You can run multiple different prompts against the same input file in one session, with all results saved to a single output file for comparison.

## Error Handling

Each module handles its own errors and provides meaningful error messages:

- **Prompt Runner**: Validates JSON structure, checks file existence, provides helpful suggestions for missing fields
- **Text Editor**: Handles file I/O errors, API timeouts, and configuration issues
- **Shared Modules**: Provide consistent error reporting and logging across both applications

The main orchestrators catch and log any unhandled exceptions while maintaining system stability.

## Advanced Features

### Prompt Runner Features
- **Complex JSON Support**: Handles nested objects and flexible prompt structures
- **Preserved Commentary**: Keeps all AI commentary and reasoning in responses
- **Interactive Workflow**: User-friendly menu system with file validation
- **Markdown Output**: Formatted output files with timestamps and metadata
- **Session Management**: Multiple prompts in one session with continue/quit options

### Text Editor Features
- **AI Commentary Removal**: Strips non-essential AI commentary for cleaner output
- **Chunking Support**: Processes large files by splitting into manageable pieces
- **Compliance Analysis**: Evaluates how well output meets original specifications
- **Batch Processing**: Handles multiple chunks with automated reassembly