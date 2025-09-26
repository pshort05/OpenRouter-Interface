# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running and Testing
```bash
# CLI usage - Single and multi-prompt support
PYTHONPATH=src python3 -m openrouter_interface.cli --help
PYTHONPATH=src python3 -m openrouter_interface.cli -p prompts/content_quality.json -i test_input.md
PYTHONPATH=src python3 -m openrouter_interface.cli -p "prompts/quality.json,prompts/grammar.json" -i test_input.md

# Web interface
PYTHONPATH=src python3 -m openrouter_interface.web --help
./start-web.sh  # Start web server with proper configuration

# Chain runner - Multi-prompt chain support
PYTHONPATH=src python3 -m openrouter_interface.chain --help
PYTHONPATH=src python3 -m openrouter_interface.chain --create-sample
PYTHONPATH=src python3 -m openrouter_interface.chain -c multi_prompt_chain_test.yaml --debug

# Global commands (after install-global.sh)
openrouter-runner --help
openrouter-web --help
openrouter-chain --help
```

### Installation and Setup
```bash
# Local development (virtual environment)
./install.sh web

# Global installation
./install-global.sh

# Set API key
./setup-api-key.sh
export OPENROUTER_API_KEY="your-api-key-here"
```

### Testing
```bash
# Run tests
pytest
pytest --cov=openrouter_interface

# Code quality
black src tests
flake8 src
mypy src
```

## Architecture Overview

### Core Package Structure
- **src/openrouter_interface/**: Main Python package following modern packaging standards
- **Entry points**: cli.py, web.py, chain.py, bookGen.py - each provides a main() function
- **Core engine**: prompt_runner.py - central processing logic for all interfaces
- **Configuration**: config_manager.py handles YAML configs, API keys, and runtime settings
- **API layer**: api_client.py and prompt_runner_api_client.py manage OpenRouter communication

### Key Components

**PromptRunner (prompt_runner.py)**
- Central orchestrator for all prompt processing
- Handles batch mode, interactive mode, and web requests
- Manages text chunking, file I/O, and API communication
- Used by all interfaces (CLI, web, chain)

**Chain Runner (prompt_chain_runner.py)**
- Multi-step workflow execution engine
- YAML-based configuration for prompt sequences
- Progress tracking and intermediate file management
- Background execution support for long-running processes

**Web Interface (prompt_runner_flask.py)**
- Flask-based web UI with real-time progress tracking
- Chain creation and monitoring dashboard
- Session management and file upload/download
- Background task execution with status persistence

**Configuration System**
- YAML-based configs in config/ directory
- Environment variable support (OPENROUTER_API_KEY)
- Model-specific configurations (claude_config.yaml, gpt4_config.yaml)
- Runtime parameter override support

### Data Flow
1. **Input**: JSON prompts from prompts/ directory define AI tasks
2. **Configuration**: YAML files specify models, parameters, and chains
3. **Processing**: PromptRunner coordinates text chunking, API calls, and response handling
4. **Output**: Processed text files with configurable naming and format

### Integration Points
- **Flask web app**: Uses prompt_runner_flask.py as main controller
- **CLI**: Direct integration via cli.py -> prompt_runner.py
- **Chain processing**: prompt_chain_runner.py orchestrates multiple PromptRunner calls
- **Book generation**: bookGen.py provides specialized workflows for chapter processing

### Important Patterns
- All modules use ConfigManager for consistent configuration handling
- LoggingManager provides unified logging across components
- Text chunking automatically handles large documents
- API client abstraction allows easy model switching
- Background processing supported for long-running chains

## Configuration Files

### Main Config (config/config.yaml)
```yaml
model_name: anthropic/claude-4-sonnet-20250522
logging_level: INFO
max_tokens: 25000
```

### Model-Specific Configs
- config/claude_config.yaml
- config/gpt4_config.yaml
- config/deepseek_config.yaml

### Chain Configs
- Multi-step workflow definitions
- Input/output file specifications
- Model selection per step
- **Multi-prompt support**: Each chain step can use comma-separated prompt files
- Progress tracking configuration

### Multi-Prompt Chain Configuration
```yaml
prompts:
  prompt 1:
    name: "comprehensive_analysis"
    prompt_file: "quality_check.json,grammar_fix.json"  # Combines two prompts
  prompt 2:
    name: "style_enhancement"
    prompt_file: "style_guide.json,tone_adjust.json,readability.json"  # Combines three prompts
  prompt 3:
    prompt_file: "final_polish.json"  # Single prompt
```

## Environment Variables
- **OPENROUTER_API_KEY**: Required for API access
- **OPENROUTER_MODEL**: Override default model
- **OPENROUTER_LOG_LEVEL**: Override logging level

## Package Entry Points
Defined in pyproject.toml:
- openrouter-runner = "openrouter_interface.cli:main"
- openrouter-web = "openrouter_interface.web:main"
- openrouter-chain = "openrouter_interface.chain:main"
- bookgen = "openrouter_interface.bookGen:main"