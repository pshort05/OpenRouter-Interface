# OpenRouter Interface
---
A comprehensive Python toolkit for working with AI language models through the OpenRouter API. Supports **single prompt processing**, **multi-prompt chaining**, **file conversion** (docx/pdf/epub), **web interface**, and **advanced automation** with pre/post processing scripts.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenRouter API](https://img.shields.io/badge/API-OpenRouter-green.svg)](https://openrouter.ai/)

---
## ✨ Key Features
---

- 🚀 **Multiple Interfaces**: CLI, Web UI, and programmatic access
- 🔗 **Prompt Chaining**: Sequential prompt execution with restart/recovery capabilities
- 🔄 **Smart Recovery**: Automatic restart from failed steps with status tracking
- 🤖 **100+ AI Models**: Support for all OpenRouter-compatible models
- 📝 **Script Integration**: Pre/post processing scripts at global and per-step levels
- 🔀 **File Conversion**: Convert between markdown and docx, pdf, epub, and more
- 📑 **Combine Outputs**: Merge all step outputs into a single file
- ✂️ **Chapter Splitter**: Split markdown documents by chapter headings
- ⚙️ **Advanced Configuration**: YAML-based configuration with parameter overrides
- 📁 **File Management**: Automatic chunking, validation, and format handling
- 🌐 **Web Dashboard**: Real-time monitoring and visual chain builder
- 📤 **Direct File Loading**: Upload and execute JSON prompts and YAML chains instantly
- 🎯 **No-Registry Execution**: Run prompts and chains without permanent storage

---
## 📖 Table of Contents
---

- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Global Installation](#global-installation-recommended)
  - [Local Development](#local-development)
  - [Platform-Specific Setup](#platform-specific-setup)
- [Usage](#-usage)
  - [Single Prompts](#single-prompts)
  - [Web Interface](#web-interface)
  - [Prompt Chaining](#prompt-chaining)
  - [Chapter Splitter](#chapter-splitter)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Support](#-support)

---
## 🚀 Quick Start
---

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

# 5. Split a document by chapters
split-chapters book.md -o chapters/

# 6. Start web interface
openrouter-web
```

---
## 📦 Installation
---

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
split-chapters --help
```

**Note:** The installer automatically detects and installs `pandoc` for file conversion features. If automatic installation fails, install manually from [pandoc.org](https://pandoc.org/installing.html).

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

---
## 🎯 Usage
---

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

#### Load Chain Configuration (Expanded)
Access from the Chain Runner page - navigates to dedicated full-page interface:

**🎯 Dedicated Load Page (`/chains/load`)**
1. **Navigate**: Click "Load Chain" to go to comprehensive load interface
2. **Upload Options**:
   - File upload with drag-and-drop support
   - Text area for direct YAML input
   - Configuration-based upload with template selection
3. **Rich Configuration Analysis**:
   - Detailed breakdown showing prompts, models, and parameters
   - Raw YAML preview with syntax highlighting
   - Template usage detection and description
4. **Advanced Execution Options**:
   - Multiple input methods (text input, file upload, config-specified)
   - Custom output filename overrides
   - Debug mode toggle for detailed logging
   - Validation checks before execution
5. **Template Management**: Access to pre-built configuration templates
6. **Direct Execution**: Start chains immediately from the load interface

**🎨 YAML Editor Integration (`/chains/yaml-editor`)**
- Professional code editor with full YAML syntax highlighting
- Five built-in templates: Basic, Advanced, Scripts, Multi-pass, Append
- Real-time validation with error detection and reporting
- Auto-save functionality and keyboard shortcuts (Ctrl+S, Ctrl+Shift+F)
- Light and dark themes for comfortable editing
- Direct execution: Save & Execute for immediate chain deployment

**🔧 Enhanced Features**:
- **Configuration Validation**: Pre-execution YAML and config validation
- **Error Handling**: Comprehensive error reporting with specific line numbers
- **Template System**: Quick-start templates for common workflow patterns
- **Seamless Integration**: Edit, validate, and execute in unified interface

```bash
# Complete workflow example:
# 1. Click "Load Chain" on /chains page → Full-page load interface
# 2. Upload: complex_chain.yaml → Rich analysis shows 5 prompts, 3 models
# 3. Preview: Raw YAML with syntax highlighting, template detection
# 4. Configure: Custom input method, debug mode enabled
# 5. Validate: Check for YAML errors and missing files
# 6. Execute: Start chain with comprehensive monitoring
# 7. Edit: Jump to YAML editor for quick modifications
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

**🔄 Chain Restart & Recovery:**

OpenRouter Interface includes powerful restart functionality to recover from failures and save time/costs by avoiding re-execution of completed steps.

```bash
# Check execution status
openrouter-chain -c config.yaml --status-only

# Restart from failed steps automatically
openrouter-chain -c config.yaml --restart

# Force restart from specific step
openrouter-chain -c config.yaml --restart-from 4

# Clean status and start fresh
openrouter-chain -c config.yaml --clean-status
```

**Key Benefits:**
- ⏱️ **Time Savings**: Skip expensive LLM calls for completed steps
- 💰 **Cost Efficiency**: Avoid re-running successful operations
- 🔍 **Transparency**: `.status` files show exactly what completed/failed
- 🎯 **Flexible Recovery**: Auto-detect restart points or force restart from any step
- 📁 **Multi-file Support**: Independent restart points per input file

**Status File Example:**
```json
{
  "chain_config": "my_chain.yaml",
  "status": "failed",
  "files": {
    "chapter_21.md": {
      "status": "failed",
      "steps": {
        "1": {"status": "completed", "name": "grammar_check", "time": 136.3},
        "2": {"status": "completed", "name": "style_improvement", "time": 135.7},
        "3": {"status": "failed", "name": "final_polish", "error": "API timeout"}
      }
    }
  }
}
```

When restarted, the chain will:
1. 🔍 **Detect** the previous failure at step 3
2. ⏭️ **Skip** steps 1-2 (already completed)
3. 🔄 **Resume** from step 3 and continue to completion
4. 📊 **Track** all new progress in the status file

### Chapter Splitter

Split large markdown documents into separate files by chapter headings:

```bash
# Basic usage - splits in same directory as input
split-chapters book.md

# Specify output directory
split-chapters book.md -o chapters/

# Dry run (preview without creating files)
split-chapters book.md --dry-run

# Global command usage (after install-global.sh)
split-chapters --help
```

**Features:**
- ✂️ **Automatic Detection**: Identifies chapter headings at any level (# Chapter 1, ## Chapter 2, etc.)
- 📝 **Smart Naming**: Creates files as `chapter_1.md`, `chapter_2.md`, etc.
- 🎯 **Title Stripping**: Removes text after chapter number (e.g., "Chapter 1: The Beginning" → `chapter_1.md`)
- 🔄 **Duplicate Handling**: Adds A, B, C suffixes for duplicate chapter numbers
- 📄 **Preamble Support**: Saves content before first chapter to `preamble.md`
- 🔠 **Case Insensitive**: Detects "chapter", "Chapter", "CHAPTER", etc.

**Example Output:**
```
Processing: book.md
Found 15 chapters

Created files:
  preamble.md (342 lines)
  chapter_1.md (1,245 lines)
  chapter_2.md (1,089 lines)
  chapter_3.md (1,367 lines)
  ...
  chapter_15.md (1,156 lines)

Total: 16 files created in /path/to/chapters/
```

**Use Cases:**
- 📚 **Book Processing**: Split manuscripts for chapter-by-chapter editing
- 🔗 **Chain Preparation**: Prepare individual chapters for prompt chain processing
- 🔀 **Parallel Processing**: Enable concurrent processing of multiple chapters
- 📦 **Organization**: Structure large documents for better version control

**Integration with Chains:**
```bash
# 1. Split book into chapters
split-chapters manuscript.md -o chapters/

# 2. Process each chapter with a chain
for chapter in chapters/chapter_*.md; do
  openrouter-chain -c editing_chain.yaml --input "$chapter"
done

# 3. Combine results if needed
cat chapters/processed_*.md > final_manuscript.md
```

---
## ⚙️ Configuration
---

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

#### File Conversion

Convert between markdown and various document formats:

```yaml
# Convert input docx to markdown before processing
input_convert:
  enabled: true
  from_format: docx  # Auto-detects if not specified

# Convert final output to multiple formats
output_convert:
  enabled: true
  formats:
    - docx
    - pdf
    - epub

# Per-step conversion for specific outputs
prompts:
  prompt 2:
    convert_output:
      format: pdf
      filename: step2_report.pdf
```

**Supported Formats:**
- Input: docx, odt, rtf, html, epub, txt, pdf, latex, rst, org, mediawiki
- Output: docx, odt, rtf, html, epub, pdf, txt, latex, rst, org, mediawiki

**Requirements:**
- `pypandoc` Python package (auto-installed)
- `pandoc` system binary (auto-installed by install scripts)
- LaTeX for PDF generation (optional)

#### Combine Outputs

Merge all step outputs into a single file:

```yaml
# Enable combine feature
combine: true
combined_file_name: all_steps_combined.md

prompts:
  prompt 1:
    name: "analysis"
    prompt_file: "prompts/analyze.json"
  prompt 2:
    name: "enhancement"
    prompt_file: "prompts/enhance.json"
  prompt 3:
    name: "finalization"
    prompt_file: "prompts/finalize.json"

# Result: Creates markdown file with headers for each step
```

**Output Format:**
```markdown
# Combined Output - input_file.md
Generated: 2025-01-15 14:30:00
---
## Step 1: analysis
[output from step 1]
---
## Step 2: enhancement
[output from step 2]
---
## Step 3: finalization
[output from step 3]
---
```

#### File Management

- **Automatic Chunking**: Handle large files automatically
- **Intermediate Files**: All step outputs preserved
- **Size Validation**: Detect processing issues
- **Format Support**: Markdown, text, JSON, YAML

---
## 📚 Examples
---

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

### Document Conversion Pipeline

Process Word documents and export to multiple formats:

```yaml
# document_conversion.yaml
input_file: manuscript.docx
output_file: processed_manuscript.md

# Convert input Word doc to markdown
input_convert:
  enabled: true
  from_format: docx

# Convert final output to multiple formats
output_convert:
  enabled: true
  formats:
    - docx  # Microsoft Word
    - pdf   # PDF document
    - epub  # eBook format

# Combine all steps for reference
combine: true
combined_file_name: processing_history.md

global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

prompts:
  prompt 1:
    name: "grammar_check"
    prompt_file: "prompts/grammar.json"
    temperature: 0.3

  prompt 2:
    name: "style_improvement"
    prompt_file: "prompts/style.json"
    temperature: 0.7
    # Export this step as PDF report
    convert_output:
      format: pdf
      filename: style_report.pdf

  prompt 3:
    name: "final_polish"
    prompt_file: "prompts/polish.json"
    temperature: 0.5

# Result: Creates processed_manuscript.md, .docx, .pdf, .epub
#         Plus processing_history.md with all steps combined
#         Plus style_report.pdf from step 2
```

### Chapter-Based Book Processing

Process a book manuscript chapter by chapter:

```bash
# Step 1: Split manuscript into chapters
split-chapters manuscript.md -o manuscript_chapters/

# Step 2: Create a chapter processing chain
cat > chapter_editing.yaml << 'EOF'
global_config:
  model: "anthropic/claude-4-sonnet-20250522"
  temperature: 0.7

input_files:
  - manuscript_chapters/chapter_1.md
  - manuscript_chapters/chapter_2.md
  - manuscript_chapters/chapter_3.md
  # Add all chapters...

output_pattern: "edited_{input_name}.md"

prompts:
  prompt 1:
    name: "grammar_and_clarity"
    prompt_file: "prompts/grammar.json"
    temperature: 0.3

  prompt 2:
    name: "dialogue_enhancement"
    prompt_file: "prompts/dialogue.json"
    temperature: 0.7

  prompt 3:
    name: "pacing_review"
    prompt_file: "prompts/pacing.json"
    temperature: 0.6
    passes: 2
EOF

# Step 3: Process all chapters
openrouter-chain -c chapter_editing.yaml

# Step 4: Combine edited chapters
cat manuscript_chapters/edited_chapter_*.md > final_manuscript.md

# Optional: Convert to multiple formats
openrouter-chain -c convert_final.yaml
```

**With restart functionality:**
```bash
# If processing fails on chapter 5
openrouter-chain -c chapter_editing.yaml --restart

# Check status of all chapters
openrouter-chain -c chapter_editing.yaml --status-only

# Restart specific chapter from step 2
openrouter-chain -c chapter_editing.yaml --restart-from 2
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

---
## 📖 Documentation
---

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
split-chapters --help

# Chapter splitting
split-chapters book.md
split-chapters book.md -o chapters/
split-chapters book.md --dry-run

# Debug and validation
openrouter-chain -c config.yaml --debug
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"

# Model and API testing
openrouter-runner -p prompts/test.json -i test.md -o test_output.md
```

---
## 🛠️ Development
---

### Project Structure

```
openrouter-interface/
├── src/openrouter_interface/     # Main Python package
│   ├── cli.py                    # CLI interface
│   ├── web.py                    # Web interface
│   ├── chain.py                  # Chain runner
│   ├── prompt_runner.py          # Core processing engine
│   ├── prompt_chain_runner.py    # Chain execution logic
│   └── split_chapters.py         # Chapter splitter utility
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

---
## 🤝 Contributing
---

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

---
## 🆘 Support
---

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

---
## 📄 License
---

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
## 🙏 Acknowledgments
---

- [OpenRouter](https://openrouter.ai/) for providing access to multiple AI models
- The Python community for excellent tools and libraries
- Contributors who help improve this project

---
## 📊 Project Status
---

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
- 🎨 **Expanded Load Chain**: Full-page configuration interface with rich preview and validation
- ⚙️ **YAML Editor**: Professional code editor with templates, syntax highlighting, and real-time validation
- 🔧 **Enhanced Error Handling**: Comprehensive YAML parsing error detection and reporting
- ✂️ **Chapter Splitter**: Standalone utility to split markdown documents by chapter headings

---

**Ready to get started?** Follow the [Quick Start](#-quick-start) guide above! 🚀