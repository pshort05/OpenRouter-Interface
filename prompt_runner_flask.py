#!/usr/bin/env python3
"""
OpenRouter Prompt Runner - Flask Web Application

A Flask web application that provides a web interface for scanning JSON prompt files
and executing them against input files using the OpenRouter API.

Usage:
    python prompt_runner_flask.py
    
Then navigate to http://localhost:5000 in your browser.
"""

import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from flask import Response

from config_manager import ConfigManager
from logging_manager import LoggingManager
from prompt_scanner import PromptScanner
from prompt_handler import PromptLoader, PromptProcessor
from prompt_runner_api_client import PromptAPIClient


class FlaskPromptRunner:
    """Flask web application for OpenRouter Prompt Runner."""
    
    def __init__(self):
        """Initialize the Flask application."""
        self.app = Flask(__name__)
        self.app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')
        
        # Configure upload settings
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        self.app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
        
        # Initialize components
        self._init_components()
        self._setup_routes()
        
        logging.info("✓ Flask Prompt Runner initialized successfully")
    
    def _init_components(self):
        """Initialize the core components."""
        # Create minimal config for API operations
        config_dict = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.8,
            'max_tokens': 10000,
            'log_level': 'INFO',
            'log_to_file': False,
            'payload_file': 'prompt_runner_flask.payload.json'
        }
        
        # Initialize components
        self.config = ConfigManager()
        self.config.config = config_dict
        self.logging_manager = LoggingManager(self.config)
        self.api_client = PromptAPIClient(self.config)
        
        # Initialize other components
        self.scanner = PromptScanner()
        self.prompt_loader = PromptLoader()
        self.processor = PromptProcessor()
        
        # Storage for session data
        self.session_responses = []
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main page showing available prompts."""
            try:
                # Scan for JSON prompts
                json_files = self.scanner.scan_for_prompts()
                
                # Convert to list of dictionaries for template
                prompts = []
                for json_file in json_files:
                    file_size = json_file.stat().st_size if json_file.exists() else 0
                    prompts.append({
                        'name': json_file.name,
                        'path': str(json_file),
                        'size': file_size,
                        'size_formatted': self._format_file_size(file_size)
                    })
                
                return render_template('index.html', prompts=prompts)
                
            except Exception as e:
                logging.error(f"Error scanning for prompts: {e}")
                flash(f"Error scanning for prompts: {e}", 'error')
                return render_template('index.html', prompts=[])
        
        @self.app.route('/prompt/<path:prompt_file>')
        def show_prompt(prompt_file):
            """Show prompt details and input form."""
            try:
                prompt_path = Path(prompt_file)
                
                if not prompt_path.exists():
                    flash(f"Prompt file not found: {prompt_file}", 'error')
                    return redirect(url_for('index'))
                
                # Load and validate prompt
                prompt_data = self.prompt_loader.load_prompt(prompt_path)
                
                # Format prompt data for display
                prompt_info = {
                    'name': prompt_path.name,
                    'path': str(prompt_path),
                    'title': prompt_data.get('title', 'Untitled Prompt'),
                    'persona': prompt_data.get('persona', ''),
                    'has_instructions': 'instructions' in prompt_data,
                    'has_criteria': 'review_criteria' in prompt_data,
                    'field_count': len(prompt_data.keys())
                }
                
                return render_template('prompt_form.html', prompt=prompt_info)
                
            except Exception as e:
                logging.error(f"Error loading prompt {prompt_file}: {e}")
                flash(f"Error loading prompt: {e}", 'error')
                return redirect(url_for('index'))
        
        @self.app.route('/execute', methods=['POST'])
        def execute_prompt():
            """Execute a prompt against input content."""
            try:
                prompt_file = request.form.get('prompt_file')
                input_method = request.form.get('input_method', 'text')
                
                if not prompt_file:
                    return jsonify({'error': 'No prompt file specified'}), 400
                
                prompt_path = Path(prompt_file)
                if not prompt_path.exists():
                    return jsonify({'error': f'Prompt file not found: {prompt_file}'}), 404
                
                # Get input content
                if input_method == 'file':
                    if 'input_file' not in request.files:
                        return jsonify({'error': 'No file uploaded'}), 400
                    
                    file = request.files['input_file']
                    if file.filename == '':
                        return jsonify({'error': 'No file selected'}), 400
                    
                    # Read file content
                    input_content = file.read().decode('utf-8')
                    input_name = secure_filename(file.filename)
                    
                else:  # text input
                    input_content = request.form.get('input_text', '').strip()
                    input_name = 'Text Input'
                    
                    if not input_content:
                        return jsonify({'error': 'No input content provided'}), 400
                
                # Load prompt
                prompt_data = self.prompt_loader.load_prompt(prompt_path)
                
                # Create full prompt
                full_prompt = self.processor.create_full_prompt(prompt_data, input_content)
                
                # Call API
                response = self.api_client.call_api(full_prompt)
                
                # Store response for session history
                response_data = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'prompt_name': prompt_path.name,
                    'input_name': input_name,
                    'response': response,
                    'input_length': len(input_content),
                    'response_length': len(response)
                }
                
                self.session_responses.append(response_data)
                
                return jsonify({
                    'success': True,
                    'response': response,
                    'metadata': {
                        'prompt_name': prompt_path.name,
                        'input_name': input_name,
                        'timestamp': response_data['timestamp'],
                        'input_length': len(input_content),
                        'response_length': len(response)
                    }
                })
                
            except Exception as e:
                logging.error(f"Error executing prompt: {e}")
                return jsonify({'error': f'Execution failed: {str(e)}'}), 500
        
        @self.app.route('/history')
        def show_history():
            """Show session response history."""
            return render_template('history.html', responses=self.session_responses)
        
        @self.app.route('/download_history')
        def download_history():
            """Download session history as markdown file."""
            if not self.session_responses:
                flash('No responses to download', 'info')
                return redirect(url_for('show_history'))
            
            # Create markdown content
            markdown_content = "# Prompt Runner Session History\n\n"
            markdown_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for i, response_data in enumerate(self.session_responses, 1):
                markdown_content += f"## Response {i} - {response_data['timestamp']}\n\n"
                markdown_content += f"**Prompt:** `{response_data['prompt_name']}`  \n"
                markdown_content += f"**Input:** {response_data['input_name']}  \n"
                markdown_content += f"**Input Length:** {response_data['input_length']} characters  \n"
                markdown_content += f"**Response Length:** {response_data['response_length']} characters  \n\n"
                markdown_content += "---\n\n"
                markdown_content += response_data['response']
                markdown_content += "\n\n---\n\n"
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(markdown_content)
                temp_file = f.name
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prompt_runner_history_{timestamp}.md"
            
            return send_file(
                temp_file,
                as_attachment=True,
                download_name=filename,
                mimetype='text/markdown'
            )
        
        @self.app.route('/clear_history', methods=['POST'])
        def clear_history():
            """Clear session history."""
            self.session_responses.clear()
            flash('Session history cleared', 'success')
            return redirect(url_for('show_history'))
        
        @self.app.route('/api/prompts')
        def api_get_prompts():
            """API endpoint to get available prompts."""
            try:
                json_files = self.scanner.scan_for_prompts()
                prompts = []
                for json_file in json_files:
                    file_size = json_file.stat().st_size if json_file.exists() else 0
                    prompts.append({
                        'name': json_file.name,
                        'path': str(json_file),
                        'size': file_size
                    })
                return jsonify({'prompts': prompts})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/prompt/<path:prompt_file>')
        def api_get_prompt(prompt_file):
            """API endpoint to get prompt details."""
            try:
                prompt_path = Path(prompt_file)
                if not prompt_path.exists():
                    return jsonify({'error': 'Prompt file not found'}), 404
                
                prompt_data = self.prompt_loader.load_prompt(prompt_path)
                return jsonify({'prompt': prompt_data})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.errorhandler(413)
        def too_large(e):
            flash('File too large. Maximum size is 16MB.', 'error')
            return redirect(url_for('index'))
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Run the Flask application."""
        print(f"Starting OpenRouter Prompt Runner Flask App...")
        print(f"Navigate to http://{host}:{port} in your browser")
        print("Press Ctrl+C to stop the server")
        
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main entry point for the Flask application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OpenRouter Prompt Runner - Flask Web Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python prompt_runner_flask.py
    python prompt_runner_flask.py --host 0.0.0.0 --port 8080
    python prompt_runner_flask.py --debug

The web application will:
1. Scan the current directory for .json prompt files
2. Display them in a web interface
3. Allow users to select prompts and provide input content
4. Execute prompts against inputs using OpenRouter API
5. Display responses and maintain session history
6. Allow downloading session history as markdown

Note: Ensure the templates/ directory exists with the required HTML template files.
        """
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind the server to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind the server to (default: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )
    
    args = parser.parse_args()
    
    try:
        # Check if templates directory exists
        templates_dir = Path('templates')
        if not templates_dir.exists():
            print("Error: templates/ directory not found.")
            print("Please create the templates directory with the required HTML files.")
            print("Run create_templates.py to generate the template files.")
            return 1
        
        # Initialize and run the Flask app
        flask_runner = FlaskPromptRunner()
        flask_runner.run(host=args.host, port=args.port, debug=args.debug)
        
    except Exception as e:
        logging.error(f"Failed to start Flask application: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())