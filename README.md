# OpenRouter Interface

A comprehensive Python toolkit for working with AI language models through the OpenRouter API. Supports **single prompt processing**, **multi-prompt chaining**, **web interface**, and **advanced automation** with pre/post processing scripts.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenRouter API](https://img.shields.io/badge/API-OpenRouter-green.svg)](https://openrouter.ai/)

## ✨ Key Features

- 🚀 **Multiple Interfaces**: CLI, Web UI, and programmatic access
- 🔗 **Prompt Chaining**: Sequential prompt execution with intermediate file management
- 🤖 **100+ AI Models**: Support for all OpenRouter-compatible models
- 📝 **Script Integration**: Pre/post processing scripts at global and per-step levels
- ⚙️ **Advanced Configuration**: YAML-based configuration with parameter overrides
- 📁 **File Management**: Automatic chunking, validation, and format handling
- 🌐 **Web Dashboard**: Real-time monitoring and visual chain builder
- 📤 **Direct File Loading**: Upload and execute JSON prompts and YAML chains instantly
- 🎯 **No-Registry Execution**: Run prompts and chains without permanent storage

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Global Installation](#global-installation-recommended)
  - [Local Development](#local-development)
  - [Platform-Specific Setup](#platform-specific-setup)
- [Usage](#-usage)
  - [Single Prompts](#single-prompts)
  - [Web Interface](#web-interface)
  - [Prompt Chaining](#prompt-chaining)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Support](#-support)

## 🚀 Quick Start

### 5-Minute Setup

```bash
# 1. Clone and install
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface
./install-global.sh

# 2. Set up API key
export OPENROUTER_API_KEY="your-api-key-here"

# 3. Run a single prompt
openrouter-runner -p prompts/example.json -i input.md -o output.md

# 4. Create and run a chain
openrouter-chain --create-sample
openrouter-chain -c sample_chain.yaml

# 5. Start web interface
openrouter-web
```

## 📦 Installation

### Global Installation (Recommended)

Install system-wide for use from anywhere:

```bash
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface
./install-global.sh

# Verify installation
openrouter-runner --help
openrouter-web --help
openrouter-chain --help
```

### Local Development

For development or isolated environments:

```bash
./install.sh web
source openrouter-venv/bin/activate
PYTHONPATH=src python3 -m openrouter_interface.cli --help
```

### Platform-Specific Setup

<details>
<summary><strong>🐧 Linux</strong></summary>

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip git

# Clone and install
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface
./install-global.sh

# Set API key
echo 'export OPENROUTER_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```
</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

```bash
# Using Homebrew
brew install python git

# Clone and install
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface
./install-global.sh

# Set API key
echo 'export OPENROUTER_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```
</details>

<details>
<summary><strong>🪟 Windows</strong></summary>

```cmd
# Install Python 3.8+ and Git
# Clone repository
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface

# Run PowerShell as administrator
powershell -ExecutionPolicy Bypass -File install-windows.ps1

# Set API key
setx OPENROUTER_API_KEY "your-api-key-here"
```
</details>

### API Key Setup

Get your API key from [OpenRouter](https://openrouter.ai/) and set it up:

```bash
# Method 1: Environment variable
export OPENROUTER_API_KEY="your-api-key-here"

# Method 2: Setup script
./setup-api-key.sh

# Method 3: Add to shell profile
echo 'export OPENROUTER_API_KEY="your-api-key-here"' >> ~/.bashrc
```

## 🎯 Usage

### Single Prompts

Execute individual prompts against AI models:

```bash
# Basic usage
openrouter-runner -p prompts/analysis.json -i document.md -o result.md

# With model and parameter overrides
openrouter-runner -p prompts/creative.json -i input.md -o output.md \
  --model "openai/gpt-4-turbo" \
  --temperature 0.8 \
  --max-tokens 25000

# Multiple prompts in sequence
openrouter-runner -p "prompts/grammar.json,prompts/style.json" \
  -i draft.md -o final.md
```

### Web Interface

Launch the web dashboard for visual prompt management:

```bash
# Start with default settings
openrouter-web

# Custom port and debug mode
openrouter-web --port 8080 --debug

# With custom configuration
openrouter-web --config config/web_config.yaml
```

**Web Features:**
- 📤 **File Upload**: Drag-and-drop interface
- ⚙️ **Model Selection**: Choose from 100+ models
- 🔗 **Chain Builder**: Visual chain creation
- 📊 **Real-time Monitoring**: Live progress tracking
- 📁 **File Management**: Browse intermediate results
- 🎯 **Load Prompt**: Upload and execute JSON prompts instantly
- 🔗 **Load Chain**: Upload and execute YAML chains directly

#### Load Prompt Button
Access from the main page with the green "Load Prompt" button:

1. **Upload JSON Prompt**: Select any JSON prompt file
2. **Preview**: View prompt details (title, description, instructions, examples)
3. **Configure**: Optionally upload YAML configuration for API parameters
4. **Input**: Provide text or upload file
5. **Execute**: Run immediately and view results in modal

```bash
# Example usage flow:
# 1. Click "Load Prompt" on main page
# 2. Upload: test_load_prompt.json
# 3. Configure: test_single_prompt_config.yaml (optional)
# 4. Input: "This is test content to analyze"
# 5. Execute and view results
```

#### Load Chain Button
Access from the Chain Runner page next to "New Chain":

1. **Upload YAML Configuration**: Select any chain configuration file
2. **Preview**: View configuration summary and raw YAML
3. **Input**: Provide text or upload file
4. **Execute**: Start chain and monitor in real-time

```bash
# Example usage flow:
# 1. Click "Load Chain" on /chains page
# 2. Upload: test_web_yaml_config.yaml
# 3. Input: "Content to process through chain"
# 4. Execute and monitor progress below
```

### Prompt Chaining

Chain multiple prompts for complex workflows:

```bash
# Create sample configuration
openrouter-chain --create-sample

# Run a chain
openrouter-chain -c chain_config.yaml

# With debug output
openrouter-chain -c chain_config.yaml --debug
```

**Basic Chain Configuration:**
```yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

input_file: document.md
output_file: processed_document.md

prompts:
  prompt 1:
    name: "grammar_check"
    prompt_file: "prompts/grammar.json"
    temperature: 0.2

  prompt 2:
    name: "style_improvement"
    prompt_file: "prompts/style.json"
    temperature: 0.8
```

## ⚙️ Configuration

### Model Support

Supports 100+ models through OpenRouter:

- **Anthropic**: Claude 4, Claude 3.5 Sonnet, Claude Haiku
- **OpenAI**: GPT-4 Turbo, GPT-4o, GPT-3.5 Turbo
- **Google**: Gemini 2.0 Flash, Gemini 1.5 Pro
- **Specialized**: DeepSeek Coder, Llama models
- **And many more...**

### Advanced Features

#### Pre/Post Processing Scripts

Execute custom scripts before and after processing:

```yaml
# Global scripts (run once per chain)
preprocessing:
  script01: echo "Starting processing pipeline"
  name01: "Initialize Pipeline"
  script02: python3 scripts/validate_input.py
  name02: "Validate Input"

postprocessing:
  script01: python3 scripts/generate_report.py
  name01: "Generate Report"

# Per-step scripts (run for each prompt)
prompts:
  prompt 1:
    prescript: "touch {input_file}.backup"
    name: "content_processing"
    prompt_file: "prompts/process.json"
    postscript: "wc -l {output_file} > {output_file}.stats"
```

#### Multi-Pass Processing

Run prompts multiple times with iterative improvement:

```yaml
prompts:
  prompt 1:
    name: "iterative_improvement"
    prompt_file: "prompts/improve.json"
    passes: 3  # Run 3 times
    append: yes  # Accumulate content
```

#### File Management

- **Automatic Chunking**: Handle large files automatically
- **Intermediate Files**: All step outputs preserved
- **Size Validation**: Detect processing issues
- **Format Support**: Markdown, text, JSON, YAML

## 📚 Examples

### Content Enhancement Pipeline

```yaml
# content_enhancement.yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

input_file: blog_draft.md
output_file: enhanced_blog.md

prompts:
  prompt 1:
    name: "grammar_foundation"
    prompt_file: "prompts/grammar.json"
    temperature: 0.2

  prompt 2:
    name: "engagement_boost"
    prompt_file: "prompts/engagement.json"
    temperature: 0.8

  prompt 3:
    name: "seo_optimization"
    prompt_file: "prompts/seo.json"
    temperature: 0.6
```

### Technical Documentation

```yaml
# technical_docs.yaml
global_config:
  model: "deepseek/deepseek-coder"
  temperature: 0.3

preprocessing:
  script01: python3 scripts/extract_code.py
  name01: "Extract Code Blocks"

prompts:
  prompt 1:
    prescript: "python3 scripts/validate_syntax.py {input_file}"
    name: "code_documentation"
    prompt_file: "prompts/document_code.json"
    postscript: "python3 scripts/test_examples.py {output_file}"

postprocessing:
  script01: python3 scripts/generate_toc.py
  name01: "Generate Table of Contents"
```

### Multi-File Processing

```yaml
# multi_file_processing.yaml
input_files:
  - chapter1.md
  - chapter2.md
  - chapter3.md
output_pattern: "processed_{input_name}.md"

prompts:
  prompt 1:
    prescript: "echo 'Processing {input_file}' >> progress.log"
    name: "content_enhancement"
    prompt_file: "prompts/enhance.json"
    postscript: "wc -w {output_file} >> word_counts.log"
```

### Web Interface Load Examples

#### Load Prompt Example

```json
// test_load_prompt.json
{
  "title": "Content Quality Analysis",
  "description": "Analyze content for clarity, coherence, and quality",
  "persona": "You are a professional content analyst who provides clear, actionable feedback.",
  "instructions": "Analyze the provided content for clarity, coherence, and overall quality. Provide specific recommendations for improvement.",
  "review_criteria": "Evaluate based on: 1) Clarity of message, 2) Logical structure, 3) Grammar and style, 4) Overall effectiveness",
  "output_format": "Provide a structured analysis with specific examples and recommendations."
}
```

**Web Usage:**
1. Click "Load Prompt" on main page
2. Upload `test_load_prompt.json`
3. Optionally upload `test_single_prompt_config.yaml` for custom API settings
4. Enter content: "This is my draft article about AI development..."
5. Execute and view results instantly

#### Load Chain Example

```yaml
# test_web_yaml_config.yaml
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7
  max_tokens: 20000

input_file: test_input.md
output_file: test_web_output.md

preprocessing:
  script01: echo "Starting web-loaded chain"
  name01: "Initialize Chain"

prompts:
  prompt 1:
    name: "test_analysis"
    prompt_file: "prompts/content_quality.json"
    temperature: 0.3

  prompt 2:
    name: "final_polish"
    prompt_file: "prompts/content_quality.json"
    temperature: 0.8
    append: yes

postprocessing:
  script01: echo "Web chain complete"
  name01: "Finalize Chain"
```

**Web Usage:**
1. Navigate to `/chains` page
2. Click "Load Chain" button
3. Upload `test_web_yaml_config.yaml`
4. Preview shows: 2 prompts, preprocessing/postprocessing scripts, append mode
5. Enter content and start execution
6. Monitor real-time progress in active chains section

## 📖 Documentation

### Quick References

- **[Complete Documentation](docs/)** - Full guides and API reference
- **[Configuration Guide](docs/configuration.md)** - YAML configuration options
- **[Prompt Templates](docs/templates.md)** - Creating reusable prompts
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

### Common Commands

```bash
# Help and information
openrouter-runner --help
openrouter-chain --help
openrouter-web --help

# Debug and validation
openrouter-chain -c config.yaml --debug
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"

# Model and API testing
openrouter-runner -p prompts/test.json -i test.md -o test_output.md
```

## 🛠️ Development

### Project Structure

```
openrouter-interface/
├── src/openrouter_interface/     # Main Python package
│   ├── cli.py                    # CLI interface
│   ├── web.py                    # Web interface
│   ├── chain.py                  # Chain runner
│   ├── prompt_runner.py          # Core processing engine
│   └── prompt_chain_runner.py    # Chain execution logic
├── config/                       # Configuration files
├── prompts/                      # Prompt templates
├── scripts/                      # Utility scripts
├── tests/                        # Test suite
└── docs/                         # Documentation
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=openrouter_interface

# Run specific test files
pytest tests/test_cli.py
pytest tests/test_chain.py
```

### Code Quality

```bash
# Format code
black src tests

# Type checking
mypy src

# Linting
flake8 src
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Quick Contribution Guide

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with tests and documentation
4. **Run tests**: `pytest && black src tests && flake8 src`
5. **Submit a pull request**

### Areas for Contribution

- 🎯 **New Features**: Prompt templates, chain configurations
- 🤖 **Model Support**: Additional model integrations
- 📚 **Documentation**: Tutorials, examples, guides
- 🧪 **Testing**: Test coverage improvements
- ⚡ **Performance**: Optimization and profiling
- 🎨 **UI/UX**: Web interface improvements

### Development Setup

```bash
# Clone and install for development
git clone https://github.com/your-org/openrouter-interface.git
cd openrouter-interface
./install.sh dev

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run development server
PYTHONPATH=src python3 -m openrouter_interface.web --debug
```

## 🆘 Support

### Getting Help

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-org/openrouter-interface/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/openrouter-interface/discussions)
- 📖 **Documentation**: [Complete Docs](docs/)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/your-org/openrouter-interface/issues)

### Community

- 💬 **Discord**: Join our community chat
- 🐦 **Twitter**: Follow for updates and tips
- 📝 **Blog**: Technical articles and tutorials

### Troubleshooting

**Common Issues:**

```bash
# API key not set
echo $OPENROUTER_API_KEY

# Permission issues
chmod +x install-global.sh

# Python path issues
which python3
python3 --version
```

**Debug Mode:**
```bash
# Enable detailed logging
openrouter-chain -c config.yaml --debug 2>&1 | tee debug.log

# Check configuration validity
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai/) for providing access to multiple AI models
- The Python community for excellent tools and libraries
- Contributors who help improve this project

---

## 📊 Project Status

- ✅ **Stable**: Core functionality tested and reliable
- 🚀 **Active Development**: Regular updates and new features
- 🧪 **Well Tested**: Comprehensive test suite
- 📚 **Documented**: Complete documentation and examples

### Recent Updates

- ✨ **Per-Phase Scripts**: Individual prescript/postscript for each step
- 🔗 **Variable Substitution**: Dynamic {input_file}/{output_file} replacement
- 📊 **Enhanced Monitoring**: Improved web interface with real-time progress
- 🎯 **Model Compatibility**: Automatic parameter filtering per model
- 📁 **File Management**: Advanced validation and size checking
- 📤 **Load Buttons**: Direct upload and execution of JSON prompts and YAML chains
- 🚀 **No-Registry Execution**: Run files instantly without permanent storage

---

**Ready to get started?** Follow the [Quick Start](#-quick-start) guide above! 🚀