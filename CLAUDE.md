# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenRouter Interface is a Python toolkit for AI language model processing through the OpenRouter API. It provides:

- **CLI Interface**: Single and multi-prompt processing (`openrouter-runner`)
- **Web Interface**: Flask-based dashboard (`openrouter-web`)
- **Chain Processing**: Multi-step workflows (`openrouter-chain`)
- **Script Integration**: Pre/post processing automation
- **Advanced Features**: Multi-pass, content append, variable substitution

## Key Architecture

### Core Components
- **src/openrouter_interface/**: Main Python package
- **prompt_runner.py**: Core processing engine for single prompts
- **prompt_chain_runner.py**: Chain execution with multi-step workflows
- **config_manager.py**: YAML configuration handling
- **api_client.py**: OpenRouter API communication

### Entry Points (pyproject.toml)
- `openrouter-runner` = CLI interface for single prompts
- `openrouter-web` = Web interface launcher
- `openrouter-chain` = Chain execution engine
- `bookgen` = Specialized book generation workflows

## Development Commands

### Installation and Setup
```bash
# Local development (virtual environment)
./install.sh web

# Global installation
./install-global.sh

# Set API key
export OPENROUTER_API_KEY="your-api-key-here"
./setup-api-key.sh
```

### Running and Testing
```bash
# CLI usage - Single and multi-prompt support
PYTHONPATH=src python3 -m openrouter_interface.cli -p prompts/test.json -i input.md -o output.md
PYTHONPATH=src python3 -m openrouter_interface.cli -p "prompts/quality.json,prompts/grammar.json" -i input.md

# CLI with parameter overrides
PYTHONPATH=src python3 -m openrouter_interface.cli -p prompts/analysis.json -i input.md --temperature 0.2 --max-tokens 30000

# Web interface
PYTHONPATH=src python3 -m openrouter_interface.web --help
./start-web.sh

# Chain runner - Multi-prompt chain support
PYTHONPATH=src python3 -m openrouter_interface.chain --help
PYTHONPATH=src python3 -m openrouter_interface.chain --create-sample
PYTHONPATH=src python3 -m openrouter_interface.chain -c config.yaml --debug

# Global commands (after install-global.sh)
openrouter-runner --help
openrouter-web --help
openrouter-chain --help
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

## Configuration Files

### Main Config (config/config.yaml)
```yaml
model: anthropic/claude-4-sonnet-20250522
temperature: 0.8
max_tokens: 25000
logging_level: INFO

# Advanced parameters (optional)
top_p: 0.9
frequency_penalty: 0.1
presence_penalty: 0.1
```

### Chain Config Example
```yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

input_file: input.md
output_file: output.md

# Global pre/post processing
preprocessing:
  script01: echo "Starting processing"
  name01: "Initialize"

postprocessing:
  script01: echo "Processing complete"
  name01: "Cleanup"

prompts:
  prompt 1:
    prescript: "touch {input_file}.backup"
    name: "grammar_foundation"
    prompt_file: "prompts/grammar.json"
    temperature: 0.2
    passes: 2
    append: yes
    postscript: "wc -l {output_file} > {output_file}.stats"
```

## Key Features for Development

### Pre/Post Processing Scripts
- **Global Level**: Execute before/after entire chain (`preprocessing`/`postprocessing`)
- **Per-Phase Level**: Execute before/after each prompt step (`prescript`/`postscript`)
- **Variable Substitution**: `{input_file}` and `{output_file}` replaced with actual paths
- **Naming Support**: Optional `name01-name99` for human-readable script descriptions

### Multi-Pass Processing
- **passes: N**: Run prompt step N times (1-99)
- **Content Chaining**: Output of pass N becomes input for pass N+1
- **Skip Steps**: `passes: 0` skips the step entirely

### Content Append Mode
- **append: yes**: Append output to input instead of replacing
- **Content Accumulation**: Useful for multi-document summarization
- **Pass Integration**: Works with multi-pass for iterative accumulation

### File Management
- **Intermediate Files**: All step outputs preserved in temp directory
- **Naming Convention**: `{input_name}_step_{step_number}_{prompt_name}.{ext}`
- **Size Validation**: Configurable file size validation to detect processing issues

## Important Development Patterns

### Error Handling
- **Script Failures**: Prescript failure aborts step; postscript failure logged but continues
- **Chain Continuation**: Use `on_error: continue` to skip failed steps
- **File Validation**: Automatic size validation with configurable thresholds

### API Parameter Support
- **Universal**: model, temperature, max_tokens
- **Advanced**: top_p, top_k, frequency_penalty, presence_penalty, seed
- **Model-Specific**: Automatic filtering for model compatibility (e.g., Gemini models)

### Console Output Format
- **Global Scripts**: "Executing script N: Script Name" → "Result: ✅ complete: time X.X seconds"
- **Per-Phase Scripts**: "preprocessing script: ✅ successfully run" / "postprocessing script: ✅ successfully run"
- **Prompt Results**: "Result: ✅ prompt N name output size: X.Xk time: X.X seconds"

## Environment Variables
- **OPENROUTER_API_KEY**: Required for API access
- **OPENROUTER_MODEL**: Override default model
- **OPENROUTER_LOG_LEVEL**: Override logging level

## File Locations
- **Configuration**: config/ directory
- **Prompts**: prompts/ directory (JSON format)
- **Templates**: Web UI templates in templates/
- **Tests**: tests/ directory
- **Documentation**: README.md (primary user docs)

## Code References
When referencing code, use the pattern `file_path:line_number` for easy navigation (e.g., `src/openrouter_interface/prompt_chain_runner.py:1825`).

## Recent Major Features Added
1. **Per-Phase Pre/Post Processing**: Individual prescript/postscript for each step with variable substitution
2. **Global Pre/Post Processing**: Chain-level script execution with numbered ordering
3. **Multi-Pass Execution**: Iterative prompt processing with configurable passes
4. **Content Append Mode**: Content accumulation across steps
5. **Enhanced Console Output**: Minimal, clean status reporting
6. **File Size Validation**: Automatic detection of processing issues
7. **Web Interface YAML Loading**: Upload YAML configs for both single prompts and prompt chains via web UI

## Web Interface Features

### YAML Configuration Loading
The web interface now supports uploading YAML configuration files for:

#### Single Prompt Execution
- Upload YAML files containing API parameters (model, temperature, max_tokens, etc.)
- Real-time preview of configuration settings
- Automatic validation and parameter filtering based on model compatibility
- Support for all OpenRouter API parameters including advanced sampling controls

#### Prompt Chain Execution
- Upload existing chain configuration files from tests/ directory or custom configs
- Visual preview showing raw YAML and parsed configuration summary
- Support for all chain features: global config, preprocessing/postprocessing, multi-pass, append mode
- Configuration validation and error reporting

### Web UI Navigation
- **Main Page**: `/` - "Load Prompt" button for uploading and executing JSON prompt files directly
- **Single Prompts**: `/prompt/<prompt_file>` - Select "Upload YAML Configuration" option
- **Prompt Chains**: `/chains` - "Load Chain" button for uploading and executing YAML chain configurations directly
- **Chain Creation**: `/chains/create` - Choose "Upload Existing YAML Configuration" method
- **Configuration Management**: `/config` - Manage default Flask application settings

### Load Buttons Features
#### Load Prompt Button (Main Page)
- **Direct JSON Upload**: Upload any JSON prompt file without adding to registry
- **Real-time Preview**: Shows prompt details (title, description, persona, instructions, etc.)
- **Configuration Support**: Optional YAML config upload for custom API parameters
- **Input Methods**: Text input or file upload
- **Output Formats**: Markdown, JSON, XML, plain text
- **Immediate Execution**: Execute and view results in modal dialog with copy functionality

#### Load Chain Button (Chain Runner Page)
- **Direct YAML Upload**: Upload chain configuration files for immediate execution
- **Rich Preview**: Shows parsed configuration summary and raw YAML content
- **Configuration Analysis**: Displays global config, file settings, scripts, and prompt steps
- **Input Handling**: Text input or file upload for chain processing
- **Background Execution**: Starts chain execution and displays in active chains list
- **Real-time Monitoring**: Progress tracking and log viewing through existing chain interface