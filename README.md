# OpenRouter Prompt Runner

A comprehensive tool for executing JSON prompt files using the OpenRouter API. Available as both a **command-line interface (CLI)** and a **Flask web application**. Choose the interface that best fits your workflow!

## 🚀 Interfaces Available

### 📟 Command Line Interface (CLI)
Perfect for automation, batch processing, and CI/CD pipelines:
- **Batch mode**: Process specific files directly
- **Interactive mode**: Browse and select files interactively
- **Configuration management**: YAML config files and command-line overrides
- **Logging**: File and console logging with multiple levels

### 🌐 Web Application
Ideal for interactive use and team collaboration:
- **Web interface**: Modern, responsive design
- **Session management**: Track history and download results
- **Configuration UI**: Web-based settings management
- **File uploads**: Drag-and-drop file processing

### ⛓️ Prompt Chain Runner
Advanced automation for multi-step AI workflows:
- **Sequential Processing**: Execute 1-99 prompts in sequence
- **Multi-File Support**: Process multiple files through the same prompt chain
- **Per-Prompt Configuration**: Use different LLMs for each step (Claude, GPT-4, DeepSeek, etc.)
- **Advanced File Management**: Organized temp directories with full traceability
- **Flexible Output**: Pattern-based naming for batch processing

---

---

## 🛠️ Setup and Installation

### Quick Setup (Recommended)

For complete setup instructions, see the **[Setup Guide (README_setup.md)](README_setup.md)**.

**One-command automated setup:**
```bash
# Download project files, then run:
chmod +x setup_prompt_runner.sh
./setup_prompt_runner.sh
```

This automated script will:
- ✅ Check Python 3 installation
- ✅ Install all required packages
- ✅ Make files executable
- ✅ Install to `~/.local/bin` for system-wide access
- ✅ Verify everything works

### Manual Setup

If you prefer manual installation, see the detailed instructions in [README_setup.md](README_setup.md).

---

## 📟 Command Line Interface (CLI)

### 🛠️ CLI Setup

#### 1. Required Files
Ensure you have all necessary Python modules:
```
project/
├── prompt_runner.py                    # Main CLI application
├── config_manager.py                   # Configuration handling
├── logging_manager.py                  # Logging setup
├── prompt_scanner.py                   # JSON prompt discovery
├── prompt_handler.py                   # Prompt loading and processing
├── input_handler.py                    # Input file handling
├── prompt_runner_api_client.py         # OpenRouter API client
├── response_handler.py                 # Output handling
├── file_handler.py                     # File operations
├── *.json                             # Your JSON prompt files
└── openrouter_editor.yaml             # Optional config file
```

#### 2. Install Dependencies
```bash
pip install requests pyyaml
```

#### 3. Set API Key
```bash
# Set your OpenRouter API key as environment variable
export OPENROUTER_API_KEY="your_api_key_here"

# Or add it to your config file (not recommended for security)
echo "api_key: your_api_key_here" >> openrouter_editor.yaml
```

### 🔧 CLI Configuration

#### Command Line Options
```bash
python prompt_runner.py [OPTIONS]

Mode Selection:
  -p, --prompt PROMPT_FILE     JSON prompt file (enables batch mode)
  -i, --input INPUT_FILE       Input file to process (requires --prompt)

Configuration Options:
  -c, --config CONFIG_FILE     Configuration file (YAML format)

Output Options:
  -o, --output-file OUTPUT     Output file for responses (markdown)

Logging Options:
  -l, --log-file LOG_FILE      Log file path (enables file logging)
  -v, --verbose                Enable verbose logging (DEBUG level)
  -q, --quiet                  Suppress output except errors
  --temp-dir TEMP_DIR          Temporary directory for logs and payload files

Help:
  -h, --help                   Show help message and examples
```

#### Configuration File Format
Create `openrouter_editor.yaml`:
```yaml
# OpenRouter API Settings
model: anthropic/claude-4-sonnet-20250522
api_base_url: https://openrouter.ai/api/v1
temperature: 0.8
max_tokens: 25000

# Application Settings
log_level: INFO
log_to_file: false                      # Set true to enable file logging
log_file: prompt_runner.log             # Automatically enables file logging
payload_file: prompt_runner.payload.json

# Input/Output Settings
input_file: input.md
output_file: output.md
action_file: action.json
```

### 📝 CLI Usage Examples

#### Interactive Mode (Default)
```bash
# Basic interactive mode - scan directory and select files
python prompt_runner.py

# Interactive with output file
python prompt_runner.py -o responses.md

# Interactive with custom config
python prompt_runner.py -c my_config.yaml -o responses.md

# Interactive with verbose logging to file
python prompt_runner.py -l debug.log -v -o responses.md
```

#### Batch Mode
```bash
# Basic batch processing
python prompt_runner.py -p analysis.json -i document.md

# Batch with output file
python prompt_runner.py -p review.json -i code.py -o results.md

# Batch with custom config
python prompt_runner.py -p analysis.json -i data.txt -c config.yaml -o analysis.md

# Batch with logging
python prompt_runner.py -p review.json -i code.py -l batch.log -o results.md
```

#### Batch Processing Multiple Files
```bash
# Process multiple files with same prompt - perfect for automation
python prompt_runner.py -p review.json -i file1.md -o results.md -l batch.log
python prompt_runner.py -p review.json -i file2.md -o results.md -l batch.log
python prompt_runner.py -p review.json -i file3.md -o results.md -l batch.log

# Or use a loop for many files
for file in *.md; do
    python prompt_runner.py -p review.json -i "$file" -o results.md -l batch.log
done
```

#### Configuration Combinations
```bash
# Command line log file overrides config
python prompt_runner.py -c config.yaml -l custom.log -p analysis.json -i doc.md

# Mix command line and config file settings
python prompt_runner.py -c base_config.yaml -p custom_prompt.json -i input.txt -l debug.log -v

# Use custom temp directory for organized file management
python prompt_runner.py -p analysis.json -i document.md --temp-dir temp/analysis_run
```

### 🔍 CLI Workflow Examples

#### Development and Testing
```bash
# Debug a specific prompt with verbose logging
python prompt_runner.py -p debug_prompt.json -i test_input.md -l debug.log -v

# Quick test without saving output
python prompt_runner.py -p test.json -i sample.md -q

# Test with different models using config
python prompt_runner.py -c gpt4_config.yaml -p analysis.json -i document.md
```

#### Production Batch Processing
```bash
# Process a batch of documents with consistent logging
mkdir -p logs outputs
for doc in inputs/*.md; do
    filename=$(basename "$doc" .md)
    python prompt_runner.py \
        -p production_review.json \
        -i "$doc" \
        -o "outputs/${filename}_review.md" \
        -l "logs/batch_$(date +%Y%m%d).log" \
        -c production_config.yaml
done
```

#### CI/CD Integration
```bash
# Automated analysis in CI pipeline
python prompt_runner.py \
    -p code_review.json \
    -i src/main.py \
    -o reports/code_analysis.md \
    -l logs/ci_analysis.log \
    -c ci_config.yaml || exit 1

# Exit code 0 = success, 1 = failure (perfect for scripts)
```

### 📊 CLI Output and Logging

#### Console Output
```bash
# Normal operation shows progress
$ python prompt_runner.py -p analysis.json -i document.md
2025-01-26 10:30:15 - INFO - Initializing OpenRouter Prompt Runner
2025-01-26 10:30:15 - INFO - ✓ Files validated successfully
2025-01-26 10:30:15 - INFO - ✓ Prompt loaded successfully
2025-01-26 10:30:15 - INFO - ✓ Input content loaded
2025-01-26 10:30:16 - INFO - ✓ API call successful
✓ Successfully processed document.md with analysis.json
```

#### Log File Contents
When using `-l` or config file logging:
```
================================================================================
NEW SESSION STARTED
================================================================================
2025-01-26 10:30:15 - INFO - Initializing OpenRouter Prompt Runner
2025-01-26 10:30:15 - INFO - Command line log file specified: batch.log
2025-01-26 10:30:15 - INFO - ✓ Logging to file: batch.log
2025-01-26 10:30:15 - INFO - Model: anthropic/claude-4-sonnet-20250522
2025-01-26 10:30:15 - INFO - API call completed in 1.23 seconds
2025-01-26 10:30:15 - INFO - ✓ Batch processing completed successfully
```

#### Output File Format
When using `-o output.md`:
```markdown
## Prompt Response - 2025-01-26 10:30:16

**Prompt File:** `analysis.json`  
**Input File:** `document.md`  
**Timestamp:** 2025-01-26 10:30:16

---

[AI Response Content Here]

---
```

### ⚙️ CLI Advanced Features

#### File Validation
```bash
# CLI validates files at startup
$ python prompt_runner.py -p missing.json -i document.md
ERROR: Prompt file not found: missing.json

$ python prompt_runner.py -p analysis.json -i missing.md
ERROR: Input file not found: missing.md
```

#### Configuration Priority
1. **Command line options** (highest priority)
2. **Config file settings** (`-c config.yaml`)
3. **Default configuration**

#### Auto-Detection Features
- **File logging**: Automatically enabled when log file specified
- **Batch mode**: Triggered when both `-p` and `-i` provided
- **Directory creation**: Log and output directories created automatically

#### File Management Features
- **Unique payload files**: Each execution creates timestamped payload files (`prompt_runner_20250131_143052_12345.payload.json`)
- **Temporary directory support**: Use `--temp-dir` to organize all files in one location
- **Shared temp directories**: When used with prompt chains, all files stored in the same temp directory
- **File preservation**: Payload files preserved after execution for debugging and review

### 🚨 CLI Troubleshooting

#### Common Issues and Solutions

**1. API Key Not Found**
```bash
$ python prompt_runner.py -p test.json -i input.md
ERROR: API key not found

# Solution:
export OPENROUTER_API_KEY="your_key_here"
```

**2. Missing Dependencies**
```bash
$ python prompt_runner.py
ModuleNotFoundError: No module named 'yaml'

# Solution:
pip install pyyaml requests
```

**3. File Permission Errors**
```bash
$ python prompt_runner.py -p test.json -i input.md -l /restricted/log.log
ERROR: Failed to save payload

# Solution:
python prompt_runner.py -p test.json -i input.md -l ./log.log
```

**4. Invalid JSON Prompts**
```bash
$ python prompt_runner.py -p broken.json -i input.md
ERROR: Invalid JSON in prompt file broken.json

# Solution: Validate JSON format
python -m json.tool broken.json
```

---

## 🌐 Web Application Interface

### 🛠️ Web Setup

#### 1. Quick Start with Shell Script

The easiest way to run the Flask web application:

```bash
# Make the launcher script executable
chmod +x prompt_runner_flask.sh

# Run initial setup (creates templates and config)
./prompt_runner_flask.sh --setup

# Start the web application
./prompt_runner_flask.sh

# Or start in production mode
./prompt_runner_flask.sh --production
```

#### 2. Flask Launcher Script Options

The `prompt_runner_flask.sh` script provides convenient management:

```bash
# Basic usage
./prompt_runner_flask.sh                      # Start with defaults (127.0.0.1:5000)
./prompt_runner_flask.sh -d                   # Debug mode
./prompt_runner_flask.sh -H 0.0.0.0 -p 8080   # Custom host and port

# Management commands
./prompt_runner_flask.sh --setup              # Create templates and config
./prompt_runner_flask.sh --check              # Verify dependencies
./prompt_runner_flask.sh --background         # Run as daemon
./prompt_runner_flask.sh --kill               # Stop background instances
./prompt_runner_flask.sh --logs               # View application logs

# Production deployment
./prompt_runner_flask.sh --production         # Production settings (0.0.0.0, no debug)
./prompt_runner_flask.sh --public             # Public access (0.0.0.0)
```

#### 3. Script Features

- **Dependency checking**: Validates Python, Flask, and required modules
- **Automatic setup**: Creates templates and configuration files
- **Process management**: Start, stop, and monitor background processes
- **Logging**: File and console logging with real-time viewing
- **Error handling**: Clear error messages and recovery suggestions

#### 4. Manual Flask Setup

If you prefer to run Flask directly:

#### 4. Manual Flask Setup

If you prefer to run Flask directly:

#### Additional Required Files for Web Interface
```
project/
├── prompt_runner_flask.py              # Flask web application
├── create_templates.py                 # Template setup script
├── flask_config.yaml                   # Web app configuration
├── prompts_registry.yaml               # Prompt registry
├── templates/                          # HTML templates directory
│   ├── base.html                      # Base template
│   ├── index.html                     # Main page
│   ├── config.html                    # Configuration page
│   ├── prompts_registry.html          # Registry management
│   ├── prompt_form.html              # Prompt execution form
│   └── history.html                  # Session history
└── [CLI files from above]             # All CLI files also needed
```

#### Manual Web Application Setup
```bash
# Install additional web dependencies
pip install flask

# Create templates and configuration
python create_templates.py

# Set API key
export OPENROUTER_API_KEY="your_api_key_here"

# Start web application
python prompt_runner_flask.py
```

#### Access Web Interface
Navigate to: `http://localhost:5000`

---

## ⛓️ Prompt Chain Runner

The **Prompt Chain Runner** (`prompt_chain_runner.py`) enables advanced automation workflows by executing multiple prompts in sequence. Perfect for complex document processing pipelines that require multiple AI processing steps.

### 🚀 New Enhanced Features

#### Multi-File Processing
Process multiple files through the same prompt chain:
```bash
# Process 3 files through the same 3-step prompt chain
python prompt_chain_runner.py -c multi_file_config.yaml
```

**Configuration Example:**
```yaml
input_files:
  - "document1.md"
  - "document2.md" 
  - "document3.txt"
output_pattern: "processed_{input_name}_final{input_ext}"
prompts:
  prompt 1: "analysis.json"
  prompt 2: "refinement.json"
  prompt 3: "polish.json"
```

#### Per-Prompt Configuration (Different LLMs)
Use different AI models optimized for each step:
```bash
# Use Claude for creative tasks, GPT-4 for technical analysis
python prompt_chain_runner.py -c multi_llm_config.yaml
```

**Configuration Example:**
```yaml
input_file: "document.md"
output_file: "processed_document.md"
prompts:
  prompt 1:
    prompt_file: "creative_brainstorm.json"
    config_file: "claude_config.yaml"      # Claude for creativity
  prompt 2:
    prompt_file: "technical_analysis.json"
    config_file: "gpt4_config.yaml"       # GPT-4 for technical work
  prompt 3:
    prompt_file: "final_polish.json"
    config_file: "deepseek_config.yaml"   # DeepSeek for final review
```

### 📊 Execution Workflows

**Single File Processing:**
```
input.md → Analysis → Refinement → Polish → output.md
```

**Multi-File Processing:**
```
doc1.md → Analysis → Refinement → Polish → processed_doc1_final.md
doc2.md → Analysis → Refinement → Polish → processed_doc2_final.md  
doc3.txt → Analysis → Refinement → Polish → processed_doc3_final.txt
```

### 🗂️ Advanced File Organization

All execution artifacts are preserved in organized temp directories:
```
temp/input_document_20250131_143052_12345/
├── input_document_20250131_143052_12345.log           # Execution log
├── original_input_document.md                         # Original input
├── file01_step01_analysis.tmp                         # Intermediate files
├── file01_step02_refinement.tmp
├── prompt_runner_20250131_143053_12346.payload.json   # API payloads
├── prompt_runner_20250131_143054_12347.payload.json
└── processed_document_final.md                        # Final output copy
```

### 🛠️ Quick Start

**1. Create Configuration:**
```bash
# Generate sample config
python prompt_chain_runner.py --create-sample
```

**2. Run Single File Chain:**
```bash
python prompt_chain_runner.py -c my_chain.yaml
```

**3. Run Multi-File Processing:**
```bash
python prompt_chain_runner.py -c multi_file_config.yaml
```

**4. Debug with Verbose Logging:**
```bash
python prompt_chain_runner.py -c config.yaml --debug
```

### 📖 Full Documentation
For complete details, see [prompt_chain_readme.md](prompt_chain_readme.md)

---

## 🤖 Supported AI Models

This application works with 400+ AI models through OpenRouter.ai, including the most popular LLMs:

### Top 12 Most Used Models:
1. **OpenAI**
   - GPT-4o: `openai/gpt-4o-2024-11-20`
   - GPT-4.5: `openai/gpt-4.5-preview`
   - o3-mini: `openai/o3-mini`

2. **Claude (Anthropic)**
   - Claude 4 Sonnet: `anthropic/claude-4-sonnet-20250522`
   - Claude 3.7 Sonnet: `anthropic/claude-3.7-sonnet`
   - Claude 3.5 Sonnet: `anthropic/claude-3.5-sonnet:beta`

3. **Gemini (Google)**
   - Gemini 2.5 Pro: `google/gemini-2.5-pro-exp-03-25`
   - Gemini 2.0 Flash: `google/gemini-2.0-flash-experimental`
   - Gemini Pro: `google/gemini-pro-1.5-latest`

4. **DeepSeek**
   - DeepSeek R1: `deepseek/deepseek-r1`
   - DeepSeek V3: `deepseek/deepseek-chat-v3-0324`
   - DeepSeek Coder: `deepseek/deepseek-coder`

5. **Llama (Meta)**
   - Llama 4 Maverick: `meta-llama/llama-4-maverick`
   - Llama 3.3 70B: `meta-llama/llama-3.3-70b-instruct`
   - Llama 3.1 Nemotron: `nvidia/llama-3.1-nemotron-70b-instruct`

6. **Grok (xAI)**
   - Grok Beta: `x-ai/grok-beta`
   - Grok 2: `x-ai/grok-2-1212`

7. **Qwen (Alibaba)**
   - Qwen 3: `qwen/qwen-3-turbo`
   - Qwen 2.5 Coder: `qwen/qwen-2.5-coder-32b-instruct`
   - QwQ: `qwen/qwq-32b-preview`

8. **Mistral**
   - Mistral Large: `mistralai/mistral-large-2411`
   - Mistral Small: `mistralai/mistral-small-3.1-24b-instruct`
   - Pixtral: `mistralai/pixtral-12b-2409`

9. **Cohere**
   - Command R+: `cohere/command-r-plus`
   - Command R7B: `cohere/command-r7b-12-2024`
   - Command R: `cohere/command-r`

10. **Amazon Nova**
    - Nova Pro: `amazon/nova-pro-v1`
    - Nova Lite: `amazon/nova-lite-v1`
    - Nova Micro: `amazon/nova-micro-v1`

11. **Dolphin (Cognitive Computations)**
    - Dolphin Mixtral 8x7B: `cognitivecomputations/dolphin-mixtral-8x7b`
    - Dolphin Mixtral 8x22B: `cognitivecomputations/dolphin-mixtral-8x22b`
    - Dolphin 2.6 Mixtral: `cognitivecomputations/dolphin-2.6-mixtral-8x7b`

12. **Venice.ai Models** (via direct API or OpenRouter)
    - Venice Large (Qwen3): Use Venice.ai API directly
    - Venice Medium: Use Venice.ai API directly  
    - Venice Small: Use Venice.ai API directly
    - *Note: Venice.ai has its own API separate from OpenRouter*
    - *Website: https://venice.ai*
    - *API URL: https://api.venice.ai/api/v1*

### Free Models Available:
Many models offer free tiers with rate limits. Add `:free` suffix to model names:
- `deepseek/deepseek-chat:free`
- `meta-llama/llama-4-maverick:free`
- `google/gemini-2.5-pro-exp-03-25:free`
- `mistralai/mistral-small-3.1-24b-instruct:free`
- `cognitivecomputations/dolphin-mixtral-8x7b:free`

### Using Venice.ai Models:
Venice.ai provides private, uncensored AI models through their own API. To use Venice models:

1. **Direct Venice API**: Set up a Venice.ai account and use their API directly
2. **Model Configuration**: Update `api_base_url` to `https://api.venice.ai/api/v1`
3. **Available Models**: `llama-3.3-70b`, `deepseek-r1-llama-70b`, `qwen32b`, `dolphin-2.9.2-qwen2`

*Note: Venice.ai requires separate API credentials and is not part of OpenRouter*

### Model Selection:
Configure your preferred model in the configuration file or web interface:

**CLI Configuration (`openrouter_editor.yaml`):**
```yaml
model: anthropic/claude-4-sonnet-20250522  # Default model
temperature: 0.8
max_tokens: 25000
```

**Web Configuration (`flask_config.yaml`):**
```yaml
model: anthropic/claude-4-sonnet-20250522  # Default model
temperature: 0.8
max_tokens: 10000
```

## 🚀 Features

### CLI Features
- **Batch Processing**: Automated file processing for CI/CD pipelines
- **Interactive Mode**: Browse and select files with guided prompts
- **Configuration Management**: YAML config files with command-line overrides
- **Flexible Logging**: Console and file logging with multiple levels
- **File Validation**: Comprehensive input validation and error handling
- **Session Persistence**: Append logging for batch processing workflows

### Web Features
- **Modern Interface**: Clean, responsive design with mobile support
- **Session History**: Track all responses with download capability
- **Configuration UI**: Web-based settings management
- **File Uploads**: Support for text input and file uploads
- **Live Updates**: Real-time processing with AJAX
- **Prompts Registry**: Web-based prompt management

## 🎯 Choosing the Right Interface

### Use Flask Launcher When:
- **Quick setup**: Need to get started fast with minimal configuration
- **Development**: Testing and debugging with built-in process management
- **Production deployment**: Running on servers with monitoring needs
- **Process management**: Need to start/stop/monitor the application
- **Logging**: Want centralized log management and viewing

### Use Direct Flask When:
- **Automation**: Integrating with scripts, CI/CD, or batch processing
- **Performance**: Processing many files efficiently
- **Scripting**: Building automated workflows
- **Headless**: Running on servers without GUI
- **Version Control**: Configuration files can be tracked in git

### Use Web Interface When:
- **Interactive Use**: Exploring prompts and experimenting
- **Team Collaboration**: Sharing access with multiple users
- **File Uploads**: Processing files through web interface
- **Visual Feedback**: Need immediate visual feedback
- **Session Management**: Tracking history within sessions

## 🔒 Security Considerations

- **API Key Protection**: Store your OpenRouter API key as an environment variable
- **File Upload Limits**: Configure appropriate upload size limits (web interface)
- **Input Validation**: All inputs are validated before processing
- **File Permissions**: Ensure proper read/write permissions for config and log files
- **Session Management**: Web sessions are memory-based and cleared on restart

## 🛠️ Development

### Custom JSON Prompts
Create custom prompts in JSON format:
```json
{
  "instruction": "Analyze the following text for sentiment",
  "type": "analysis",
  "requirements": [
    "Identify overall sentiment (positive/negative/neutral)",
    "Highlight key emotional indicators",
    "Provide confidence score"
  ],
  "output_format": "structured analysis with clear sections"
}
```

### Adding New Features

1. **CLI Features**: Modify `prompt_runner.py` and related modules
2. **Web Features**: Add routes to `prompt_runner_flask.py` and create templates
3. **Configuration**: Add new settings to config management system
4. **API Integration**: Extend API client for new functionality

### Dependencies

**Core Requirements:**
- `requests` - HTTP client for API calls
- `pyyaml` - YAML configuration handling
- `pathlib` - File path handling (built-in)
- `json` - JSON processing (built-in)
- `logging` - Logging system (built-in)

**Web Interface Additional:**
- `flask` - Web framework for GUI

## 📈 Monitoring and Logging

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages  
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

### CLI Logging Options
```bash
# Console logging (default)
python prompt_runner.py -p test.json -i input.md

# File logging
python prompt_runner.py -p test.json -i input.md -l debug.log

# Verbose console logging
python prompt_runner.py -p test.json -i input.md -v

# Quiet mode (errors only)
python prompt_runner.py -p test.json -i input.md -q
```

## 🚨 Troubleshooting

### CLI Issues
1. **Missing Files**: Ensure all required Python modules are present
2. **API Key**: Set `OPENROUTER_API_KEY` environment variable
3. **Dependencies**: Install required packages with `pip install requests pyyaml`
4. **Permissions**: Check file read/write permissions
5. **JSON Format**: Validate prompt files with `python -m json.tool file.json`

### Web Interface Issues
1. **Templates Missing**: Run `python create_templates.py`
2. **Config Missing**: Check `flask_config.yaml` exists
3. **Port Conflicts**: Flask runs on port 5000 by default
4. **File Uploads**: Check upload size limits in configuration

### Common Solutions
```bash
# Reinstall dependencies
pip install --upgrade requests pyyaml flask

# Check file permissions
ls -la *.py *.yaml *.json

# Validate JSON prompts
for file in *.json; do python -m json.tool "$file" >/dev/null && echo "$file: OK" || echo "$file: ERROR"; done

# Test API key
echo $OPENROUTER_API_KEY
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Update documentation for new features
5. Test both CLI and web interfaces
6. Submit a pull request

## 📄 License

This project is provided as-is for educational and development purposes. Please ensure compliance with OpenRouter's terms of service when using their API.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review configuration files and logs
3. Verify API key and network connectivity
4. Test with simple prompts first
5. Check file permissions and dependencies

---

**Happy Prompting with CLI and Web!** 🎉