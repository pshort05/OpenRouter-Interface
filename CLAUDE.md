# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenRouter Interface is a Python toolkit for AI language model processing through the OpenRouter API. It provides:

- **CLI Interface**: Single and multi-prompt processing (`openrouter-runner`)
- **Web Interface**: Flask-based dashboard (`openrouter-web`)
- **Chain Processing**: Multi-step workflows (`openrouter-chain`)
- **Script Integration**: Pre/post processing automation
- **File Conversion**: Convert between markdown and various formats (docx, pdf, epub, etc.)
- **Advanced Features**: Multi-pass, content append, combine outputs, variable substitution

## Key Architecture

### Core Components
- **src/openrouter_interface/**: Main Python package
- **prompt_runner.py**: Core processing engine for single prompts
- **prompt_chain_runner.py**: Chain execution with multi-step workflows
  - **chain_console.py**: Console output management for chains
  - **chain_status.py**: Status tracking and restart functionality
  - **file_converter.py**: Document format conversion (docx, pdf, epub, etc.)
- **prompt_runner_flask.py**: Flask web application
  - **flask_helpers.py**: Utility functions (file size formatting, IP detection)
- **config_manager.py**: YAML configuration handling
- **api_client.py**: OpenRouter API communication

### Entry Points (pyproject.toml)
- `openrouter-runner` = CLI interface for single prompts
- `openrouter-web` = Web interface launcher
- `openrouter-chain` = Chain execution engine
- `bookgen` = Specialized book generation workflows
- `split-chapters` = Utility to split markdown documents by chapter headings

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

# Chain restart and recovery
PYTHONPATH=src python3 -m openrouter_interface.chain --status-only -c config.yaml
PYTHONPATH=src python3 -m openrouter_interface.chain --restart -c config.yaml
PYTHONPATH=src python3 -m openrouter_interface.chain --restart-from 4 -c config.yaml
PYTHONPATH=src python3 -m openrouter_interface.chain --clean-status -c config.yaml

# Global commands (after install-global.sh)
openrouter-runner --help
openrouter-web --help
openrouter-chain --help
split-chapters --help

# Chapter splitter - Split documents by chapters
split-chapters book.md
split-chapters book.md -o chapters/
split-chapters book.md --dry-run
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

### Combine Outputs Feature
- **combine: true**: Combine all step output files into a single file after chain completes
- **combined_file_name**: Name of the combined output file (required when combine=true)
- **Differs from append**: Append mode creates one output during processing; combine merges all step outputs afterward
- **Format**: Creates markdown file with headers for each step and separators
- **Example**:
  ```yaml
  combine: true
  combined_file_name: all_steps_combined.md
  ```

### File Conversion Feature
- **Input Conversion**: Convert input files (docx, pdf, epub, etc.) to markdown before chain processing
- **Output Conversion**: Convert final markdown output to multiple formats (docx, pdf, epub, etc.)
- **Per-Step Conversion**: Convert individual step outputs to specific formats
- **Automatic Format Detection**: Auto-detects input format if not specified
- **Dependencies**: Requires pypandoc Python package and pandoc system binary
- **Supported Formats**:
  - **Input**: docx, odt, rtf, html, epub, txt, pdf, latex, rst, org, mediawiki
  - **Output**: docx, odt, rtf, html, epub, pdf, txt, latex, rst, org, mediawiki
- **Configuration**:
  ```yaml
  # Pre-processing: Convert input to markdown
  input_convert:
    enabled: true
    from_format: docx  # Optional: auto-detects if not specified

  # Post-processing: Convert output to multiple formats
  output_convert:
    enabled: true
    formats:
      - docx
      - pdf
      - epub

  # Per-step: Convert specific step output
  prompts:
    prompt 2:
      convert_output:
        format: pdf
        filename: step2_custom.pdf  # Optional custom filename
  ```
- **Installation**:
  ```bash
  pip install pypandoc
  # Install pandoc: https://pandoc.org/installing.html
  # For PDF: Install LaTeX (TeX Live, MiKTeX)
  ```

### Chapter Splitter Utility
- **Standalone Tool**: Split markdown documents into separate files by chapter headings
- **Automatic Detection**: Identifies chapter headings at any level (e.g., `# Chapter 1`, `## Chapter 2`)
- **Smart Naming**: Creates files as `chapter_1.md`, `chapter_2.md`, etc.
- **Title Stripping**: Drops text after chapter number (e.g., "Chapter 1: The Beginning" → `chapter_1.md`)
- **Duplicate Handling**: Adds A, B, C suffixes for duplicate chapter numbers
- **Preamble Support**: Saves content before first chapter to `preamble.md`
- **Case Insensitive**: Detects "chapter", "Chapter", "CHAPTER", etc.
- **Configuration**:
  ```bash
  # Basic usage (output in same directory as input)
  split-chapters book.md

  # Specify output directory
  split-chapters book.md -o chapters/

  # Dry run (preview without creating files)
  split-chapters book.md --dry-run

  # From Python module (development)
  PYTHONPATH=src python3 -m openrouter_interface.split_chapters book.md
  ```
- **Output Format**:
  - Creates individual chapter files with original heading preserved
  - Comprehensive summary showing all chapters found
  - Warnings for duplicate chapter numbers
  - Line counts and file statistics
- **Use Cases**:
  - Prepare book chapters for individual processing in chains
  - Split large documents for parallel processing
  - Organize content by chapter for version control
  - Extract specific chapters from compiled manuscripts

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
1. **Chain Restart & Recovery**: Automatic restart from failed steps with persistent status tracking
2. **Per-Phase Pre/Post Processing**: Individual prescript/postscript for each step with variable substitution
3. **Global Pre/Post Processing**: Chain-level script execution with numbered ordering
4. **Multi-Pass Execution**: Iterative prompt processing with configurable passes
5. **Content Append Mode**: Content accumulation across steps
6. **Combine Outputs**: Merge all step outputs into single file after chain completion
7. **File Conversion**: Convert between markdown and various formats (docx, pdf, epub, etc.) at input, output, and per-step levels
8. **Enhanced Console Output**: Minimal, clean status reporting
9. **File Size Validation**: Automatic detection of processing issues
10. **Web Interface YAML Loading**: Upload YAML configs for both single prompts and prompt chains via web UI

### Chain Restart & Recovery System
The chain runner now includes comprehensive restart functionality to recover from failures and optimize expensive LLM processing:

**Key Benefits:**
- ⏱️ **Time Savings**: Skip completed steps when restarting failed chains
- 💰 **Cost Efficiency**: Avoid re-running expensive LLM calls
- 🔍 **Full Transparency**: `.status` files show exactly what completed/failed
- 🎯 **Flexible Recovery**: Auto-detect restart points or force restart from any step
- 📁 **Multi-file Support**: Independent restart points per input file

**Status Tracking:**
- Real-time status updates in `{config_name}.status` JSON files
- Detailed execution tracking: timing, file sizes, error messages
- Per-file and per-step progress tracking

**CLI Commands:**
```bash
# Check execution status without running
openrouter-chain -c config.yaml --status-only

# Restart from failed steps automatically
openrouter-chain -c config.yaml --restart

# Force restart from specific step for all files
openrouter-chain -c config.yaml --restart-from 4

# Clean status file before starting fresh
openrouter-chain -c config.yaml --clean-status
```

**Example Restart Scenario:**
```
Working on file chapter_21.md size: 21.6k

Executing Prompt 1: grammar_foundation
Result: ✅ prompt 1 grammar_foundation output size: 21.6k time: 136.3 seconds

Executing Prompt 2: ai_word_cleaning
Result: ✅ prompt 2 ai_word_cleaning output size: 21.3k time: 135.7 seconds

Executing Prompt 3: overwritten_language_reduction
Result: ✅ prompt 3 overwritten_language_reduction output size: 21.1k time: 139.2 seconds

Executing Prompt 4: sensory_enhancement
Result: ❌ prompt 4 sensory_enhancement FAILED time: 300.1 seconds
        Error: openrouter-runner timed out after 5 minutes
```

When restarted with `--restart`, the system will:
1. Detect previous failure at step 4
2. Skip steps 1-3 (already completed successfully)
3. Resume execution from step 4 and continue through remaining steps
4. Track all new progress in the status file

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
- **Prompt Chains**: `/chains` - "Load Chain" button navigates to dedicated load page
- **Chain Load Page**: `/chains/load` - Full-featured YAML configuration upload and execution page
- **YAML Editor**: `/chains/yaml-editor` - Advanced YAML editor with syntax highlighting and templates
- **Chain Creation**: `/chains/create` - Visual chain builder with upload configuration option
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
- **Dedicated Load Page**: Full-featured page similar to "Create New Prompt Chain" at `/chains/load`
- **YAML Editor Integration**: Built-in YAML editor at `/chains/yaml-editor` with syntax highlighting and validation
- **Rich Configuration Analysis**: Detailed breakdown of global config, scripts, prompts, and validation settings
- **Advanced Input Options**: Text, file upload, or use configuration file input
- **Validation & Preview**: Client-side YAML validation with comprehensive error reporting
- **Template Support**: Quick access to configuration templates (basic, advanced, scripts, multi-pass, append)
- **Execution Control**: Debug mode, output filename override, and validation checks
- **Editor Features**: Auto-save, keyboard shortcuts, theme selection, format validation