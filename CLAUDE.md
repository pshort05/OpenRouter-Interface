# OpenRouter Interface Documentation

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Table of Contents

- [Overview](#overview) ([Quickstart Guide](#quickstart-guide))
- [1. Installation](#1-installation)
  - [1.1 API Key Setup](#11-api-key-setup)
  - [1.2 Linux Installation](#12-linux-installation)
  - [1.3 Windows Installation](#13-windows-installation)
  - [1.4 Mac Installation](#14-mac-installation)
- [2. Running Single Prompts](#2-running-single-prompts)
- [3. Web Interface](#3-web-interface)
- [4. Chaining Prompts](#4-chaining-prompts)
  - [4.1 Chaining Prompts via CLI](#41-chaining-prompts-via-cli)
  - [4.2 Chaining Prompts via Web Interface](#42-chaining-prompts-via-web-interface)
  - [4.3 Common Configurations](#43-common-configurations)
  - [4.4 Pre and Post Processing](#44-pre-and-post-processing)
  - [4.5 File Management](#45-file-management)
  - [4.6 Full Configuration Documentation](#46-full-configuration-documentation)
- [5. Templates](#5-templates)
- [6. Examples](#6-examples)
- [7. Model Reference](#7-model-reference)
- [8. Troubleshooting](#8-troubleshooting)
  - [8.1 Getting Help](#81-getting-help)
- [9. Developer Documentation](#9-developer-documentation)
  - [9.1 Project Structure](#91-project-structure)
  - [9.2 Tests](#92-tests)
- [10. Project Information](#10-project-information)
  - [10.1 License](#101-license)
  - [10.2 Support](#102-support)
  - [10.3 Contributing](#103-contributing)

---

## Overview

OpenRouter Interface is a comprehensive toolkit for working with AI language models through the OpenRouter API. It provides:

- **Single Prompt Processing**: Run individual prompts against AI models
- **Multi-Prompt Chaining**: Chain multiple prompts together for complex workflows
- **Web Interface**: User-friendly web dashboard for managing prompts and chains
- **Advanced Features**: Pre/post processing scripts, file management, and extensive configuration options

### Key Features

- ✅ **Multiple Interface Options**: CLI, Web UI, and programmatic access
- ✅ **Model Flexibility**: Support for 100+ AI models via OpenRouter
- ✅ **Chain Processing**: Sequential prompt execution with intermediate file management
- ✅ **Script Integration**: Pre/post processing scripts at global and per-step levels
- ✅ **Configuration Management**: YAML-based configuration with parameter overrides
- ✅ **File Processing**: Automatic chunking, validation, and format handling

### Quickstart Guide

1. **Install the package**:
   ```bash
   ./install-global.sh
   ```

2. **Set up your API key**:
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   ```

3. **Run a single prompt**:
   ```bash
   openrouter-runner -p prompts/example.json -i input.md -o output.md
   ```

4. **Create and run a prompt chain**:
   ```bash
   openrouter-chain --create-sample
   openrouter-chain -c sample_chain.yaml
   ```

5. **Start the web interface**:
   ```bash
   openrouter-web
   ```

---

## 1. Installation

### 1.1 API Key Setup

First, obtain an API key from [OpenRouter](https://openrouter.ai/) and set it up:

```bash
# Method 1: Environment variable
export OPENROUTER_API_KEY="your-api-key-here"

# Method 2: Using setup script
./setup-api-key.sh

# Method 3: Add to your shell profile
echo 'export OPENROUTER_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 1.2 Linux Installation

#### Global Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface

# Install globally
./install-global.sh

# Verify installation
openrouter-runner --help
openrouter-web --help
openrouter-chain --help
```

#### Local Development Installation
```bash
# Install for development
./install.sh web

# Activate virtual environment
source openrouter-venv/bin/activate

# Run from source
PYTHONPATH=src python3 -m openrouter_interface.cli --help
```

### 1.3 Windows Installation

#### Prerequisites
- Python 3.8 or higher
- Git for Windows

#### Installation Steps
```cmd
# Clone the repository
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface

# Install using PowerShell (run as administrator)
powershell -ExecutionPolicy Bypass -File install-windows.ps1

# Set API key in Windows
setx OPENROUTER_API_KEY "your-api-key-here"
```

### 1.4 Mac Installation

#### Using Homebrew (Recommended)
```bash
# Install Python if not available
brew install python

# Clone and install
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface
./install-global.sh

# Set API key
echo 'export OPENROUTER_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Manual Installation
```bash
# Ensure Python 3.8+
python3 --version

# Install
./install.sh web
```

---

## 2. Running Single Prompts

### Basic Usage

```bash
# Simple prompt execution
openrouter-runner -p prompts/analysis.json -i input.md -o output.md

# With model override
openrouter-runner -p prompts/creative.json -i input.md -o output.md --model "openai/gpt-4-turbo"

# With parameter overrides
openrouter-runner -p prompts/technical.json -i input.md -o output.md \
  --temperature 0.2 \
  --max-tokens 30000 \
  --top-p 0.95
```

### Multi-Prompt Execution

Execute multiple prompts sequentially on the same input:

```bash
# Multiple prompts (comma-separated)
openrouter-runner -p "prompts/quality.json,prompts/grammar.json,prompts/style.json" \
  -i document.md -o processed_document.md

# Each prompt processes the output of the previous one
```

### Command Line Options

```bash
# Get help
openrouter-runner --help

# Common options
-p, --prompt          Prompt file(s) - comma-separated for multiple
-i, --input           Input file path
-o, --output          Output file path
-c, --config          Configuration file override
-l, --log             Log file path
--model              Model override
--temperature        Temperature override (0.0-2.0)
--max-tokens         Maximum tokens override
--debug              Enable debug logging
--temp-dir           Custom temporary directory
```

### Configuration Files

Create custom configuration files for different use cases:

```yaml
# config/creative_config.yaml
model: "openai/gpt-4-turbo"
temperature: 0.9
max_tokens: 25000
top_p: 0.95
presence_penalty: 0.3

# config/analytical_config.yaml
model: "anthropic/claude-4-sonnet-20250522"
temperature: 0.2
max_tokens: 30000
top_k: 20
frequency_penalty: 0.3
```

---

## 3. Web Interface

### Starting the Web Interface

```bash
# Start with default configuration
openrouter-web

# Start with custom configuration
openrouter-web --config config/web_config.yaml

# Start on specific port
openrouter-web --port 8080

# Start with debug mode
openrouter-web --debug
```

### Web Interface Features

#### Single Prompt Processing
- **Upload Files**: Drag and drop or browse to upload input files
- **Select Prompts**: Choose from available prompt templates
- **Model Selection**: Pick from 100+ available models
- **Parameter Control**: Adjust temperature, max tokens, and other parameters
- **Real-time Processing**: Watch progress and download results

#### Chain Management
- **Create Chains**: Visual chain builder with drag-and-drop interface
- **Monitor Progress**: Real-time execution status with step-by-step progress
- **File Management**: View intermediate files and download results
- **Configuration Templates**: Save and reuse common chain configurations

#### Dashboard Features
- **Execution History**: View past runs with detailed logs
- **Model Statistics**: Usage statistics and performance metrics
- **File Browser**: Browse and manage input/output files
- **Configuration Manager**: Edit and save configuration templates

### Web Interface Configuration

```yaml
# config/web_config.yaml
server:
  host: "0.0.0.0"
  port: 8080
  debug: false

upload:
  max_file_size: 50MB
  allowed_extensions: [".md", ".txt", ".json", ".yaml"]
  temp_directory: "temp/uploads"

security:
  enable_auth: false
  session_timeout: 3600

features:
  enable_file_browser: true
  enable_model_selection: true
  max_concurrent_chains: 5
```

---

## 4. Chaining Prompts

### 4.1 Chaining Prompts via CLI

#### Basic Chain Execution

```bash
# Create a sample chain configuration
openrouter-chain --create-sample

# Run a chain
openrouter-chain -c chain_config.yaml

# Run with debug output
openrouter-chain -c chain_config.yaml --debug

# Override input/output files
openrouter-chain -c chain_config.yaml -i custom_input.md -o custom_output.md
```

#### Chain Configuration Format

```yaml
# Basic chain configuration
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7
  max_tokens: 20000

input_file: input.md
output_file: processed_output.md

prompts:
  prompt 1:
    name: "grammar_foundation"
    prompt_file: "prompts/1_grammar.json"
    temperature: 0.2

  prompt 2:
    name: "style_enhancement"
    prompt_file: "prompts/2_style.json"
    temperature: 0.8
    model: "openai/gpt-4-turbo"

  prompt 3:
    name: "final_review"
    prompt_file: "prompts/3_review.json"
```

### 4.2 Chaining Prompts via Web Interface

#### Creating Chains in Web UI

1. **Navigate to Chain Builder**
   - Click "Create New Chain" in the web dashboard
   - Use the visual chain builder interface

2. **Add Chain Steps**
   - Drag prompt templates to create steps
   - Configure each step's parameters
   - Set model overrides per step

3. **Configure Global Settings**
   - Set default model and parameters
   - Configure file management options
   - Set up pre/post processing scripts

4. **Execute and Monitor**
   - Start chain execution
   - Monitor real-time progress
   - View intermediate results

#### Web Interface Chain Features

- **Visual Chain Builder**: Drag-and-drop interface for creating chains
- **Real-time Monitoring**: Live progress updates with step status
- **Intermediate File Viewing**: Inspect outputs at each chain step
- **Error Handling**: Visual error reporting with detailed logs
- **Chain Templates**: Save and reuse common chain configurations

### 4.3 Common Configurations

#### Content Processing Pipeline

```yaml
# Content enhancement chain
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

prompts:
  prompt 1:
    name: "grammar_check"
    prompt_file: "prompts/grammar.json"
    temperature: 0.2

  prompt 2:
    name: "style_improvement"
    prompt_file: "prompts/style.json"
    temperature: 0.8

  prompt 3:
    name: "readability_enhancement"
    prompt_file: "prompts/readability.json"
    temperature: 0.6

  prompt 4:
    name: "final_polish"
    prompt_file: "prompts/polish.json"
    temperature: 0.4
```

#### Multi-Pass Processing

```yaml
# Iterative refinement with multiple passes
prompts:
  prompt 1:
    name: "iterative_improvement"
    prompt_file: "prompts/improve.json"
    passes: 3  # Run this step 3 times
    temperature: 0.6

  prompt 2:
    name: "content_expansion"
    prompt_file: "prompts/expand.json"
    passes: 2
    append: yes  # Append output to input
```

#### Model-Specific Configurations

```yaml
# Using different models for different tasks
prompts:
  prompt 1:
    name: "technical_analysis"
    prompt_file: "prompts/analyze.json"
    model: "deepseek/deepseek-coder"
    temperature: 0.3

  prompt 2:
    name: "creative_enhancement"
    prompt_file: "prompts/creative.json"
    model: "openai/gpt-4-turbo"
    temperature: 0.9

  prompt 3:
    name: "final_review"
    prompt_file: "prompts/review.json"
    model: "anthropic/claude-4-sonnet-20250522"
    temperature: 0.4
```

### 4.4 Pre and Post Processing

#### Global Pre/Post Processing Scripts

Execute scripts before and after the entire chain:

```yaml
# Global script execution
preprocessing:
  script01: echo "Starting processing pipeline"
  name01: "Initialize Pipeline"
  script02: python3 scripts/validate_input.py
  name02: "Validate Input"
  script03: mkdir -p output/logs
  name03: "Create Directories"

postprocessing:
  script01: python3 scripts/generate_report.py
  name01: "Generate Report"
  script02: ./scripts/cleanup.sh
  name02: "Cleanup Temporary Files"

prompts:
  prompt 1:
    name: "content_processing"
    prompt_file: "prompts/process.json"
```

#### Per-Phase Pre/Post Processing Scripts

Execute scripts before and after individual prompt steps:

```yaml
prompts:
  prompt 1:
    prescript: "touch {input_file}.backup"
    name: "grammar_foundation"
    prompt_file: "prompts/grammar.json"
    postscript: "wc -l {output_file} > {output_file}.stats"

  prompt 2:
    prescript: "echo 'Processing: {input_file}' >> progress.log"
    name: "style_enhancement"
    prompt_file: "prompts/style.json"
    postscript: "cp {output_file} backup/step2_output.md"
```

#### Variable Substitution

Scripts support dynamic variable replacement:

- **{input_file}**: Actual input file path for the step
- **{output_file}**: Actual output file path for the step

```yaml
prompt 1:
  prescript: "python3 validate.py {input_file}"
  postscript: "diff {input_file} {output_file} > changes.log"
```

#### Real-World Script Examples

**File Validation and Backup:**
```yaml
prompt 1:
  prescript: "cp {input_file} {input_file}.backup && chmod 644 {input_file}"
  postscript: "python3 validate_output.py {output_file} || exit 1"
```

**Progress Tracking:**
```yaml
prompt 1:
  prescript: "echo 'Starting step 1 at $(date)' >> progress.log"
  postscript: "echo 'Step 1 completed: $(wc -w {output_file})' >> progress.log"
```

### 4.5 File Management

#### Input/Output Configuration

```yaml
# Single file processing
input_file: document.md
output_file: processed_document.md

# Multiple file processing
input_files:
  - chapter1.md
  - chapter2.md
  - chapter3.md
output_pattern: "processed_{input_name}.md"
```

#### File Size Validation

```yaml
# Configure file size validation
global_config:
  file_size_validation:
    enabled: true
    max_size_difference_percent: 50
    min_file_size_bytes: 100
```

#### Temporary File Management

- **Intermediate Files**: All step outputs preserved in temp directory
- **Naming Convention**: `{input_name}_step_{step_number}_{prompt_name}.{ext}`
- **Preservation**: Files kept for debugging and analysis
- **Cleanup**: Optional cleanup after chain completion

#### Content Append Mode

```yaml
# Accumulate content across steps
prompts:
  prompt 1:
    name: "summary_1"
    prompt_file: "prompts/summarize.json"
    append: yes  # Append output to input

  prompt 2:
    name: "summary_2"
    prompt_file: "prompts/summarize.json"
    append: yes  # Continue accumulating
```

### 4.6 Full Configuration Documentation

#### Complete Configuration Example

```yaml
# Complete chain configuration with all features
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7
  max_tokens: 25000

  # Advanced API parameters
  top_p: 0.9
  top_k: 50
  frequency_penalty: 0.1
  presence_penalty: 0.1

  # File validation
  file_size_validation:
    enabled: true
    max_size_difference_percent: 50
    min_file_size_bytes: 100

# Input/Output configuration
input_file: document.md
output_file: processed_document.md

# Global preprocessing scripts
preprocessing:
  script01: echo "Starting processing"
  name01: "Initialize"
  script02: python3 scripts/validate.py
  name02: "Validate Input"

# Global postprocessing scripts
postprocessing:
  script01: python3 scripts/report.py
  name01: "Generate Report"

# Prompt chain configuration
prompts:
  prompt 1:
    prescript: "touch {input_file}.marker"
    name: "grammar_foundation"
    prompt_file: "prompts/grammar.json"
    model: "deepseek/deepseek-coder"
    temperature: 0.2
    passes: 2
    on_error: continue
    postscript: "ls -la {output_file}"

  prompt 2:
    name: "style_enhancement"
    prompt_file: "prompts/style.json"
    temperature: 0.8
    append: yes
    top_p: 0.95

  prompt 3:
    name: "final_review"
    prompt_file: "prompts/review.json"
    passes: 0  # Skip this step
```

#### Configuration Parameters Reference

**Global Parameters:**
- `model`: Default model for all steps
- `temperature`: Randomness control (0.0-2.0)
- `max_tokens`: Maximum response length
- `top_p`: Top-p nucleus sampling
- `top_k`: Top-k sampling
- `frequency_penalty`: Reduce repetition by frequency
- `presence_penalty`: Reduce repetition by presence

**Step-Specific Parameters:**
- `name`: Human-readable step name
- `prompt_file`: Path to prompt JSON file
- `prescript`: Script to run before step
- `postscript`: Script to run after step
- `passes`: Number of times to run the step (1-99)
- `append`: Append output to input (yes/no)
- `on_error`: Behavior on error (stop/continue)

**File Management:**
- `input_file`: Single input file
- `input_files`: Multiple input files
- `output_file`: Single output file
- `output_pattern`: Output naming pattern for multiple files

---

## 5. Templates

### Prompt Templates

Create reusable prompt templates in JSON format:

```json
{
  "instruction": "You are a content quality evaluator.",
  "persona": "Professional Content Quality Analyst",
  "evaluation_directives": {
    "clarity": "Assess how clearly ideas are expressed",
    "coherence": "Evaluate how well ideas flow together",
    "structure": "Analyze organizational structure"
  },
  "output_format": "Provide structured analysis with recommendations."
}
```

### Chain Templates

Common chain templates for different use cases:

#### Content Enhancement Template
```yaml
# templates/content_enhancement.yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

prompts:
  prompt 1:
    name: "grammar_check"
    prompt_file: "prompts/grammar.json"
    temperature: 0.2

  prompt 2:
    name: "style_improvement"
    prompt_file: "prompts/style.json"
    temperature: 0.8

  prompt 3:
    name: "readability_check"
    prompt_file: "prompts/readability.json"
```

#### Technical Documentation Template
```yaml
# templates/technical_docs.yaml
global_config:
  model: "deepseek/deepseek-coder"
  temperature: 0.3

prompts:
  prompt 1:
    name: "code_analysis"
    prompt_file: "prompts/analyze_code.json"

  prompt 2:
    name: "documentation_generation"
    prompt_file: "prompts/generate_docs.json"

  prompt 3:
    name: "example_creation"
    prompt_file: "prompts/create_examples.json"
```

---

## 6. Examples

### Basic Examples

#### Example 1: Single Prompt Processing
```bash
# Process a document for grammar issues
openrouter-runner \
  -p prompts/grammar_check.json \
  -i my_document.md \
  -o corrected_document.md \
  --temperature 0.2
```

#### Example 2: Multi-Prompt Processing
```bash
# Process document through multiple improvement steps
openrouter-runner \
  -p "prompts/grammar.json,prompts/style.json,prompts/clarity.json" \
  -i draft.md \
  -o final_draft.md
```

### Chain Examples

#### Example 3: Content Enhancement Chain
```yaml
# content_enhancement_example.yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

input_file: blog_post_draft.md
output_file: enhanced_blog_post.md

prompts:
  prompt 1:
    name: "grammar_foundation"
    prompt_file: "prompts/grammar.json"
    temperature: 0.2

  prompt 2:
    name: "engagement_improvement"
    prompt_file: "prompts/engagement.json"
    temperature: 0.8

  prompt 3:
    name: "seo_optimization"
    prompt_file: "prompts/seo.json"
    temperature: 0.6
```

#### Example 4: Technical Document Processing
```yaml
# technical_processing_example.yaml
global_config:
  model: "deepseek/deepseek-coder"
  temperature: 0.3

preprocessing:
  script01: python3 scripts/extract_code_blocks.py
  name01: "Extract Code Blocks"

prompts:
  prompt 1:
    name: "code_documentation"
    prompt_file: "prompts/document_code.json"
    prescript: "python3 scripts/validate_syntax.py {input_file}"
    postscript: "python3 scripts/test_examples.py {output_file}"

  prompt 2:
    name: "api_reference_generation"
    prompt_file: "prompts/api_reference.json"

postprocessing:
  script01: python3 scripts/generate_toc.py
  name01: "Generate Table of Contents"
```

### Advanced Examples

#### Example 5: Multi-File Processing with Scripts
```yaml
# multi_file_processing_example.yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.6

input_files:
  - chapter1.md
  - chapter2.md
  - chapter3.md
output_pattern: "processed_{input_name}.md"

preprocessing:
  script01: mkdir -p output/chapters
  name01: "Create Output Directory"
  script02: python3 scripts/validate_chapters.py
  name02: "Validate Chapter Structure"

prompts:
  prompt 1:
    prescript: "echo 'Processing {input_file}' >> processing.log"
    name: "content_enhancement"
    prompt_file: "prompts/enhance.json"
    postscript: "wc -w {output_file} >> word_counts.log"

postprocessing:
  script01: python3 scripts/combine_chapters.py
  name01: "Combine Processed Chapters"
  script02: python3 scripts/generate_index.py
  name02: "Generate Chapter Index"
```

---

## 7. Model Reference

### Supported Models

OpenRouter Interface supports 100+ models through the OpenRouter API:

#### Popular Models

**Anthropic Claude Models:**
- `anthropic/claude-4-sonnet-20250522` - High-quality reasoning and writing
- `anthropic/claude-3-5-sonnet` - Fast and capable
- `anthropic/claude-3-haiku` - Quick responses

**OpenAI Models:**
- `openai/gpt-4-turbo` - Advanced reasoning and creativity
- `openai/gpt-4o` - Optimized for speed and efficiency
- `openai/gpt-3.5-turbo` - Cost-effective option

**Google Models:**
- `google/gemini-2.0-flash-001` - Fast multimodal processing
- `google/gemini-1.5-pro` - Advanced reasoning

**Specialized Models:**
- `deepseek/deepseek-coder` - Code generation and analysis
- `meta/llama-3.1-405b` - Open-source large language model

### Model Configuration

```yaml
# Model-specific configurations
configs:
  creative_config:
    model: "openai/gpt-4-turbo"
    temperature: 0.9
    top_p: 0.95
    presence_penalty: 0.3

  analytical_config:
    model: "anthropic/claude-4-sonnet-20250522"
    temperature: 0.2
    top_k: 20
    frequency_penalty: 0.3

  coding_config:
    model: "deepseek/deepseek-coder"
    temperature: 0.3
    response_format:
      type: "json_object"
```

### Model Parameter Compatibility

Different models support different parameters:

**Universal Parameters:**
- `model`, `temperature`, `max_tokens`

**OpenAI/Anthropic Compatible:**
- `top_p`, `frequency_penalty`, `presence_penalty`, `seed`

**Google Gemini Specific:**
- `max_output_tokens` (converted from `max_tokens`)
- Limited parameter support (auto-filtered)

---

## 8. Troubleshooting

### Common Issues

#### API Key Issues
```bash
# Check if API key is set
echo $OPENROUTER_API_KEY

# Test API connectivity
openrouter-runner --help
```

#### File Permission Issues
```bash
# Fix file permissions
chmod +x install-global.sh
chmod +x start-web.sh

# Check file accessibility
ls -la input_file.md
```

#### Memory Issues
```bash
# Reduce max_tokens for large files
openrouter-runner -p prompt.json -i large_file.md -o output.md --max-tokens 10000

# Process in smaller chunks
split -l 100 large_file.md chunk_
```

#### Chain Execution Issues
```bash
# Enable debug mode for detailed logs
openrouter-chain -c config.yaml --debug

# Check intermediate files
ls -la temp/chain_execution_*/

# Validate configuration
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

### Error Messages

**"Configuration file not found"**
- Check file path is correct
- Ensure file exists and is readable

**"Prompt file not found"**
- Verify prompt files exist in prompts/ directory
- Check prompt_file paths in configuration

**"API request failed"**
- Verify OPENROUTER_API_KEY is set
- Check internet connectivity
- Verify model name is correct

### Performance Optimization

```yaml
# Optimize for speed
global_config:
  model: "openai/gpt-3.5-turbo"  # Faster model
  max_tokens: 10000              # Reduce token limit
  temperature: 0.5               # Lower temperature

# Optimize for quality
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  max_tokens: 30000
  temperature: 0.7
  top_p: 0.9
```

### 8.1 Getting Help

#### Documentation and Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Complete guides and API reference
- **Community**: Discord/Slack for community support
- **Examples**: Sample configurations and use cases

#### Debug Information

```bash
# Generate debug information
openrouter-runner --version
python3 --version
echo $OPENROUTER_API_KEY | cut -c1-8  # Show first 8 chars

# Enable verbose logging
openrouter-chain -c config.yaml --debug 2>&1 | tee debug.log
```

#### Common Commands for Debugging

```bash
# Test basic functionality
openrouter-runner -p prompts/test.json -i test_input.md -o test_output.md

# Validate configuration
python3 -m openrouter_interface.chain --validate-config config.yaml

# Check model availability
python3 -m openrouter_interface.cli --list-models

# Test web interface
openrouter-web --debug --port 8080
```

---

## 9. Developer Documentation

### 9.1 Project Structure

```
openrouter-interface/
├── src/openrouter_interface/     # Main Python package
│   ├── cli.py                    # CLI interface
│   ├── web.py                    # Web interface
│   ├── chain.py                  # Chain runner
│   ├── prompt_runner.py          # Core processing engine
│   ├── prompt_chain_runner.py    # Chain execution logic
│   ├── config_manager.py         # Configuration handling
│   └── api_client.py             # OpenRouter API client
├── config/                       # Configuration files
├── prompts/                      # Prompt templates
├── templates/                    # Web UI templates
├── scripts/                      # Utility scripts
├── tests/                        # Test suite
└── docs/                         # Documentation
```

#### Core Components

**PromptRunner (prompt_runner.py):**
- Central orchestrator for prompt processing
- Handles text chunking, API communication
- Manages batch and interactive modes

**ChainRunner (prompt_chain_runner.py):**
- Multi-step workflow execution
- Progress tracking and file management
- Error handling and recovery

**ConfigManager (config_manager.py):**
- YAML configuration loading and validation
- Parameter merging and override handling
- Environment variable integration

### 9.2 Tests

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=openrouter_interface

# Run specific test categories
pytest tests/test_cli.py
pytest tests/test_chain.py
pytest tests/test_config.py

# Run integration tests
pytest tests/integration/
```

#### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Configuration Tests**: YAML validation and parameter handling
- **API Tests**: OpenRouter API interaction testing

#### Writing Tests

```python
# Example test structure
import pytest
from openrouter_interface.config_manager import ConfigManager

def test_config_loading():
    config = ConfigManager("test_config.yaml")
    assert config.get_model() == "expected_model"
    assert config.get_temperature() == 0.7

def test_chain_execution():
    runner = ChainRunner("test_chain.yaml")
    result = runner.run_chain()
    assert result == True
```

---

## 10. Project Information

### 10.1 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### 10.2 Support

#### Getting Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/your-org/openrouter-interface/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/your-org/openrouter-interface/discussions)
- **Documentation**: [Complete documentation and guides](https://docs.your-org.com/openrouter-interface)

#### Community

- **Discord**: Join our community chat
- **Twitter**: Follow for updates and tips
- **Blog**: Technical articles and tutorials

### 10.3 Contributing

#### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-org/openrouter-interface.git
   cd openrouter-interface
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Run Tests**
   ```bash
   pytest
   black src tests
   flake8 src
   mypy src
   ```

5. **Submit Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all checks pass

#### Development Setup

```bash
# Install development dependencies
./install.sh dev

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run development server
PYTHONPATH=src python3 -m openrouter_interface.web --debug
```

#### Coding Standards

- **Python Style**: Follow PEP 8, use Black for formatting
- **Type Hints**: Use type annotations for all functions
- **Documentation**: Docstrings for all public functions
- **Testing**: Minimum 80% test coverage for new code

#### Areas for Contribution

- **New Features**: Prompt templates, chain configurations
- **Model Support**: Additional model integrations
- **Documentation**: Tutorials, examples, guides
- **Testing**: Test coverage improvements
- **Performance**: Optimization and profiling
- **UI/UX**: Web interface improvements

---

## Environment Variables

### Required Variables
- **OPENROUTER_API_KEY**: Your OpenRouter API key (required)

### Optional Variables
- **OPENROUTER_MODEL**: Override default model
- **OPENROUTER_LOG_LEVEL**: Override logging level
- **OPENROUTER_CONFIG_DIR**: Custom configuration directory

### Example Environment Setup

```bash
# Required
export OPENROUTER_API_KEY="your-api-key-here"

# Optional customizations
export OPENROUTER_MODEL="anthropic/claude-4-sonnet-20250522"
export OPENROUTER_LOG_LEVEL="DEBUG"
export OPENROUTER_CONFIG_DIR="/custom/config/path"
```

---

## Package Entry Points

Defined in pyproject.toml:
- `openrouter-runner` = CLI interface for single prompts
- `openrouter-web` = Web interface launcher
- `openrouter-chain` = Chain execution engine
- `bookgen` = Specialized book generation workflows