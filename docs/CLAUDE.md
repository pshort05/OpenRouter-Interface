# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Quick automated setup (recommended)
chmod +x setup_prompt_runner.sh
./setup_prompt_runner.sh

# Create Flask templates and config
python create_templates.py
```

### Running Applications

#### CLI Interface
```bash
# Interactive mode - scan and select prompts
python prompt_runner.py

# Batch mode - process specific files
python prompt_runner.py -p analysis.json -i document.md -o results.md

# With logging and config
python prompt_runner.py -p review.json -i code.py -c config.yaml -l debug.log -v
```

#### Web Interface
```bash
# Quick start with shell script
chmod +x prompt_runner_flask.sh
./prompt_runner_flask.sh --setup    # Initial setup
./prompt_runner_flask.sh            # Start server

# Direct Flask execution
python prompt_runner_flask.py
```

#### Prompt Chain Execution
```bash
# Run multiple prompts in sequence
python prompt_chain_runner.py -c chain_config.yaml -i input.md -o final_output.md
```

### Testing and Validation
```bash
# Validate JSON prompt files
python -m json.tool prompt_file.json

# Test API connectivity
python api_client.py

# Check configuration
python config_manager.py
```

## Code Architecture

This is a Python-based OpenRouter API interface with multiple execution modes and comprehensive prompt management.

### Core Application Structure

**Main Applications:**
- `prompt_runner.py` - CLI application with interactive/batch modes
- `prompt_runner_flask.py` - Web application with modern UI
- `prompt_chain_runner.py` - Sequential prompt execution engine

**Core Module Dependencies (Required for all applications):**
- `config_manager.py` - YAML configuration handling
- `logging_manager.py` - Centralized logging system
- `prompt_scanner.py` - JSON prompt file discovery
- `prompt_handler.py` - Prompt loading and processing
- `input_handler.py` - Input file management
- `response_handler.py` - Output formatting and saving
- `file_handler.py` - File operations utilities

**API Clients:**
- `prompt_runner_api_client.py` - OpenRouter API client for prompt runner
- `api_client.py` - General OpenRouter API client
- `openrouter_client.py` - Legacy OpenRouter client

### Application-Specific Files

**Flask Web Interface:**
- `create_templates.py` - HTML template generator
- `flask_config.yaml` - Web app configuration
- `prompts_registry.yaml` - Prompt registry management
- `templates/` - HTML templates directory

**Legacy Applications:**
- `openrouter_editor.py` - Original text editor interface
- `generateProse.py` - Prose generation utility
- `bookGen.py` - Book generation system
- `callAPI.py` - Basic API caller

### Configuration System

**Primary Config Files:**
- `config.yaml` - Main application configuration
- `openrouter_editor.yaml` - Prompt runner specific settings
- `flask_config.yaml` - Web interface settings
- `bookGen.yaml` - Book generation configuration

**Configuration Priority (CLI):**
1. Command line arguments (highest)
2. YAML config files
3. Environment variables
4. Default values

### JSON Prompt System

The system uses JSON files for prompt definitions with flexible structure:
- Prompts are auto-discovered by scanning directory
- Support for complex prompt templates and requirements
- Batch processing capabilities for multiple files
- Interactive selection in CLI mode

### Key Features

**Multi-Interface Architecture:**
- CLI for automation/scripting
- Web interface for interactive use  
- Prompt chains for sequential processing

**Robust Configuration Management:**
- YAML-based configuration
- Command-line overrides
- Environment variable support

**Comprehensive Logging:**
- File and console logging
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Session tracking for batch operations

**File Validation and Error Handling:**
- Comprehensive input validation
- Graceful error recovery
- Detailed error messaging

## Environment Requirements

**Required Environment Variables:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key (required)

**Python Dependencies:**
- `requests>=2.25.0` - HTTP client for API calls
- `PyYAML>=5.4.0` - YAML configuration parsing
- `flask` - Web framework (for web interface only)

**Supported Models:**
The system supports 400+ AI models via OpenRouter.ai, including Claude, GPT-4, Gemini, DeepSeek, Llama, and others. Default model is `anthropic/claude-4-sonnet-20250522`.

## File Organization

**Execution Modes:**
- Interactive CLI mode for file selection and experimentation
- Batch CLI mode for automated processing and CI/CD
- Web interface for team collaboration and visual feedback
- Prompt chaining for complex multi-step operations

**Output Management:**
- Markdown formatted responses
- Session history tracking (web interface)
- Comprehensive logging with timestamps
- Configurable output file naming

## Development Best Practices

### Testing and Validation Commands
```bash
# Validate JSON prompt files before using
python -m json.tool [prompt_file].json

# Test API connectivity
python api_client.py

# Validate configuration files
python config_manager.py

# Test prompt chain configurations
python prompt_chain_runner.py -c chain_config.yaml --validate
```

### Debugging Commands
```bash
# Debug API issues with verbose logging
python prompt_runner.py -p debug_prompt.json -i test.md -l debug.log -v

# Check Flask template setup
python create_templates.py --verify

# Monitor Flask app in development
./prompt_runner_flask.sh -d -l
```

### Security Requirements
- **API Keys**: Always use environment variables (`OPENROUTER_API_KEY`), never store in config files
- **File Permissions**: Ensure proper read/write permissions for logs and output directories
- **Input Validation**: All JSON prompts and input files are validated before processing

### Development Workflow
1. **Always validate JSON prompts** before testing with `python -m json.tool`
2. **Use verbose logging** (`-v` flag) when debugging API issues
3. **Test configuration changes** with `config_manager.py` before deployment
4. **Prefer editing existing files** over creating new ones
5. **Run setup scripts** (`./setup_prompt_runner.sh`) after major changes