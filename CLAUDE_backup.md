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
- Multi-step workflow execution engine with fault tolerance
- YAML-based configuration for prompt sequences
- Progress tracking and intermediate file management with colored console output
- Background execution support for long-running processes
- Error handling with `on_error` behavior (stop/continue)
- Automatic file size validation and quality control
- Substep support (e.g., 6.1, 6.2) for complex workflows

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
- **Multi-pass execution**: Each step can run multiple passes with `passes: N` setting
- **Content append mode**: Each step can append output to input with `append: yes` setting
- **Global pre/post processing**: Execute custom scripts before and after chain processing
- **Per-step pre/post processing**: Individual prescript and postscript for each step with variable substitution
- **Error handling control**: Per-step `on_error: stop/continue` behavior
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

  # Phase 3: Technical review with structured output and multi-pass execution
  prompt 3:
    name: "final_review"
    prompt_file: "review.json"
    model: "deepseek/deepseek-coder" # Specialized technical model
    temperature: 0.4               # Balanced for technical accuracy
    passes: 2                      # Two-pass review for thoroughness
    on_error: continue             # Skip if technical model fails
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

  # Phase 4: Content accumulation with append mode
  prompt 4:
    name: "content_accumulation"
    prompt_file: "summarize.json"
    append: yes                    # Append output to input for content accumulation
    passes: 3                      # Multiple passes with accumulation
    temperature: 0.6               # Balanced for summarization

  # Phase 5: Disabled optional enhancement
  prompt 5:
    name: "optional_enhancement"
    prompt_file: "enhance.json"
    passes: 0                      # Skip this step entirely
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

### Substep Support and Advanced Chain Features

#### Substep Configuration
The system supports decimal substeps (e.g., 6.1, 6.2) for complex workflows that require multiple phases within a logical step:

```yaml
prompts:
  # Main dialogue enhancement phase
  prompt 6:
    name: "dialogue_enhancement"
    prompt_file: "6_dialogue_enhancement.json"
    model: "openai/gpt-4.1"
    temperature: 1.2

  # Optional character-specific dialogue pass
  prompt 6.1:
    name: "character_dialogue_pass"
    prompt_file: "6.5_character_dialogue_pass.json"
    model: "openai/gpt-4o"
    temperature: 0.8
    on_error: continue  # Optional enhancement that can be skipped

  # Additional dialogue refinement
  prompt 6.2:
    name: "dialogue_polish"
    prompt_file: "dialogue_polish.json"
    temperature: 0.6

  # Continue with next main phase
  prompt 7:
    name: "weak_language_cleanup"
    prompt_file: "7_weak_language_cleanup.json"
```

#### Enhanced Console Output
- **Colored Status Indicators**: Green ✅, Yellow ⚠️, Red ❌
- **Timing Information**: Execution time for each step
- **Progress Tracking**: "File X, Step Y/Total" format
- **File Size Reporting**: Decimal precision (52B, 14.5k, 1.2M)
- **Step Identification**: Clear display of step numbers including substeps (1, 6.1, 6.2, etc.)

#### Chain Execution Features
- **Automatic File Management**: Intermediate files preserved in temp directories
- **Step-by-Step Validation**: Each step verified before proceeding
- **Comprehensive Logging**: Detailed execution logs with timestamps
- **Background Processing**: Long-running chains with progress persistence
- **Final Reports**: Summary of all steps with file sizes and status indicators

## Environment Variables
- **OPENROUTER_API_KEY**: Required for API access
- **OPENROUTER_MODEL**: Override default model
- **OPENROUTER_LOG_LEVEL**: Override logging level

## Error Handling and Fault Tolerance

### On-Error Behavior Control

The system now supports configurable error handling behavior for each step in a prompt chain, providing robust fault tolerance for complex workflows.

#### Configuration Options
- **`on_error: stop`** (default): Stop execution when a step fails
- **`on_error: continue`**: Skip failed step and pass input file through unchanged

#### Per-Step Error Handling
```yaml
prompts:
  # Normal step that will stop on failure (default behavior)
  prompt 1:
    name: "critical_step"
    prompt_file: "analysis.json"
    # Implicit: on_error: stop

  # Step that will continue on failure
  prompt 2:
    name: "optional_enhancement"
    prompt_file: "enhancement.json"
    on_error: continue

  # Subsequent steps continue normally
  prompt 3:
    name: "final_step"
    prompt_file: "finalize.json"
```

#### Error Handling Features
- **Execution Error Handling**: API failures, invalid models, network issues
- **File Verification Error Handling**: File size validation failures, output verification issues
- **File Passthrough**: When a step is skipped, input file is copied unchanged to output location
- **Visual Indicators**: Clear console output with colored status indicators:
  - ✅ **Green**: Successful steps
  - ⚠️ **Yellow**: Skipped steps with "(on_error: continue)" message
  - ❌ **Red**: Failed steps that stop execution
- **Detailed Logging**: Comprehensive logging of skip reasons and actions taken
- **Final Reports**: Updated reports show "skipped" status with appropriate icons

#### Example Error Handling Scenario
```yaml
prompts:
  prompt 1:
    name: "grammar_check"
    prompt_file: "grammar.json"
    # This step must succeed

  prompt 2:
    name: "style_enhancement"
    prompt_file: "style.json"
    model: "advanced/experimental-model"  # Might fail
    on_error: continue                    # Skip if it fails

  prompt 3:
    name: "final_review"
    prompt_file: "review.json"
    # This step gets the original input if step 2 was skipped
```

## Pre/Post Processing Scripts

### Script Configuration

The system supports execution of custom shell scripts and commands before and after chain processing. This feature enables integration with external tools, data preparation workflows, cleanup operations, and custom automation tasks.

#### Configuration Options
- **`preprocessing`**: Scripts executed before chain processing begins
- **`postprocessing`**: Scripts executed after chain processing completes
- **Script Numbering**: Up to 99 scripts per phase (script01-script99)
- **Optional Names**: Human-readable names for scripts (name01-name99)
- **Execution Order**: Scripts execute in numerical order based on suffix
- **Default Behavior**: No scripts execute if sections not present in config

#### Script Execution Behavior
- **Sequential Processing**: Scripts execute one at a time in numerical order
- **Error Propagation**: Script failure halts chain execution immediately
- **Timeout Protection**: 5-minute timeout per script prevents hanging
- **Shell Environment**: Full access to system shell and environment variables
- **Output Capture**: stdout and stderr captured and logged to files
- **Minimal Console Output**: Clean, concise status reporting with execution times
- **Working Directory**: Scripts execute from chain configuration directory

#### Pre/Post Processing Configuration Examples

```yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

# Input/output configuration
input_file: documents/source.md
output_file: documents/processed.md

# Preprocessing scripts - execute before chain starts
preprocessing:
  script01: echo "Starting document processing pipeline"
  name01: "Initialize Pipeline"
  script02: python3 scripts/validate_input.py
  name02: "Validate Input Data"
  script03: ./scripts/prepare_environment.sh
  name03: "Setup Environment"
  script04: mkdir -p output/logs
  name04: "Create Directories"
  script05: cp source_backup.md backup/
  name05: "Backup Source Files"

# Postprocessing scripts - execute after chain completes
postprocessing:
  script01: python3 scripts/validate_output.py
  name01: "Validate Results"
  script02: ./scripts/generate_report.sh
  name02: "Generate Reports"
  script03: echo "Processing pipeline completed"
  name03: "Pipeline Complete"

# Chain configuration
prompts:
  prompt 1:
    name: "content_processing"
    prompt_file: "analysis.json"
```

#### Real-World Use Cases

**Data Pipeline Integration:**
```yaml
preprocessing:
  script01: python3 etl/extract_data.py
  name01: "Extract Raw Data"
  script02: python3 etl/transform_data.py
  name02: "Transform Data"
  script03: python3 etl/validate_schema.py
  name03: "Validate Schema"

postprocessing:
  script01: python3 etl/load_results.py
  name01: "Load to Database"
  script02: python3 etl/cleanup_temp.py
  name02: "Cleanup Temp Files"
  script03: ./scripts/send_notification.sh
  name03: "Send Notifications"
```

**Development Workflow:**
```yaml
preprocessing:
  script01: git pull origin main
  script02: npm install
  script03: npm run build
  script04: pytest tests/

postprocessing:
  script01: npm run test
  script02: ./scripts/deploy.sh
  script03: git tag -a "v$(date +%Y%m%d)" -m "Automated release"
```

**File Management and Backup:**
```yaml
preprocessing:
  script01: ./scripts/backup_inputs.sh
  script02: python3 scripts/check_disk_space.py
  script03: mkdir -p logs/$(date +%Y-%m-%d)

postprocessing:
  script01: ./scripts/archive_outputs.sh
  script02: python3 scripts/generate_metadata.py
  script03: rsync -av outputs/ backup_server:/backups/
```

**Quality Assurance Pipeline:**
```yaml
preprocessing:
  script01: python3 qa/spell_check.py
  script02: python3 qa/format_validation.py
  script03: ./scripts/style_guide_check.sh

postprocessing:
  script01: python3 qa/output_validation.py
  script02: python3 qa/metrics_calculation.py
  script03: ./scripts/generate_qa_report.sh
```

#### Console Output Features

The system provides clean, minimal console output while preserving detailed information in log files.

**Console Output Format:**
```
Pre Processing:
Executing script 1: Initialize Environment
Result:   ✅ complete:  time 0.5 seconds

Executing script 2: Validate Input Data
Result:   ✅ complete:  time 2.1 seconds

Executing Prompt 1: content_processing
preprocessing script:   ✅  successfully run
Result:   ✅ prompt 1 content_processing output size: 14.5k time: 16.8 seconds
postprocessing script:   ✅  successfully run

Post Processing:
Executing script 1: Validate Results
Result:   ✅ complete:  time 1.3 seconds
```

**Console Output Features:**
- **Phase Headers**: Clear "Pre Processing:" and "Post Processing:" section dividers
- **Script Names**: Human-readable script names displayed instead of commands
- **Minimal Status**: Simple "✅ complete:" or "❌ failed:" indicators
- **Execution Timing**: Precise timing information for performance monitoring
- **Consistent Formatting**: Matches prompt execution result format
- **Error Details**: Failure reasons shown concisely (exit codes, timeouts, errors)

**Detailed Logging to Files:**
- **Full Commands**: Complete script commands logged to file
- **stdout/stderr**: All script output captured in log files
- **Execution Context**: Script names, numbers, and detailed timing
- **Debug Information**: Comprehensive execution details for troubleshooting

#### Script Management Best Practices
- **Executable Permissions**: Ensure script files have proper execute permissions
- **Error Handling**: Scripts should return appropriate exit codes (0 for success)
- **Path Management**: Use absolute paths or ensure scripts are in PATH
- **Logging**: Consider adding logging within scripts for detailed debugging
- **Idempotency**: Design scripts to be safely re-runnable
- **Resource Cleanup**: Ensure scripts clean up temporary resources on completion

#### Error Handling and Debugging
- **Script Failures**: Any script failure immediately halts chain execution
- **Timeout Handling**: Scripts exceeding 5-minute timeout are terminated
- **Error Logging**: Detailed error messages logged to chain log file
- **stdout/stderr Capture**: All script output captured for debugging
- **Exit Code Reporting**: Non-zero exit codes reported with context
- **Debugging Support**: Use `--debug` flag for verbose script execution logs

#### Integration with Other Features
- **Chain Independence**: Scripts execute regardless of prompt chain success/failure
- **Multi-File Compatibility**: Scripts execute once per chain, not per input file
- **Config Override**: Scripts use same configuration directory as chain
- **Temp Directory**: Scripts can access chain temp directory for intermediate files
- **Environment Access**: Full access to environment variables and system tools

## Per-Phase Pre/Post Processing Scripts

### Per-Step Script Configuration

The system supports individual prescript and postscript execution for each prompt step. This feature enables step-specific preparation, validation, and cleanup operations with dynamic file path substitution.

#### Configuration Options
- **`prescript`**: Single script executed before the prompt step
- **`postscript`**: Single script executed after the prompt step completes
- **Variable Substitution**: {input_file} and {output_file} replaced with actual file paths
- **Error Handling**: Prescript failure aborts the step; postscript failure is logged but continues
- **Default Behavior**: No scripts execute if not specified in step configuration

#### Variable Substitution
- **`{input_file}`**: Replaced with the actual input file path for the step
- **`{output_file}`**: Replaced with the actual output file path for the step
- **Path Resolution**: All paths are absolute and fully resolved
- **File Accessibility**: Scripts can access and modify the specified files

#### Per-Phase Script Configuration Examples

```yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

input_file: document.md
output_file: processed_document.md

prompts:
  prompt 1:
    prescript: "touch {input_file}.backup"
    name: "grammar_foundation"
    prompt_file: "1_grammar_foundation.json"
    model: "google/gemini-2.0-flash-001"
    temperature: 0.2
    postscript: "ls -haltr {output_file}"

  prompt 2:
    prescript: "echo 'Processing: {input_file}' >> processing.log"
    name: "content_enhancement"
    prompt_file: "2_content_enhancement.json"
    temperature: 0.5
    postscript: "wc -l {output_file} > {output_file}.stats"

  prompt 3:
    name: "final_review"
    prompt_file: "3_final_review.json"
    postscript: "cp {output_file} final_backup.md"
    # No prescript for this step
```

#### Real-World Use Cases

**File Validation and Backup:**
```yaml
prompt 1:
  prescript: "cp {input_file} {input_file}.backup && chmod 644 {input_file}"
  name: "content_processing"
  prompt_file: "process.json"
  postscript: "diff {input_file} {output_file} > changes.log"
```

**Progress Tracking:**
```yaml
prompt 1:
  prescript: "echo 'Starting step 1 at $(date)' >> progress.log"
  name: "analysis"
  prompt_file: "analyze.json"
  postscript: "echo 'Step 1 completed: $(wc -w {output_file})' >> progress.log"
```

**Quality Assurance:**
```yaml
prompt 1:
  prescript: "python3 validate_input.py {input_file}"
  name: "content_check"
  prompt_file: "check.json"
  postscript: "python3 validate_output.py {output_file} || exit 1"
```

**File Format Conversion:**
```yaml
prompt 1:
  prescript: "pandoc {input_file} -o {input_file}.html"
  name: "format_processing"
  prompt_file: "format.json"
  postscript: "pandoc {output_file} -o {output_file}.pdf"
```

#### Console Output Format

```
Executing Prompt 1: grammar_foundation
preprocessing script:   ✅  successfully run
Result:   ✅ prompt 1 grammar_foundation output size: 14.5k time: 16.8 seconds
postprocessing script:   ✅  successfully run
```

#### Execution Flow
1. **Prescript Execution**: Runs before prompt processing with current step input
2. **Prompt Processing**: Normal prompt execution with AI model
3. **Postscript Execution**: Runs after prompt completion with step output
4. **Error Handling**: Prescript failure aborts step; postscript failure continues chain
5. **Variable Substitution**: File paths resolved before script execution

#### Best Practices
- **Prescript Safety**: Use for validation, backup, and preparation tasks
- **Postscript Utility**: Use for verification, reporting, and cleanup tasks
- **Error Handling**: Design scripts with proper exit codes for error detection
- **Path Management**: Scripts receive absolute paths for reliable file access
- **Resource Cleanup**: Use postscripts to clean up temporary resources
- **Logging Integration**: Scripts can write to separate log files for detailed tracking

#### Integration with Global Scripts
- **Execution Order**: Global preprocessing → Step prescripts → Prompts → Step postscripts → Global postprocessing
- **Configuration Compatibility**: Per-step scripts work alongside global pre/post processing
- **Variable Scope**: Global scripts have no access to step-specific file paths
- **Error Propagation**: All script types can halt chain execution on failure
- **Logging Separation**: Per-step scripts logged with step context in main log file

## Content Append Mode

### Append Configuration

The system supports content accumulation through the `append` setting, allowing output to be appended to input instead of replacing it. This feature is ideal for creating summaries of multiple documents or building comprehensive content from multiple processing passes.

#### Configuration Options
- **`append: yes`**: Append output to input (content accumulation mode)
- **`append: no`**: Replace input with output (default behavior)
- **`append: true/false`**: Boolean values also supported
- **`append: 1/0`**: Numeric string values supported
- **Default**: `false` (no append behavior)

#### Append Behavior
- **Content Concatenation**: Output is appended to input with separator: `input + "\n\n" + output`
- **File Naming**: Appended files get `_appended` suffix in their names
- **Chain Continuity**: Next step receives the accumulated content as input
- **Pass Integration**: Works seamlessly with multi-pass execution for iterative accumulation
- **Intermediate Preservation**: All intermediate files preserved in temp directory

#### Content Append Configuration Examples

```yaml
prompts:
  # Normal processing (default behavior)
  prompt 1:
    name: "initial_processing"
    prompt_file: "process.json"
    # Implicit: append: no

  # Simple append mode
  prompt 2:
    name: "content_accumulation"
    prompt_file: "summarize.json"
    append: yes                    # Append output to input

  # Append with multi-pass for iterative accumulation
  prompt 3:
    name: "iterative_accumulation"
    prompt_file: "refine_summary.json"
    append: true                   # Boolean format
    passes: 3                      # Each pass appends to growing content

  # Append with string values
  prompt 4:
    name: "final_accumulation"
    prompt_file: "finalize.json"
    append: "yes"                  # String format supported
```

#### Real-World Use Cases

**Multi-Document Summarization:**
```yaml
prompts:
  prompt 1:
    name: "document_summary"
    prompt_file: "create_summary.json"
    append: yes                    # Accumulate summaries from multiple docs
    passes: 1                      # Single pass per document
```

**Iterative Content Building:**
```yaml
prompts:
  prompt 1:
    name: "content_expansion"
    prompt_file: "expand_content.json"
    append: yes                    # Build content progressively
    passes: 5                      # Multiple expansion passes
    temperature: 0.7              # Consistent creativity
```

**Research Compilation:**
```yaml
prompts:
  prompt 1:
    name: "research_gathering"
    prompt_file: "gather_research.json"
    append: yes                    # Compile research findings

  prompt 2:
    name: "analysis_addition"
    prompt_file: "add_analysis.json"
    append: yes                    # Add analysis to research
    temperature: 0.4              # Analytical processing
```

#### Console Output Features
- **Append Indicators**: Shows "(append mode)" in console output
- **Combined Display**: Shows "(N passes, append mode)" for multi-pass append steps
- **File Size Tracking**: Displays accumulating file sizes as content grows
- **Status Reporting**: Clear indication when content is being accumulated vs replaced

#### File Management
- **Intermediate Files**: Each append creates: `input_step_X_name_appended.ext`
- **Pass Integration**: Multi-pass append creates: `input_step_X_name_pass_N_appended.ext`
- **Final Output**: Last append result becomes the step's final output
- **Chain Continuity**: Next step receives accumulated content as input
- **Temp Preservation**: All intermediate files preserved for analysis and debugging

#### Integration with Other Features
- **Multi-Pass Compatibility**: Append works with any number of passes
- **Error Handling**: Compatible with `on_error: continue` for fault tolerance
- **File Size Validation**: Append mode considered in size validation calculations
- **Parameter Overrides**: Append setting can be combined with any API parameter overrides

## Multi-Pass Execution

### Passes Configuration

The system supports iterative processing through the `passes` setting, allowing each step to be executed multiple times with chained output.

#### Configuration Options
- **`passes: N`**: Execute the step N times (default: 1, maximum: 99)
- **`passes: 0`**: Skip the step entirely (equivalent to disabling the step)
- **`passes: <negative>`**: Skip the step entirely (treated same as 0)

#### Pass Execution Behavior
- **Pass Chaining**: Output from pass 1 becomes input for pass 2, and so on
- **File Naming**: Each pass creates a separate file: `_pass_1`, `_pass_2`, etc.
- **Final Output**: The last pass output becomes the step's final output
- **Timing**: All passes are timed together as a single step execution
- **Validation**: Each pass is individually validated before proceeding

#### Multi-Pass Configuration Examples

```yaml
prompts:
  # Single pass (default behavior)
  prompt 1:
    name: "initial_processing"
    prompt_file: "process.json"
    # Implicit: passes: 1

  # Multi-pass iterative refinement
  prompt 2:
    name: "iterative_improvement"
    prompt_file: "refine.json"
    passes: 3                    # Run 3 times, each pass refines the previous

  # Skip step entirely
  prompt 3:
    name: "optional_step"
    prompt_file: "optional.json"
    passes: 0                    # Step will be skipped

  # High-iteration processing
  prompt 4:
    name: "deep_refinement"
    prompt_file: "polish.json"
    passes: 10                   # Maximum refinement passes

  # Disabled step (negative passes)
  prompt 5:
    name: "disabled_step"
    prompt_file: "disabled.json"
    passes: -1                   # Step will be skipped
```

#### Real-World Use Cases

**Iterative Content Refinement:**
```yaml
prompts:
  prompt 1:
    name: "content_polish"
    prompt_file: "polish_text.json"
    passes: 5                    # Polish text through 5 iterations
    temperature: 0.7            # Consistent creativity level
```

**Progressive Style Application:**
```yaml
prompts:
  prompt 1:
    name: "style_application"
    prompt_file: "apply_style.json"
    passes: 3                    # Apply style guide progressively
    temperature: 0.4            # Consistent style application
```

**Quality Assurance Pipeline:**
```yaml
prompts:
  prompt 1:
    name: "grammar_check"
    prompt_file: "grammar.json"
    passes: 2                    # Two-pass grammar checking

  prompt 2:
    name: "fact_check"
    prompt_file: "facts.json"
    passes: 3                    # Thorough fact verification

  prompt 3:
    name: "final_review"
    prompt_file: "review.json"
    passes: 1                    # Single final review
```

#### Console Output Features
- **Pass Progress**: Shows "Executing Prompt X: name (N passes)" for multi-pass steps
- **Pass Execution**: Logs each individual pass as "Executing pass X/N"
- **Results Display**: Shows "(N passes)" in final results
- **Timing**: Combined execution time across all passes
- **File Tracking**: Individual pass files preserved in temp directory

#### File Management
- **Intermediate Files**: Each pass creates: `input_step_X_name_pass_N.ext`
- **Final Output**: Last pass output becomes the step's result
- **Chain Continuity**: Next step receives the final pass output as input
- **Temp Preservation**: All pass files preserved for debugging and analysis

## File Size Validation

The system includes automatic file size validation to detect when processing significantly changes file sizes, which can indicate issues like incomplete processing, truncated output, or AI hallucination.

### Configuration
```yaml
# Global configuration or in individual config files
file_size_validation:
  enabled: true                        # Enable/disable validation (default: true)
  max_size_difference_percent: 50      # Maximum size difference % (default: 50%, updated from 30%)
  min_file_size_bytes: 100            # Minimum acceptable file size (default: 100)
```

### Chain Configuration Example
```yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7
  max_tokens: 20000
  file_size_validation:
    enabled: true
    max_size_difference_percent: 25    # Stricter validation (25% instead of 30%)
    min_file_size_bytes: 200          # Higher minimum size requirement

prompts:
  prompt 1:
    name: "content_analysis"
    prompt_file: "analysis.json"
    # Inherits global file size validation settings
```

### Validation Behavior
- **Size Comparison**: Output file size is compared to input file size
- **Percentage Check**: Fails if output is more than `max_size_difference_percent` larger or smaller
- **Minimum Size**: Fails if output is smaller than `min_file_size_bytes`
- **Chain Failure**: File size validation failure causes chain to fail at that step (unless `on_error: continue`)
- **Error Handling Integration**: Works with `on_error` behavior - validation failures can be skipped
- **Logging**: Detailed logging shows input size, output size, and percentage difference with decimal precision (e.g., 14.5k vs 14k)
- **File Size Display**: Human-readable format with 1 decimal place (B, k, M, G)

### Common Use Cases
- **Content Processing**: Detect truncated or incomplete AI responses
- **Text Enhancement**: Ensure content isn't dramatically shortened or expanded unexpectedly
- **Quality Control**: Catch cases where AI returns error messages instead of processed content
- **Pipeline Reliability**: Fail fast when processing pipeline produces unexpected results

### Disabling Validation
```yaml
# Disable globally
file_size_validation:
  enabled: false

# Or per-step (if needed for specific prompts that legitimately change size dramatically)
# Note: Per-step file size validation overrides are not currently supported
# but can be requested as a feature enhancement
```

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

## Model Compatibility and Parameter Filtering

The system provides intelligent, automatic parameter filtering based on the specific model being used. You can configure any parameters in your config files - incompatible ones will be automatically filtered out without causing errors.

### Automatic Parameter Management
- **Smart Filtering**: Incompatible parameters are automatically removed for each model
- **Parameter Conversion**: Model-specific parameter names are automatically converted (e.g., `max_tokens` → `max_output_tokens` for Gemini)
- **Comprehensive Logging**: All filtering and conversion actions are logged for transparency
- **Zero Configuration**: No need to create model-specific configs - use any parameter combination

### Google Gemini Models
When using Google Gemini models (e.g., `google/gemini-1.5-pro`, `google/gemini-2.0-flash-001`):

**Automatic Parameter Conversion:**
- `max_tokens` → `max_output_tokens` - Gemini uses different parameter name

**Automatically Filtered Parameters:**
- `user` - User identifier not supported by Gemini API
- `top_k` - Uses different sampling approach than OpenRouter standard
- `frequency_penalty` - Not supported in Gemini API
- `presence_penalty` - Not supported in Gemini API
- `repetition_penalty` - Alternative repetition control not available
- `top_logprobs` - Token probability logging not supported
- `seed` - Deterministic output control not available
- `min_p` - Minimum probability threshold not supported

### Anthropic Claude Models
Claude models (e.g., `anthropic/claude-4-sonnet-20250522`) support most API parameters with minimal restrictions:
- **Full Support**: Most OpenRouter API parameters work natively
- **High Compatibility**: Advanced sampling controls, penalties, and response formatting supported

### OpenAI Models
OpenAI models (e.g., `openai/gpt-4-turbo`, `openai/gpt-4o`) offer comprehensive API parameter support:
- **Complete Feature Set**: All advanced sampling controls supported
- **Structured Output**: JSON response formatting available
- **Token Analysis**: Top logprobs and detailed response analysis
- **Deterministic Output**: Seed-based reproducible results

### DeepSeek and Other Models
- **Automatic Detection**: System identifies model capabilities automatically
- **Best Effort**: Maximum compatible parameter set is used
- **Graceful Fallback**: Unsupported parameters are silently filtered

**Important**: Parameter filtering is completely transparent and logged. You can use comprehensive parameter sets in your configurations - the system ensures only compatible parameters reach each model's API.

## Recent Feature Additions

### Per-Phase Pre/Post Processing Scripts (Latest)
- **Per-Step Scripts**: Individual prescript and postscript for each prompt step
- **Variable Substitution**: {input_file} and {output_file} dynamic path replacement
- **Single Script Support**: One prescript and one postscript per step maximum
- **Execution Timing**: Prescript before prompt, postscript after prompt completion
- **Console Integration**: Minimal output format matching global script execution
- **Detailed Logging**: Full command substitution and execution details in log files

### Global Pre/Post Processing Scripts
- **Script Execution**: Execute up to 99 preprocessing and postprocessing scripts per chain
- **Optional Script Names**: Human-readable names (name01-name99) for better console output
- **Numbered Ordering**: Scripts execute in numerical order (script01-script99)
- **Shell Command Support**: Full shell command and script file execution capabilities
- **Minimal Console Output**: Clean status reporting with script names and execution times
- **Detailed File Logging**: Complete script commands and output captured in log files
- **Timeout Protection**: 5-minute timeout per script with automatic failure handling
- **Error Handling**: Script failures halt chain execution with detailed error reporting

### Content Append Mode
- **Append Configuration**: Per-step `append: yes` setting for content accumulation
- **Content Accumulation**: Output is appended to input instead of replacing it
- **Multi-Document Processing**: Ideal for creating summaries by combining multiple documents
- **Flexible Settings**: Supports boolean (`true/false`) and string (`yes/no`) values
- **Pass Integration**: Works seamlessly with multi-pass execution for iterative accumulation
- **Intermediate Preservation**: All intermediate files preserved in temp directory for analysis

### Multi-Pass Execution Control
- **Passes Configuration**: Per-step `passes: N` setting for iterative processing
- **Pass Chaining**: Output from pass N becomes input for pass N+1
- **Skip Behavior**: `passes: 0` or negative values skip the step entirely
- **Maximum Limit**: Up to 99 passes per step supported
- **Enhanced Naming**: Pass-specific intermediate files (`_pass_1`, `_pass_2`, etc.)
- **Console Progress**: Clear indication of passes count and current pass execution

### Error Handling and Fault Tolerance
- **On-Error Behavior Control**: Per-step configuration with `on_error: stop/continue`
- **File Passthrough**: Automatic input file copying for skipped steps
- **Enhanced Console Output**: Colored status indicators (✅⚠️❌) with timing
- **Intelligent Error Recovery**: Handles both execution and validation failures

### File Size Validation and Quality Control
- **Automatic Output Validation**: Detects truncated or malformed AI responses
- **Configurable Thresholds**: Customizable size difference percentages and minimum sizes
- **Integration with Error Handling**: Validation failures can be skipped with `on_error: continue`
- **Improved Default**: Updated from 30% to 50% size difference threshold for better usability

### Substep Support and Advanced Workflows
- **Decimal Step Numbers**: Support for 6.1, 6.2, etc. for complex multi-phase processing
- **Enhanced Sorting**: Proper ordering of main steps and substeps
- **String-Based Step Handling**: Improved internal processing for mixed step formats

### Enhanced API Parameter Support
- **Complete OpenRouter API Coverage**: All available parameters now supported
- **Intelligent Model Compatibility**: Automatic parameter filtering per model
- **Parameter Conversion**: Automatic handling of model-specific parameter names
- **Comprehensive Logging**: Full transparency of parameter handling

### Console and Reporting Improvements
- **Decimal Precision File Sizes**: Display with 1 decimal place (14.5k vs 14k)
- **Colored Output**: Green/Yellow/Red status indicators throughout
- **Execution Timing**: Per-step timing information
- **Enhanced Final Reports**: Comprehensive status summaries with visual indicators

## Package Entry Points
Defined in pyproject.toml:
- openrouter-runner = "openrouter_interface.cli:main"
- openrouter-web = "openrouter_interface.web:main"
- openrouter-chain = "openrouter_interface.chain:main"
- bookgen = "openrouter_interface.bookGen:main"