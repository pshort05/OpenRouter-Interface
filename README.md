# OpenRouter Interface

A comprehensive Python package for executing JSON prompts using the OpenRouter API. Available as both a **command-line interface (CLI)** and a **Flask web application**. Follow Python best practices with proper package structure.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **🚀 New Easy Installation**: Just run `./install.sh web` after cloning - handles all permission issues automatically!

## ⚡ Quick Start

### 🚀 Super Easy Installation

```bash
# 1. Clone and install
git clone <repository-url>
cd openrouter-interface
./install.sh web

# 2. Set up API key  
./setup-api-key.sh

# 3. Start web interface
./start-web.sh
```

That's it! Three simple commands and you're running a full AI processing web interface.

### Manual Installation (Alternative)

```bash
# Use virtual environment manually
python3 -m venv openrouter-venv
source openrouter-venv/bin/activate
pip install -e ".[web]"     # Include web interface
pip install -e ".[dev]"     # Include development tools  
pip install -e ".[all]"     # Include everything
```

### First Run

```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY="your-api-key-here"

# Run CLI interface
openrouter-runner --help

# Run web interface with chain runner
openrouter-web
# Access at: http://localhost:5000
# Features: Single prompts, Chain runner, Progress tracking

# Run prompt chains (CLI)
openrouter-chain --help

# Book generation
bookgen --help
```

### Using as a Python Package

```python
from openrouter_interface import PromptRunner, ConfigManager

# Initialize
config = ConfigManager()
runner = PromptRunner()

# Process a prompt
success = runner.run_batch_mode("prompts/analysis.json", "input.md")
```

## 📁 Project Structure

This project follows Python best practices as outlined in the Hitchhiker's Guide to Python:

```
openrouter-interface/
├── src/
│   └── openrouter_interface/          # Main package
│       ├── __init__.py                # Package initialization
│       ├── cli.py                     # CLI entry point
│       ├── web.py                     # Web interface entry point
│       ├── chain.py                   # Chain runner entry point
│       ├── bookgen.py                 # BookGen entry point
│       ├── prompt_runner.py           # Core runner logic
│       ├── config_manager.py          # Configuration handling
│       ├── prompt_handler.py          # Prompt processing
│       ├── api_client.py              # OpenRouter API client
│       └── ...                        # Other modules
├── tests/                             # Test files
│   ├── __init__.py
│   ├── test_basic.py                  # Basic functionality tests
│   ├── unit/                          # Unit tests
│   └── integration/                   # Integration tests
├── docs/                              # Documentation
│   ├── README.md                      # Main documentation
│   ├── QUICK-START.md                 # Quick start guide
│   └── ...                            # Other documentation
├── prompts/                           # JSON prompt files
│   ├── creative_writing_assistant.json
│   ├── dialogue_editor.json
│   └── ...                            # 25+ included prompts
├── config/                            # Configuration files
│   ├── config.yaml                    # Default configuration
│   ├── flask_config.yaml             # Web app configuration
│   └── ...                            # Other configs
├── examples/                          # Usage examples
│   ├── basic_usage.py                 # Programming examples
│   └── sample_input.md               # Sample input file
├── scripts/                           # Installation/setup scripts
│   ├── install.sh                     # Installation script
│   └── dev-setup.sh                   # Development setup
├── pyproject.toml                     # Modern Python packaging
├── setup.py                           # Backward compatibility
├── requirements.txt                   # Core dependencies
└── MANIFEST.in                        # Package file inclusion
```

## 🚀 Features

### Core Capabilities
- **Multiple Interfaces**: CLI, Web, and programmatic Python API
- **400+ AI Models**: Support for Claude, GPT-4, Gemini, DeepSeek, Llama, and more
- **Prompt Management**: JSON-based prompt system with 25+ included prompts
- **Chain Processing**: Execute multiple prompts in sequence with web GUI
- **Book Generation**: Specialized tools for chapter writing and editing

### Advanced Features
- **Smart Text Chunking**: Handle large documents automatically
- **Flexible Configuration**: YAML config with command-line overrides
- **Comprehensive Logging**: Multiple log levels with file output
- **Session Management**: Web interface with history tracking
- **Real-time Progress Tracking**: Monitor long-running chain executions
- **Remote Chain Management**: Web-based control for server deployments
- **File Validation**: Input validation and error handling

## 📖 Documentation

### Quick References
- **[Quick Start Guide](docs/QUICK-START.md)** - Get running in 3 minutes
- **[Developer Guide](docs/CLAUDE.md)** - Architecture and development
- **[Setup Guide](docs/README_setup.md)** - Detailed installation

### Comprehensive Guides
- **[Setup Guide](docs/README_setup.md)** - Detailed installation
- **[Prompt Chain Runner](docs/prompt_chain_readme.md)** - Multi-step workflows
- **[BookGen Utilities](docs/README-BookGen.md)** - Book generation tools
- **[Developer Guide](docs/CLAUDE.md)** - Architecture and development

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd openrouter-interface

# Run development setup script
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
```

This creates a virtual environment, installs all dependencies, sets up pre-commit hooks, and configures development tools.

### Available Commands

```bash
# Testing
pytest                     # Run tests
pytest --cov              # Run with coverage
tox                        # Test across Python versions

# Code Quality
black src tests           # Format code
flake8 src                # Check style
mypy src                  # Type checking
pre-commit run --all      # Run all hooks

# Documentation
sphinx-build docs docs/_build/html  # Build docs
```

### Package Management

This project uses modern Python packaging:

- **pyproject.toml** - Primary configuration (PEP 518/621)
- **setup.py** - Backward compatibility  
- **MANIFEST.in** - File inclusion rules
- **requirements.txt** - Core dependencies

### Entry Points

Console commands are defined in `pyproject.toml`:

```toml
[project.scripts]
openrouter-runner = "openrouter_interface.cli:main"
openrouter-web = "openrouter_interface.web:main"
openrouter-chain = "openrouter_interface.chain:main"
bookgen = "openrouter_interface.bookgen:main"
```

## 🎯 Usage Examples

### Command Line Interface

```bash
# Interactive mode - browse and select files
openrouter-runner

# Batch processing
openrouter-runner -p prompts/analysis.json -i document.md -o results.md

# With custom configuration
openrouter-runner -c config/custom.yaml -p prompts/review.json -i code.py
```

### Web Interface

```bash
# Start web server
openrouter-web

# Access at http://localhost:5000
# Features available:
# - Single prompt processing
# - Prompt chain creation and monitoring
# - Real-time progress tracking
# - Session history management
# - Configuration management
```

#### Web Interface Features

**🔗 Prompt Chain Runner:**
- **Visual Chain Builder**: Drag-and-drop prompt sequencing
- **Upload Configurations**: Import existing YAML chain configs
- **Real-time Monitoring**: Live progress updates every 3 seconds
- **Remote Management**: Perfect for server deployments
- **Multi-step Workflows**: Connect multiple AI processing steps

**📊 Chain Management Dashboard:**
```
/chains                    # Chain overview and monitoring
/chains/create            # Visual chain creation interface  
/chains/status/<id>       # Real-time chain status
```

**🎯 Chain Creation Options:**
- **Configuration Upload**: Upload pre-built YAML files
- **Visual Builder**: Select prompts from library in sequence
- **Input Methods**: Text paste or file upload
- **Output Control**: Custom filenames and download

**⚡ Real-time Features:**
- **Progress Tracking**: Visual progress bars and percentages
- **Log Streaming**: Live execution logs in web interface
- **Status Updates**: Running, completed, failed, stopped states
- **Background Processing**: Non-blocking execution with status persistence

**🔧 Chain Operations:**
- **Start/Stop**: Full chain execution control
- **Monitor**: Real-time progress and log viewing
- **Download**: Retrieve completed results
- **Delete**: Clean up chains with file management

### Programmatic Usage

```python
from openrouter_interface import PromptRunner, PromptScanner

# Scan available prompts
scanner = PromptScanner()
prompts = scanner.scan_for_prompts()

# Process with specific prompt
runner = PromptRunner()
success = runner.run_batch_mode("prompts/editor.json", "draft.md")
```

### Prompt Chains

```bash
# Multi-step processing
openrouter-chain -c config/writing_chain.yaml -i manuscript.md

# Or use the web interface for visual chain management
# Navigate to http://localhost:5000/chains
```

## 🤖 Supported Models

Works with 400+ models through OpenRouter.ai:

- **Claude 4 Sonnet** (anthropic/claude-4-sonnet-20250522) - Default
- **GPT-4o** (openai/gpt-4o-2024-11-20)
- **Gemini 2.5 Pro** (google/gemini-2.5-pro-exp-03-25) 
- **DeepSeek R1** (deepseek/deepseek-r1)
- **Llama 4 Maverick** (meta-llama/llama-4-maverick)
- **Grok Beta** (x-ai/grok-beta)
- And many more...

## 🔧 Configuration

### Default Configuration (`config/config.yaml`)

```yaml
model: anthropic/claude-4-sonnet-20250522
api_base_url: https://openrouter.ai/api/v1
temperature: 0.8
max_tokens: 25000
log_level: INFO
```

### Environment Variables

```bash
export OPENROUTER_API_KEY="your-api-key"     # Required
export OPENROUTER_MODEL="preferred-model"    # Optional override
export OPENROUTER_LOG_LEVEL="DEBUG"          # Optional override
```

## 📦 Installation Options

### For Users

```bash
# Basic installation
pip install openrouter-interface

# With web interface
pip install "openrouter-interface[web]"

# From source
pip install -e .
```

### For Developers

```bash
# Development setup with all tools
./scripts/dev-setup.sh

# Or manual development install
pip install -e ".[dev]"
```

## 🌐 Remote Deployment & Web Chain Management

The web interface is perfect for remote server deployments, allowing team access to AI processing pipelines:

### Server Deployment

```bash
# Deploy on remote server
git clone <repository-url>
cd openrouter-interface
pip install -e ".[web]"

# Set API key on server
export OPENROUTER_API_KEY="your-api-key"

# Start web server (public access)
openrouter-web --host 0.0.0.0 --port 8080

# Or use production WSGI server
gunicorn -w 4 -b 0.0.0.0:8080 "openrouter_interface.web:create_app()"
```

### Remote Chain Management Benefits

**📱 Web-based Control:**
- No SSH or CLI access needed
- Cross-platform browser compatibility
- Mobile-friendly responsive design

**⏱️ Long-running Process Management:**
- Start chains and close browser
- Return later to check progress
- Background execution continues
- Email notifications (configurable)

**👥 Team Collaboration:**
- Multiple users can access same server
- Shared chain configurations
- Centralized processing power
- Collaborative prompt development

**📊 Monitoring & Analytics:**
- Real-time progress dashboards
- Execution history tracking
- Performance metrics
- Resource usage monitoring

### Chain Management Workflow

1. **Deploy** server with web interface
2. **Access** via browser from anywhere
3. **Create chains** using visual builder
4. **Upload configs** or build interactively
5. **Start execution** and monitor progress
6. **Return later** to check results
7. **Download outputs** when complete
8. **Share configurations** with team

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=openrouter_interface

# Specific test categories  
pytest tests/unit          # Unit tests only
pytest tests/integration   # Integration tests only

# Test across Python versions
tox

# Test web interface
pytest tests/web/          # Web interface tests
python -m pytest tests/chains/  # Chain runner tests
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure package is installed with `pip install -e .`
2. **API Key Missing**: Set `OPENROUTER_API_KEY` environment variable
3. **Command Not Found**: Package may not be in PATH, use `python -m openrouter_interface.cli`
4. **Permission Errors**: Use virtual environment or `--user` flag

### Getting Help

```bash
# Command help
openrouter-runner --help
openrouter-web --help

# Python help
python -c "import openrouter_interface; help(openrouter_interface)"

# Version info
python -c "import openrouter_interface; print(openrouter_interface.__version__)"
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Setup development environment: `./scripts/dev-setup.sh`
4. Make changes and add tests
5. Run quality checks: `pre-commit run --all`
6. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: Check `docs/` directory
- **Issues**: Report bugs and feature requests via GitHub issues
- **Examples**: See `examples/` directory for code samples
- **Configuration**: Reference files in `config/` directory

---

**Built with modern Python best practices** 🐍 **following the Hitchhiker's Guide to Python** 📖