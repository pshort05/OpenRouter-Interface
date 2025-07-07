#!/usr/bin/env python3
"""
Template Creation Script for OpenRouter Prompt Runner Flask App

Creates the HTML template files required for the Flask web application.

Usage:
    python create_templates.py
"""

from pathlib import Path


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
        .prompt-card h3 { margin: 0 0 10px 0; font-size: 1.1em; }
        .prompt-meta { font-size: 0.9em; color: #666; margin-bottom: 15px; }
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
        }
        .btn:hover { background: #2980b9; }
        .btn-secondary { background: #95a5a6; }
        .btn-secondary:hover { background: #7f8c8d; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
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
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-info { background: #cce7ff; color: #004085; border: 1px solid #bee5eb; }
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
    </style>
</head>
<body>
    <div class="container">
        <nav class="navbar">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('show_history') }}">History</a>
        </nav>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'info' }}">
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
        <div class="prompt-card">
            <h3>{{ prompt.name }}</h3>
            <div class="prompt-meta">
                Size: {{ prompt.size_formatted }}
            </div>
            <a href="{{ url_for('show_prompt', prompt_file=prompt.path) }}" class="btn">Use This Prompt</a>
        </div>
        {% endfor %}
    </div>
{% else %}
    <div class="alert alert-info">
        <strong>No JSON prompt files found</strong><br>
        Please add some .json prompt files to the current directory and refresh the page.
    </div>
{% endif %}
{% endblock %}'''
    
    with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_template)
    print("✓ Created index.html")
    
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
    print("You can now run the Flask application with: python prompt_runner_flask.py")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create HTML templates for OpenRouter Prompt Runner Flask App",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script creates the following template files:
- templates/base.html - Base template with shared layout and styling
- templates/index.html - Main page showing available prompts
- templates/prompt_form.html - Form for executing prompts
- templates/history.html - Session history display

After running this script, you can start the Flask application.
        """
    )
    
    args = parser.parse_args()
    
    try:
        create_templates()
        return 0
    except Exception as e:
        print(f"Error creating templates: {e}")
        return 1


if __name__ == "__main__":
    exit(main())