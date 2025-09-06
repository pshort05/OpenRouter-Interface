#!/usr/bin/env python3
"""
Template Creation Script for OpenRouter Prompt Runner Flask App

Creates the HTML template files and initial configuration files 
required for the Flask web application.

Usage:
    python create_templates.py
"""

import json
import yaml
from datetime import datetime
from pathlib import Path


def scan_for_json_prompts():
    """Scan current directory for JSON files and create prompts registry."""
    current_dir = Path('.')
    json_files = list(current_dir.glob('*.json'))
    
    prompts = []
    for json_file in json_files:
        try:
            # Try to load the JSON file to validate it and extract metadata
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            prompts.append({
                'name': json_file.name,
                'path': str(json_file),
                'title': data.get('title', json_file.stem),
                'description': data.get('description', f'JSON prompt file: {json_file.name}'),
                'enabled': True
            })
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Could not process {json_file}: {e}")
            # Still add it but mark as potentially problematic
            prompts.append({
                'name': json_file.name,
                'path': str(json_file),
                'title': json_file.stem,
                'description': f'JSON file (validation error: {e})',
                'enabled': False
            })
    
    return prompts


def create_config_files():
    """Create configuration files."""
    print("Creating configuration files...")
    
    # Create Flask configuration
    flask_config = {
        'model': 'anthropic/claude-4-sonnet-20250522',
        'api_base_url': 'https://openrouter.ai/api/v1',
        'temperature': 0.8,
        'max_tokens': 10000,
        'log_level': 'INFO',
        'log_to_file': False,
        'payload_file': 'prompt_runner_flask.payload.json',
        'max_content_length_mb': 16,
        'session_timeout_hours': 24
    }
    
    with open('flask_config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(flask_config, f, default_flow_style=False, sort_keys=True)
    print("✓ Created flask_config.yaml")
    
    # Create prompts registry by scanning directory
    prompts = scan_for_json_prompts()
    
    registry_data = {
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'prompts': prompts
    }
    
    with open('prompts_registry.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(registry_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Created prompts_registry.yaml with {len(prompts)} prompts")
    if prompts:
        for prompt in prompts:
            status = "✓" if prompt['enabled'] else "⚠"
            print(f"  {status} {prompt['name']} - {prompt['title']}")


def create_templates():
    """Create HTML templates for the Flask application."""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    print(f"Creating templates in {templates_dir.absolute()}")
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OpenRouter Prompt Runner{% endblock %}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 { color: #2c3e50; }
        .prompt-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .prompt-card {
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            background: #f9f9f9;
            transition: all 0.3s ease;
        }
        .prompt-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .prompt-card.disabled { opacity: 0.6; background: #f0f0f0; }
        .prompt-card h3 { margin: 0 0 10px 0; font-size: 1.1em; }
        .prompt-meta { font-size: 0.9em; color: #666; margin-bottom: 15px; }
        .prompt-description { font-size: 0.85em; color: #777; margin-bottom: 10px; }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-right: 10px;
            margin-bottom: 5px;
        }
        .btn:hover { background: #2980b9; }
        .btn-secondary { background: #95a5a6; }
        .btn-secondary:hover { background: #7f8c8d; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
        .btn:disabled { background: #bdc3c7; cursor: not-allowed; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .form-group textarea { min-height: 200px; resize: vertical; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .form-row .form-group { margin-bottom: 15px; }
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-info { background: #cce7ff; color: #004085; border: 1px solid #bee5eb; }
        .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .response-container {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 20px;
            margin-top: 20px;
        }
        .response-meta {
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        .response-content {
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            background: white;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
            max-height: 600px;
            overflow-y: auto;
        }
        .navbar {
            background: #2c3e50;
            padding: 10px 0;
            margin: -30px -30px 30px -30px;
            border-radius: 8px 8px 0 0;
        }
        .navbar a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            display: inline-block;
        }
        .navbar a:hover { background: #34495e; }
        .navbar a.active { background: #34495e; }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .history-item {
            border: 1px solid #ddd;
            border-radius: 6px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .history-header {
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #ddd;
        }
        .history-content {
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
        }
        .config-section {
            border: 1px solid #ddd;
            border-radius: 6px;
            margin-bottom: 20px;
            padding: 20px;
            background: #f9f9f9;
        }
        .config-section h3 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        .registry-item {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            background: white;
        }
        .registry-item.disabled { background: #f8f9fa; opacity: 0.8; }
        .registry-controls { margin-bottom: 20px; }
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="navbar">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('show_history') }}">History</a>
            <a href="{{ url_for('show_config') }}">Configuration</a>
            <a href="{{ url_for('show_prompts_registry') }}">Prompts Registry</a>
        </nav>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'info' if category == 'info' else 'warning' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(templates_dir / 'base.html', 'w', encoding='utf-8') as f:
        f.write(base_template)
    print("✓ Created base.html")
    
    # Index template
    index_template = '''{% extends "base.html" %}

{% block title %}Prompt Runner - Available Prompts{% endblock %}

{% block content %}
<h1>OpenRouter Prompt Runner</h1>
<p>Select a JSON prompt file to execute against your input content.</p>

{% if prompts %}
    <div class="prompt-list">
        {% for prompt in prompts %}
        <div class="prompt-card {{ 'disabled' if not prompt.enabled or not prompt.exists }}">
            <h3>{{ prompt.title or prompt.name }}</h3>
            <div class="prompt-meta">
                <strong>File:</strong> {{ prompt.name }}<br>
                {% if prompt.exists %}
                    <strong>Size:</strong> {{ prompt.size_formatted }}<br>
                {% else %}
                    <strong>Status:</strong> <span style="color: #e74c3c;">File not found</span><br>
                {% endif %}
                <strong>Enabled:</strong> {{ "Yes" if prompt.enabled else "No" }}
            </div>
            {% if prompt.description %}
            <div class="prompt-description">{{ prompt.description }}</div>
            {% endif %}
            {% if prompt.enabled and prompt.exists %}
                <a href="{{ url_for('show_prompt', prompt_file=prompt.path) }}" class="btn">Use This Prompt</a>
            {% else %}
                <button class="btn" disabled>{{ "File Missing" if not prompt.exists else "Disabled" }}</button>
            {% endif %}
        </div>
        {% endfor %}
    </div>
{% else %}
    <div class="alert alert-info">
        <strong>No prompts configured</strong><br>
        Please check the <a href="{{ url_for('show_prompts_registry') }}">Prompts Registry</a> to configure available prompts.
    </div>
{% endif %}
{% endblock %}'''
    
    with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_template)
    print("✓ Created index.html")
    
    # Configuration template
    config_template = '''{% extends "base.html" %}

{% block title %}Configuration{% endblock %}

{% block content %}
<h1>Configuration</h1>
<p>Modify application settings. Changes will be saved and the application configuration will be reloaded.</p>

<form method="POST" action="{{ url_for('update_config') }}">
    <div class="config-section">
        <h3>OpenRouter API Settings</h3>
        <div class="form-row">
            <div class="form-group">
                <label for="model">Model:</label>
                <input type="text" name="model" id="model" value="{{ config.model }}" required>
            </div>
            <div class="form-group">
                <label for="api_base_url">API Base URL:</label>
                <input type="url" name="api_base_url" id="api_base_url" value="{{ config.api_base_url }}" required>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label for="temperature">Temperature (0.0 - 2.0):</label>
                <input type="number" name="temperature" id="temperature" value="{{ config.temperature }}" 
                       min="0" max="2" step="0.1" required>
            </div>
            <div class="form-group">
                <label for="max_tokens">Max Tokens (1 - 100,000):</label>
                <input type="number" name="max_tokens" id="max_tokens" value="{{ config.max_tokens }}" 
                       min="1" max="100000" required>
            </div>
        </div>
    </div>
    
    <div class="config-section">
        <h3>Application Settings</h3>
        <div class="form-row">
            <div class="form-group">
                <label for="log_level">Log Level:</label>
                <select name="log_level" id="log_level">
                    <option value="DEBUG" {{ 'selected' if config.log_level == 'DEBUG' }}>DEBUG</option>
                    <option value="INFO" {{ 'selected' if config.log_level == 'INFO' }}>INFO</option>
                    <option value="WARNING" {{ 'selected' if config.log_level == 'WARNING' }}>WARNING</option>
                    <option value="ERROR" {{ 'selected' if config.log_level == 'ERROR' }}>ERROR</option>
                </select>
            </div>
            <div class="form-group">
                <div class="checkbox-group">
                    <input type="checkbox" name="log_to_file" id="log_to_file" 
                           {{ 'checked' if config.log_to_file }}>
                    <label for="log_to_file">Log to File</label>
                </div>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label for="max_content_length_mb">Max Upload Size (MB):</label>
                <input type="number" name="max_content_length_mb" id="max_content_length_mb" 
                       value="{{ config.max_content_length_mb }}" min="1" max="100" required>
            </div>
            <div class="form-group">
                <label for="session_timeout_hours">Session Timeout (Hours):</label>
                <input type="number" name="session_timeout_hours" id="session_timeout_hours" 
                       value="{{ config.session_timeout_hours }}" min="1" max="168" required>
            </div>
        </div>
        <div class="form-group">
            <label for="payload_file">Payload File:</label>
            <input type="text" name="payload_file" id="payload_file" 
                   value="{{ config.payload_file }}" required>
        </div>
    </div>
    
    <div style="margin-top: 30px;">
        <button type="submit" class="btn btn-success">Save Configuration</button>
        <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancel</a>
    </div>
</form>

<div class="config-section" style="margin-top: 30px;">
    <h3>Current Configuration File</h3>
    <p><strong>Location:</strong> flask_config.yaml</p>
    <p><em>Note: You can also edit the configuration file directly and restart the application.</em></p>
</div>
{% endblock %}'''
    
    with open(templates_dir / 'config.html', 'w', encoding='utf-8') as f:
        f.write(config_template)
    print("✓ Created config.html")
    
    # Prompts registry template
    registry_template = '''{% extends "base.html" %}

{% block title %}Prompts Registry{% endblock %}

{% block content %}
<h1>Prompts Registry</h1>
<p>Manage the registry of available prompt files. You can rescan the directory or manually edit the registry.</p>

<div class="registry-controls">
    <form method="POST" action="{{ url_for('update_prompts_registry') }}" style="display: inline;">
        <input type="hidden" name="action" value="rescan">
        <button type="submit" class="btn btn-success">Rescan Directory</button>
    </form>
    <a href="{{ url_for('index') }}" class="btn btn-secondary">Back to Home</a>
</div>

<form method="POST" action="{{ url_for('update_prompts_registry') }}">
    <input type="hidden" name="action" value="save">
    <input type="hidden" name="prompt_count" value="{{ prompts|length }}">
    
    {% if prompts %}
        {% for prompt in prompts %}
        <div class="registry-item {{ 'disabled' if not prompt.enabled }}">
            <div class="form-row">
                <div class="form-group">
                    <label for="prompt_{{ loop.index0 }}_name">File Name:</label>
                    <input type="text" name="prompt_{{ loop.index0 }}_name" 
                           value="{{ prompt.name }}" readonly>
                </div>
                <div class="form-group">
                    <label for="prompt_{{ loop.index0 }}_path">File Path:</label>
                    <input type="text" name="prompt_{{ loop.index0 }}_path" 
                           value="{{ prompt.path }}" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="prompt_{{ loop.index0 }}_title">Title:</label>
                    <input type="text" name="prompt_{{ loop.index0 }}_title" 
                           value="{{ prompt.title }}" required>
                </div>
                <div class="form-group">
                    <div class="checkbox-group" style="margin-top: 30px;">
                        <input type="checkbox" name="prompt_{{ loop.index0 }}_enabled" 
                               id="prompt_{{ loop.index0 }}_enabled" 
                               {{ 'checked' if prompt.enabled }}>
                        <label for="prompt_{{ loop.index0 }}_enabled">Enabled</label>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="prompt_{{ loop.index0 }}_description">Description:</label>
                <textarea name="prompt_{{ loop.index0 }}_description" 
                          style="min-height: 60px;">{{ prompt.description }}</textarea>
            </div>
        </div>
        {% endfor %}
        
        <div style="margin-top: 30px;">
            <button type="submit" class="btn btn-success">Save Registry</button>
            <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancel</a>
        </div>
    {% else %}
        <div class="alert alert-info">
            <strong>No prompts in registry</strong><br>
            Click "Rescan Directory" to scan for JSON files in the current directory.
        </div>
    {% endif %}
</form>

<div class="config-section" style="margin-top: 30px;">
    <h3>Registry Information</h3>
    <p><strong>Registry File:</strong> prompts_registry.yaml</p>
    <p><strong>Prompts Count:</strong> {{ prompts|length }}</p>
    <p><em>The registry file can also be edited directly with a text editor.</em></p>
</div>
{% endblock %}'''
    
    with open(templates_dir / 'prompts_registry.html', 'w', encoding='utf-8') as f:
        f.write(registry_template)
    print("✓ Created prompts_registry.html")
    
    # Prompt form template
    prompt_form_template = '''{% extends "base.html" %}

{% block title %}Execute Prompt - {{ prompt.name }}{% endblock %}

{% block content %}
<h1>Execute Prompt</h1>
<h2>{{ prompt.title or prompt.name }}</h2>

<div class="response-meta">
    <strong>Prompt File:</strong> {{ prompt.name }}<br>
    <strong>Fields:</strong> {{ prompt.field_count }}<br>
    {% if prompt.has_instructions %}<strong>Has Instructions:</strong> Yes<br>{% endif %}
    {% if prompt.has_criteria %}<strong>Has Review Criteria:</strong> Yes<br>{% endif %}
</div>

<form id="promptForm" method="POST" action="{{ url_for('execute_prompt') }}" enctype="multipart/form-data">
    <input type="hidden" name="prompt_file" value="{{ prompt.path }}">
    
    <div class="form-group">
        <label for="input_method">Input Method:</label>
        <select name="input_method" id="input_method" onchange="toggleInputMethod()">
            <option value="text">Text Input</option>
            <option value="file">File Upload</option>
        </select>
    </div>
    
    <div id="text_input" class="form-group">
        <label for="input_text">Input Content:</label>
        <textarea name="input_text" id="input_text" placeholder="Enter the content you want to analyze with this prompt..."></textarea>
    </div>
    
    <div id="file_input" class="form-group" style="display: none;">
        <label for="input_file">Upload Input File:</label>
        <input type="file" name="input_file" id="input_file" accept=".txt,.md,.json,.csv">
    </div>
    
    <button type="submit" class="btn">Execute Prompt</button>
    <a href="{{ url_for('index') }}" class="btn btn-secondary">Back to Prompts</a>
</form>

<div id="loading" class="loading">
    <div class="spinner"></div>
    <p>Processing your request...</p>
</div>

<div id="response" class="response-container" style="display: none;">
    <div id="response-meta" class="response-meta"></div>
    <div id="response-content" class="response-content"></div>
</div>
{% endblock %}

{% block scripts %}
<script>
function toggleInputMethod() {
    const method = document.getElementById('input_method').value;
    const textInput = document.getElementById('text_input');
    const fileInput = document.getElementById('file_input');
    
    if (method === 'file') {
        textInput.style.display = 'none';
        fileInput.style.display = 'block';
    } else {
        textInput.style.display = 'block';
        fileInput.style.display = 'none';
    }
}

document.getElementById('promptForm').onsubmit = function(e) {
    e.preventDefault();
    
    const loading = document.getElementById('loading');
    const response = document.getElementById('response');
    
    loading.style.display = 'block';
    response.style.display = 'none';
    
    const formData = new FormData(this);
    
    fetch('{{ url_for("execute_prompt") }}', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = 'none';
        
        if (data.success) {
            const responseMeta = document.getElementById('response-meta');
            const responseContent = document.getElementById('response-content');
            
            responseMeta.innerHTML = `
                <strong>Prompt:</strong> ${data.metadata.prompt_name}<br>
                <strong>Input:</strong> ${data.metadata.input_name}<br>
                <strong>Timestamp:</strong> ${data.metadata.timestamp}<br>
                <strong>Input Length:</strong> ${data.metadata.input_length} characters<br>
                <strong>Response Length:</strong> ${data.metadata.response_length} characters
            `;
            
            responseContent.textContent = data.response;
            document.getElementById('response').style.display = 'block';
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        loading.style.display = 'none';
        alert('Error: ' + error.message);
    });
};
</script>
{% endblock %}'''
    
    with open(templates_dir / 'prompt_form.html', 'w', encoding='utf-8') as f:
        f.write(prompt_form_template)
    print("✓ Created prompt_form.html")
    
    # History template
    history_template = '''{% extends "base.html" %}

{% block title %}Session History{% endblock %}

{% block content %}
<h1>Session History</h1>

<div style="margin-bottom: 20px;">
    {% if responses %}
        <a href="{{ url_for('download_history') }}" class="btn">Download as Markdown</a>
        <form method="POST" action="{{ url_for('clear_history') }}" style="display: inline;" 
              onsubmit="return confirm('Are you sure you want to clear the session history?');">
            <button type="submit" class="btn btn-danger">Clear History</button>
        </form>
        <p><strong>{{ responses|length }}</strong> response(s) in this session</p>
    {% else %}
        <div class="alert alert-info">
            No responses in this session yet. <a href="{{ url_for('index') }}">Run some prompts</a> to see them here.
        </div>
    {% endif %}
</div>

{% for response in responses %}
<div class="history-item">
    <div class="history-header">
        <strong>{{ response.prompt_name }}</strong> - {{ response.timestamp }}<br>
        <small>Input: {{ response.input_name }} ({{ response.input_length }} chars) | 
               Response: {{ response.response_length }} chars</small>
    </div>
    <div class="history-content">
        <pre>{{ response.response }}</pre>
    </div>
</div>
{% endfor %}
{% endblock %}'''
    
    with open(templates_dir / 'history.html', 'w', encoding='utf-8') as f:
        f.write(history_template)
    print("✓ Created history.html")
    
    print(f"\n✓ All templates created successfully in {templates_dir.absolute()}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create HTML templates and configuration files for OpenRouter Prompt Runner Flask App",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script creates:
1. Configuration files:
   - flask_config.yaml - Application configuration
   - prompts_registry.yaml - Registry of available prompts (scanned from directory)

2. Template files:
   - templates/base.html - Base template with shared layout and styling
   - templates/index.html - Main page showing available prompts
   - templates/config.html - Configuration management page
   - templates/prompts_registry.html - Prompts registry management page
   - templates/prompt_form.html - Form for executing prompts
   - templates/history.html - Session history display

After running this script, you can start the Flask application.
        """
    )
    
    args = parser.parse_args()
    
    try:
        # Create configuration files first
        create_config_files()
        
        # Create templates
        create_templates()
        
        print("\n" + "="*60)
        print("Setup completed successfully!")
        print("="*60)
        print("Next steps:")
        print("1. Set your OPENROUTER_API_KEY environment variable")
        print("2. Edit flask_config.yaml if needed")
        print("3. Edit prompts_registry.yaml to customize prompt settings")
        print("4. Run: python prompt_runner_flask.py")
        print("5. Navigate to http://localhost:5000")
        print("="*60)
        
        return 0
    except Exception as e:
        print(f"Error during setup: {e}")
        return 1


if __name__ == "__main__":
    exit(main())