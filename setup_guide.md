# Setup Guide - OpenRouter Prompt Runner Flask Application

This guide will walk you through setting up and running the OpenRouter Prompt Runner Flask application from start to finish.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.7 or higher** - [Download Python](https://python.org/downloads/)
- **pip** (Python package installer) - Usually comes with Python
- **OpenRouter API Key** - [Get one here](https://openrouter.ai/keys)
- **Git** (optional) - For cloning repositories

### System Requirements
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB free space
- **OS**: Windows, macOS, or Linux

## 🚀 Quick Start (5 Minutes)

### Step 1: Download the Application Files

Option A: **Download as ZIP**
1. Download all application files to a folder (e.g., `prompt-runner`)
2. Extract if needed

Option B: **Clone with Git**
```bash
git clone <repository-url>
cd prompt-runner
```

### Step 2: Install Dependencies

Open a terminal/command prompt in your project folder and run:

```bash
# Install required Python packages
pip install flask pyyaml requests
```

### Step 3: Set Your API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows (Command Prompt)
set OPENROUTER_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:OPENROUTER_API_KEY="your_api_key_here"

# macOS/Linux
export OPENROUTER_API_KEY="your_api_key_here"
```

**Option B: Add to Configuration File** (after setup)
1. Edit `flask_config.yaml`
2. Add line: `api_key: your_api_key_here`

### Step 4: Create Templates and Configuration

```bash
# Create all necessary files
python create_templates.py
```

This will:
- Create the `templates/` directory with all HTML files
- Generate `flask_config.yaml` with default settings
- Scan for JSON prompt files and create `prompts_registry.yaml`

### Step 5: Run the Application

```bash
# Start the Flask application
python prompt_runner_flask.py
```

### Step 6: Open in Browser

Navigate to: **http://localhost:5000**

🎉 **You're done!** The application should now be running.

## 📁 Project Structure

After setup, your project should look like this:

```
prompt-runner/
├── prompt_runner_flask.py          # Main Flask application
├── create_templates.py             # Setup script
├── flask_config.yaml              # Application configuration
├── prompts_registry.yaml          # Available prompts registry
├── templates/                      # HTML templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Main page
│   ├── config.html                # Configuration page
│   ├── prompts_registry.html      # Registry management
│   ├── prompt_form.html           # Prompt execution form
│   └── history.html               # Session history
├── *.json                         # Your JSON prompt files
└── README.md                      # Documentation
```

## 🔧 Detailed Setup Instructions

### Installing Python Dependencies

If you encounter issues with the quick installation:

```bash
# Create a virtual environment (recommended)
python -m venv prompt-runner-env

# Activate virtual environment
# Windows:
prompt-runner-env\Scripts\activate
# macOS/Linux:
source prompt-runner-env/bin/activate

# Install dependencies
pip install flask==3.0.0
pip install pyyaml==6.0.1
pip install requests==2.31.0
```

### Getting an OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Go to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-...`)

### Adding JSON Prompt Files

1. Create `.json` files in your project directory
2. Each file should contain a valid JSON prompt structure
3. Run `python create_templates.py` again to update the registry
4. Or use the web interface at `/prompts_registry` to rescan

Example prompt file (`example.json`):
```json
{
  "title": "Code Reviewer",
  "persona": "You are an expert code reviewer",
  "instructions": "Review the following code and provide feedback",
  "review_criteria": "Check for bugs, performance, and best practices"
}
```

## ⚙️ Configuration

### Application Configuration (`flask_config.yaml`)

```yaml
# API Settings
model: anthropic/claude-4-sonnet-20250522
api_base_url: https://openrouter.ai/api/v1
temperature: 0.8
max_tokens: 10000

# Application Settings
log_level: INFO
log_to_file: false
max_content_length_mb: 16
session_timeout_hours: 24
```

### Prompts Registry (`prompts_registry.yaml`)

```yaml
created: '2025-01-07 10:30:00'
prompts:
  - name: example.json
    path: ./example.json
    title: Example Prompt
    description: A sample prompt
    enabled: true
```

## 🌐 Web Interface Usage

### Main Pages

1. **Home** (`/`) - Browse and execute prompts
2. **Configuration** (`/config`) - Modify settings
3. **Prompts Registry** (`/prompts_registry`) - Manage prompt files
4. **History** (`/history`) - View session responses

### Managing Configuration

1. Navigate to `/config`
2. Modify any settings
3. Click "Save Configuration"
4. Changes apply immediately (no restart needed)

### Managing Prompts

1. Navigate to `/prompts_registry`
2. Click "Rescan Directory" to find new JSON files
3. Enable/disable prompts as needed
4. Edit titles and descriptions
5. Click "Save Registry"

### Executing Prompts

1. Go to home page (`/`)
2. Click "Use This Prompt" on any enabled prompt
3. Choose input method (text or file upload)
4. Enter your content
5. Click "Execute Prompt"

## 🔍 Troubleshooting

### Common Issues

**❌ "Templates not found" error**
```bash
# Solution: Run the setup script
python create_templates.py
```

**❌ "API key not found" error**
```bash
# Solution: Set your API key
export OPENROUTER_API_KEY="your_key_here"
```

**❌ "No prompts configured" message**
```bash
# Solution: Add JSON files and rescan
# 1. Add .json files to your directory
# 2. Go to /prompts_registry and click "Rescan Directory"
```

**❌ "Port already in use" error**
```bash
# Solution: Use a different port
python prompt_runner_flask.py --port 8080
```

**❌ Module import errors**
```bash
# Solution: Install missing dependencies
pip install flask pyyaml requests
```

### Checking Your Setup

Run these commands to verify your setup:

```bash
# Check Python version
python --version

# Check if packages are installed
python -c "import flask, yaml, requests; print('All packages installed')"

# Check if templates exist
ls templates/  # macOS/Linux
dir templates\ # Windows

# Check configuration files
ls *.yaml  # macOS/Linux
dir *.yaml # Windows
```

### Log Files

Enable logging to troubleshoot issues:

1. Go to `/config`
2. Check "Log to File"
3. Save configuration
4. Check the generated log file for error details

## 🚀 Advanced Setup

### Running with Custom Settings

```bash
# Custom host and port
python prompt_runner_flask.py --host 0.0.0.0 --port 8080

# Debug mode (for development)
python prompt_runner_flask.py --debug
```

### Using Different AI Providers

**For Venice.ai models:**
1. Sign up at [Venice.ai](https://venice.ai)
2. Get API credentials
3. Update configuration:
   ```yaml
   api_base_url: https://api.venice.ai/api/v1
   model: llama-3.3-70b
   ```

**For different OpenRouter models:**
1. Visit [OpenRouter Models](https://openrouter.ai/models)
2. Copy the model ID
3. Update in `/config` or `flask_config.yaml`

### Production Deployment

For production use, consider:

1. **Use a production WSGI server** (e.g., Gunicorn)
2. **Set up reverse proxy** (e.g., Nginx)
3. **Configure environment variables** securely
4. **Enable SSL/HTTPS**
5. **Set up monitoring and logging**

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 prompt_runner_flask:app
```

## 📞 Getting Help

### Resources

- **OpenRouter Documentation**: https://openrouter.ai/docs
- **Flask Documentation**: https://flask.palletsprojects.com
- **Python Documentation**: https://docs.python.org

### Common Commands Reference

```bash
# Start application
python prompt_runner_flask.py

# Create/recreate templates
python create_templates.py

# Start with custom port
python prompt_runner_flask.py --port 8080

# Start in debug mode
python prompt_runner_flask.py --debug

# Check if everything is working
curl http://localhost:5000/api/prompts
```

### Support Checklist

Before seeking help, please check:

- [ ] Python 3.7+ is installed
- [ ] All dependencies are installed (`pip list`)
- [ ] OpenRouter API key is set
- [ ] Templates directory exists
- [ ] Configuration files are present
- [ ] Port 5000 is available
- [ ] No firewall blocking the application

---

**Need more help?** Check the main README.md file for additional documentation and features.

## 🎯 Next Steps

Once your application is running:

1. **Add your JSON prompt files** to the project directory
2. **Configure your preferred AI models** in the settings
3. **Customize the prompts registry** to organize your prompts
4. **Explore different AI models** through the configuration interface
5. **Create workflows** using different prompts for different tasks

Happy prompting! 🚀