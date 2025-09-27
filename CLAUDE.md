# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running and Testing
```bash
# CLI usage - Single and multi-prompt support with parameter overrides
PYTHONPATH=src python3 -m openrouter_interface.cli --help
PYTHONPATH=src python3 -m openrouter_interface.cli -p prompts/content_quality.json -i test_input.md
PYTHONPATH=src python3 -m openrouter_interface.cli -p "prompts/quality.json,prompts/grammar.json" -i test_input.md

# CLI with API parameter overrides
PYTHONPATH=src python3 -m openrouter_interface.cli -p prompts/analysis.json -i input.md --temperature 0.2 --max-tokens 30000
PYTHONPATH=src python3 -m openrouter_interface.cli -p prompts/creative.json -i input.md --model "openai/gpt-4-turbo" --top-p 0.95

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

### API Parameter Support

The system now supports the complete OpenRouter API parameter set with intelligent handling:

**Core Parameters** (always included):
- `model`: Model identifier
- `temperature`: Randomness control (0.0-2.0)
- `max_tokens`: Maximum response length

**Advanced Sampling Controls** (optional):
- `top_p`: Top-p nucleus sampling (0, 1]
- `top_k`: Top-k sampling [1, ∞)
- `min_p`: Minimum probability threshold [0, 1]
- `seed`: Deterministic output control

**Penalty Parameters** (optional):
- `frequency_penalty`: Reduce repetition by frequency [-2, 2]
- `presence_penalty`: Reduce repetition by presence [-2, 2]
- `repetition_penalty`: Alternative repetition control (0, 2]

**Response Control** (optional):
- `stream`: Enable streaming responses
- `response_format`: Force structured JSON output
- `top_logprobs`: Return token probabilities

**OpenRouter-Specific Features** (optional):
- `models`: Fallback model list for automatic failover
- `provider`: Provider routing preferences with order and fallback control
- `transforms`: OpenRouter prompt transformations
- `usage`: Detailed usage statistics in response

**Utility Parameters** (optional):
- `user`: User identifier for tracking and abuse prevention

### Parameter Override Hierarchy

1. **Chain step overrides** (highest priority)
2. **Global chain config**
3. **Base config file**
4. **System defaults** (lowest priority)

### Main Config (config/config.yaml)
```yaml
# Core API parameters (always included)
model: anthropic/claude-4-sonnet-20250522
temperature: 0.8
max_tokens: 25000

# Application settings
logging_level: INFO
api_base_url: https://openrouter.ai/api/v1

# Advanced sampling controls (optional - only sent if specified)
top_p: 0.9              # Top-p nucleus sampling (0, 1]
top_k: 50               # Top-k sampling [1, ∞)
min_p: 0.02             # Minimum probability threshold [0, 1]
seed: 12345             # Deterministic output control

# Penalty parameters (optional)
frequency_penalty: 0.1   # Reduce repetition by frequency [-2, 2]
presence_penalty: 0.1    # Reduce repetition by presence [-2, 2]
repetition_penalty: 1.1  # Alternative repetition control (0, 2]

# Response control (optional)
stream: false           # Enable streaming responses
response_format:        # Force structured JSON output
  type: "json_object"
top_logprobs: 5         # Return token probabilities

# OpenRouter-specific features (optional)
models:                 # Fallback model list
  - "anthropic/claude-4-sonnet-20250522"
  - "openai/gpt-4-turbo"
provider:               # Provider routing preferences
  order: ["Anthropic", "OpenAI"]
transforms:             # OpenRouter prompt transformations
  - "middle-out"
usage:                  # Get detailed usage statistics
  include: true

# Utility parameters (optional)
user: "user123"         # User identifier for tracking
```

### Model-Specific Configs
- config/claude_config.yaml
- config/gpt4_config.yaml
- config/deepseek_config.yaml
- config/advanced_api_config.yaml - Comprehensive example with all API parameters
- config/creative_config.yaml - Optimized for creative tasks
- config/precision_config.yaml - Optimized for analytical tasks

### Example Configurations
- examples/comprehensive_chain_with_all_params.yaml - Complete chain with all API parameters
- examples/enhanced_setting_overrides.yaml - Per-phase parameter override examples

### Chain Configs
- Multi-step workflow definitions
- Input/output file specifications
- Model selection per step
- **Per-phase setting overrides**: Each step can override any API parameter including model, temperature, max_tokens, sampling controls, penalties, response format, and OpenRouter-specific features
- **Multi-prompt support**: Each chain step can use comma-separated prompt files
- Progress tracking configuration

### Per-Phase Setting Override Configuration
```yaml
global_config:                    # Default settings for all steps
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7
  max_tokens: 20000
  top_p: 0.9
  frequency_penalty: 0.1
  user: "chain_processor"

prompts:
  # Phase 1: Analytical phase with precision settings
  prompt 1:
    name: "analysis"
    prompt_file: "analysis.json"
    model: "openai/gpt-4-turbo"     # Override model for this step
    temperature: 0.2                # Override temperature for precision
    max_tokens: 30000              # Override max tokens for detailed output
    seed: 42                       # Deterministic results for analysis
    top_k: 20                      # More focused vocabulary
    frequency_penalty: 0.3          # Strong repetition control
    presence_penalty: 0.2          # Diverse analytical points
    top_logprobs: 5                # Token analysis for debugging

  # Phase 2: Creative enhancement with diversity settings
  prompt 2:
    name: "enhancement"
    prompt_file: "enhance.json"
    temperature: 0.9               # Override just temperature for creativity
    max_tokens: 30000              # Longer creative output
    top_p: 0.95                    # Broad sampling
    min_p: 0.01                    # Allow creative tokens
    presence_penalty: 0.4          # Encourage novelty
    stream: true                   # Enable streaming for this step
    # Uses global model, frequency_penalty

  # Phase 3: Technical review with structured output
  prompt 3:
    name: "final_review"
    prompt_file: "review.json"
    model: "deepseek/deepseek-coder" # Specialized technical model
    temperature: 0.4               # Balanced for technical accuracy
    response_format:               # Structured JSON output
      type: "json_object"
    repetition_penalty: 1.2        # Alternative repetition control
    models:                        # Fallback models for reliability
      - "deepseek/deepseek-coder"
      - "anthropic/claude-4-sonnet-20250522"
      - "openai/gpt-4-turbo"
    provider:                      # Provider preferences
      order: ["DeepSeek", "Anthropic", "OpenAI"]
      allow_fallbacks: true
    transforms:                    # OpenRouter transformations
      - "middle-out"
    usage:                         # Track usage for this step
      include: true
```

### Multi-Prompt Chain Configuration
```yaml
prompts:
  prompt 1:
    name: "comprehensive_analysis"
    prompt_file: "quality_check.json,grammar_fix.json"  # Combines two prompts
    temperature: 0.3               # Override temperature for analytical work
  prompt 2:
    name: "style_enhancement"
    prompt_file: "style_guide.json,tone_adjust.json,readability.json"  # Combines three prompts
    model: "anthropic/claude-4-sonnet-20250522"  # Override model for creative work
  prompt 3:
    prompt_file: "final_polish.json"  # Single prompt
```

## Environment Variables
- **OPENROUTER_API_KEY**: Required for API access
- **OPENROUTER_MODEL**: Override default model
- **OPENROUTER_LOG_LEVEL**: Override logging level

## API Parameter Usage Patterns

### Analytical Tasks
```yaml
temperature: 0.1-0.3          # Low randomness for consistency
top_k: 10-30                  # Focused vocabulary
seed: 42                      # Reproducible results
frequency_penalty: 0.2-0.5    # Reduce repetition
top_logprobs: 5               # Debug token selection
```

### Creative Tasks
```yaml
temperature: 0.8-1.2          # High creativity
top_p: 0.9-0.95              # Broad sampling
min_p: 0.01                  # Allow creative tokens
presence_penalty: 0.3-0.6    # Encourage novelty
```

### Technical/Coding Tasks
```yaml
model: "deepseek/deepseek-coder"
temperature: 0.3-0.5          # Balanced precision/creativity
response_format:              # Structured output
  type: "json_object"
repetition_penalty: 1.1-1.3   # Avoid repetitive code patterns
```

### Production/Reliable Tasks
```yaml
models:                       # Fallback models
  - "anthropic/claude-4-sonnet-20250522"
  - "openai/gpt-4-turbo"
provider:
  order: ["Anthropic", "OpenAI"]
  allow_fallbacks: true
usage:
  include: true              # Track costs
```

## Package Entry Points
Defined in pyproject.toml:
- openrouter-runner = "openrouter_interface.cli:main"
- openrouter-web = "openrouter_interface.web:main"
- openrouter-chain = "openrouter_interface.chain:main"
- bookgen = "openrouter_interface.bookGen:main"