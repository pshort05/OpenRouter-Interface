# OpenRouter Prompt Runner Flask Application

A comprehensive Flask web application for managing and executing JSON prompt files using the OpenRouter API. Features include configuration management, prompts registry, session history, and a modern web interface.

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
Configure your preferred model in the web interface at `/config` or by editing `flask_config.yaml`:

```yaml
model: anthropic/claude-4-sonnet-20250522  # Default model
temperature: 0.8
max_tokens: 10000
```

## 🚀 Features

### Core Functionality
- **Prompt Execution**: Execute JSON prompt files against text or file inputs
- **Multiple Input Methods**: Support for text input and file uploads
- **Real-time Processing**: AJAX-based form submission with loading indicators
- **Session History**: Track all responses within a session with download capability

### Administration & Management
- **Configuration Management**: Web-based interface to modify all application settings
- **Prompts Registry**: Manage available prompts with enable/disable functionality
- **Live Configuration Reload**: Changes applied immediately without restart
- **Directory Scanning**: Automatic discovery of JSON prompt files

### User Interface
- **Modern Design**: Clean, responsive interface with mobile support
- **Interactive Elements**: Loading spinners, hover effects, and smooth transitions
- **Navigation**: Intuitive navigation between all application sections
- **Flash Messages**: User feedback for all operations

## 📋 Quick Start

### 1. Initial Setup
```bash
# Clone or download the project files
# Ensure you have Python 3.7+ installed

# Install required dependencies
pip install flask pyyaml requests

# Set your OpenRouter API key
export OPENROUTER_API_KEY="your_api_key_here"
```

### 2. Create Templates and Configuration
```bash
# Run the setup script to create all necessary files
python create_templates.py
```

This will create:
- `templates/` directory with all HTML templates
- `flask_config.yaml` with application configuration
- `prompts_registry.yaml` with discovered JSON prompts

### 3. Run the Application
```bash
# Start the Flask application
python prompt_runner_flask.py

# Navigate to http://localhost:5000
```

## 📁 Project Structure

```
project/
├── prompt_runner_flask.py          # Main Flask application
├── create_templates.py             # Setup script for templates and config
├── flask_config.yaml              # Application configuration
├── prompts_registry.yaml          # Registry of available prompts
├── templates/                      # HTML templates
│   ├── base.html                  # Base template with shared layout
│   ├── index.html                 # Main page showing prompts
│   ├── config.html                # Configuration management
│   ├── prompts_registry.html      # Prompts registry management
│   ├── prompt_form.html          # Prompt execution form
│   └── history.html              # Session history display
├── *.json                         # Your JSON prompt files
└── README.md                      # This file
```

## 🔧 Configuration

### Application Settings (`flask_config.yaml`)

The application can be configured through the web interface at `/config` or by editing the YAML file directly:

```yaml
# OpenRouter API Settings
model: anthropic/claude-4-sonnet-20250522
api_base_url: https://openrouter.ai/api/v1
temperature: 0.8
max_tokens: 10000

# Application Settings
log_level: INFO
log_to_file: false
max_content_length_mb: 16
session_timeout_hours: 24
payload_file: prompt_runner_flask.payload.json
```

### Prompts Registry (`prompts_registry.yaml`)

Manage available prompts through the web interface at `/prompts_registry` or edit the file:

```yaml
created: '2025-01-07 10:30:00'
prompts:
  - name: example_prompt.json
    path: ./example_prompt.json
    title: Example Prompt
    description: A sample prompt for demonstration
    enabled: true
```

## 🌐 Web Interface

### Main Pages

- **Home (`/`)**: Browse and select available prompts
- **Configuration (`/config`)**: Manage application settings
- **Prompts Registry (`/prompts_registry`)**: Manage prompt files
- **History (`/history`)**: View session responses and download history

### API Endpoints

- **GET `/api/prompts`**: Get list of available prompts
- **GET `/api/prompt/<path>`**: Get specific prompt details
- **POST `/execute`**: Execute a prompt (JSON response)

## 🎯 Usage Examples

### Adding New Prompts

1. **Automatic Discovery**:
   - Add `.json` files to the project directory
   - Go to `/prompts_registry` and click "Rescan Directory"

2. **Manual Addition**:
   - Edit `prompts_registry.yaml` directly
   - Add prompt entries with required fields

### Executing Prompts

1. **Text Input**:
   - Select a prompt from the home page
   - Choose "Text Input" method
   - Enter your content and click "Execute Prompt"

2. **File Upload**:
   - Select a prompt from the home page
   - Choose "File Upload" method
   - Upload a `.txt`, `.md`, `.json`, or `.csv` file

### Managing Configuration

1. **Web Interface**:
   - Navigate to `/config`
   - Modify settings using the form
   - Click "Save Configuration"

2. **Direct File Editing**:
   - Edit `flask_config.yaml`
   - Restart the application

## 🔒 Security Considerations

- **API Key Protection**: Store your OpenRouter API key as an environment variable
- **File Upload Limits**: Configure appropriate upload size limits
- **Input Validation**: All form inputs are validated before processing
- **Session Management**: Sessions are memory-based and cleared on restart

## 🛠️ Development

### Custom Styling

Modify the CSS in `templates/base.html` to customize the appearance:

```css
/* Example: Change primary color */
.btn {
    background: #your-color;
}
```

### Adding New Features

1. **New Routes**: Add route handlers in `prompt_runner_flask.py`
2. **New Templates**: Create HTML templates in the `templates/` directory
3. **Configuration Options**: Add new settings to the configuration system

### Dependencies

Required Python packages:
- `flask` - Web framework
- `pyyaml` - YAML configuration handling
- `requests` - HTTP client for API calls

Additional packages may be required based on your specific prompt handler implementations.

## 📈 Monitoring and Logging

### Log Levels

Configure logging in the web interface or configuration file:
- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

### Session History

- **In-Memory Storage**: History is stored in memory during the session
- **Download Feature**: Export session history as Markdown
- **Automatic Cleanup**: History is cleared when the application restarts

## 🚨 Troubleshooting

### Common Issues

1. **Templates Not Found**:
   ```bash
   # Run the setup script
   python create_templates.py
   ```

2. **API Key Errors**:
   ```bash
   # Set your API key
   export OPENROUTER_API_KEY="your_key_here"
   ```

3. **No Prompts Visible**:
   - Check `prompts_registry.yaml` exists
   - Verify JSON files are in the directory
   - Use "Rescan Directory" in the prompts registry

4. **Configuration Not Loading**:
   - Check `flask_config.yaml` format
   - Verify file permissions
   - Check application logs

### File Permissions

Ensure the application has read/write permissions for:
- Configuration files (`.yaml`)
- Template directory
- Temporary upload directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and development purposes. Please ensure compliance with OpenRouter's terms of service when using their API.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration files
3. Check application logs
4. Verify API key and network connectivity

---

**Happy Prompting!** 🎉