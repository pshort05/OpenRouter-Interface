# OpenRouter Text Editor - Modular Structure

The OpenRouter Text Editor has been refactored into a modular architecture for better maintainability and organization. It includes advanced features like text chunking for large files and compliance checking to ensure output quality.

## File Structure

```
openrouter_editor/
├── openrouter_editor.py      # Main orchestrator (entry point)
├── config_manager.py         # Configuration handling
├── logging_manager.py        # Logging setup and management
├── file_handler.py          # File I/O operations
├── prompt_builder.py        # API prompt creation
├── api_client.py            # OpenRouter API communication
├── text_chunker.py          # Large file chunking functionality
├── compliance_checker.py    # Output compliance analysis
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Module Responsibilities

### `config_manager.py`
- Loads configuration from YAML files
- Manages default configuration values
- Handles API key retrieval from environment variables or config files
- Provides configuration access methods

### `logging_manager.py`
- Sets up logging configuration based on config settings
- Supports both file and console logging
- Configurable log levels and formatting

### `file_handler.py`
- Handles all file I/O operations
- Loads input text files
- Loads action configuration from JSON
- Saves output files and API payloads
- Creates directories as needed

### `prompt_builder.py`
- Creates API prompts based on action configurations
- Handles different action types (edit, rewrite, summarize, translate)
- Processes custom instructions and requirements
- Adds constraints, examples, and formatting instructions

### `api_client.py`
- Manages OpenRouter API communication
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

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure all module files are in the same directory as `openrouter_editor.py`

## Usage

The usage remains the same as before:

```bash
python openrouter_editor.py
python openrouter_editor.py -c my_config.yaml
```

## Benefits of Modular Structure

1. **Single Responsibility**: Each module has a clear, focused purpose
2. **Maintainability**: Easier to modify individual components without affecting others
3. **Testability**: Each module can be tested independently
4. **Reusability**: Modules can be reused in other projects
5. **Readability**: Smaller files are easier to understand and navigate
6. **Extensibility**: New features can be added by creating new modules or extending existing ones

## Dependencies

The optional modules `text_chunker.py` and `compliance_checker.py` are imported dynamically when needed. If they're not available, the system gracefully falls back to basic functionality.

### Core Dependencies
- `requests>=2.25.0` - For API communication
- `PyYAML>=5.4.0` - For configuration file parsing

### Optional Features
- **Text Chunking**: Requires `text_chunker.py` for large file processing
- **Compliance Checking**: Requires `compliance_checker.py` for output analysis

## Workflow Examples

### Basic Processing
```bash
python openrouter_editor.py
```

### Processing with Chunking
For large files, enable chunking in your config:
```yaml
# openrouter_editor.yaml
enable_chunking: true
chunk_size: 1500
input_file: 'large_document.md'
output_file: 'processed_document.md'
```

### Processing with Compliance Checking
```yaml
# openrouter_editor.yaml
enable_compliance_check: true
compliance_output_file: 'quality_report.md'
```

### Complete Workflow (Chunking + Compliance)
```yaml
# openrouter_editor.yaml
enable_chunking: true
enable_compliance_check: true
chunk_size: 1000
input_file: 'large_book.md'
output_file: 'edited_book.md'
compliance_output_file: 'editing_analysis.md'
```

The system will:
1. Split `large_book.md` into chunks
2. Process each chunk according to `action.json`
3. Run compliance checks on each processed chunk
4. Combine all processed chunks into `edited_book.md`
5. Combine all compliance analyses into `editing_analysis.md`
6. Clean up intermediate files

## Error Handling

Each module handles its own errors and provides meaningful error messages. The main orchestrator catches and logs any unhandled exceptions while maintaining system stability.