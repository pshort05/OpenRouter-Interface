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
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from flask import Response

from .config_manager import ConfigManager
from .logging_manager import LoggingManager
from .prompt_scanner import PromptScanner
from .prompt_handler import PromptLoader, PromptProcessor
from .prompt_runner_api_client import PromptAPIClient


class FlaskPromptRunner:
    """Flask web application for OpenRouter Prompt Runner."""
    
    def __init__(self):
        """Initialize the Flask application."""
        self.app = Flask(__name__)
        self.app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')
        
        # Configure upload settings
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        self.app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
        
        # Configuration file paths
        self.config_file = 'flask_config.yaml'
        self.prompts_registry_file = 'prompts_registry.yaml'
        
        # Initialize components
        self._init_components()
        self._setup_routes()
        
        logging.info("✓ Flask Prompt Runner initialized successfully")
    
    def _init_components(self):
        """Initialize the core components."""
        # Load configuration
        self.flask_config = self._load_flask_config()
        
        # Initialize components
        self.config = ConfigManager()
        self.config.config = self.flask_config
        self.logging_manager = LoggingManager(self.config)
        self.api_client = PromptAPIClient(self.config)
        
        # Initialize other components
        self.scanner = PromptScanner()
        self.prompt_loader = PromptLoader()
        self.processor = PromptProcessor()
        
        # Storage for session data
        self.session_responses = []
    
    def _load_flask_config(self) -> Dict[str, Any]:
        """Load Flask configuration from YAML file."""
        config_path = Path(self.config_file)
        
        # Default configuration
        default_config = {
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
        
        if config_path.exists():
            logging.info(f"Loading Flask configuration from {self.config_file}")
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
            default_config.update(user_config)
        else:
            logging.info(f"Configuration file {self.config_file} not found, using defaults")
            self._save_flask_config(default_config)
            
        return default_config
    
    def _save_flask_config(self, config: Dict[str, Any]):
        """Save Flask configuration to YAML file."""
        config_path = Path(self.config_file)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=True)
        logging.info(f"Configuration saved to {self.config_file}")
    
    def _reload_configuration(self):
        """Reload configuration and reinitialize components."""
        logging.info("Reloading configuration...")
        self.flask_config = self._load_flask_config()
        self.config.config = self.flask_config
        
        # Update Flask app config
        self.app.config['MAX_CONTENT_LENGTH'] = self.flask_config.get('max_content_length_mb', 16) * 1024 * 1024
        
        # Reinitialize API client with new config
        self.api_client = PromptAPIClient(self.config)
        logging.info("✓ Configuration reloaded successfully")
    
    def _load_prompts_registry(self) -> List[Dict[str, Any]]:
        """Load prompts registry from YAML file."""
        registry_path = Path(self.prompts_registry_file)
        
        if not registry_path.exists():
            logging.warning(f"Prompts registry {self.prompts_registry_file} not found")
            return []
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry_data = yaml.safe_load(f) or {}
        
        return registry_data.get('prompts', [])
    
    def _save_prompts_registry(self, prompts: List[Dict[str, Any]]):
        """Save prompts registry to YAML file."""
        registry_data = {
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prompts': prompts
        }
        
        registry_path = Path(self.prompts_registry_file)
        with open(registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(registry_data, f, default_flow_style=False, sort_keys=False)
        
        logging.info(f"Prompts registry saved to {self.prompts_registry_file}")
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main page showing available prompts."""
            try:
                # Load prompts from registry
                prompts = self._load_prompts_registry()
                
                # Verify prompt files still exist and add metadata
                verified_prompts = []
                for prompt in prompts:
                    prompt_path = Path(prompt['path'])
                    if prompt_path.exists():
                        file_size = prompt_path.stat().st_size
                        prompt.update({
                            'size': file_size,
                            'size_formatted': self._format_file_size(file_size),
                            'exists': True
                        })
                        verified_prompts.append(prompt)
                    else:
                        prompt['exists'] = False
                        verified_prompts.append(prompt)
                
                return render_template('index.html', prompts=verified_prompts)
                
            except Exception as e:
                logging.error(f"Error loading prompts: {e}")
                flash(f"Error loading prompts: {e}", 'error')
                return render_template('index.html', prompts=[])
        
        @self.app.route('/config')
        def show_config():
            """Show configuration page."""
            return render_template('config.html', config=self.flask_config)
        
        @self.app.route('/config', methods=['POST'])
        def update_config():
            """Update configuration."""
            try:
                # Get form data
                new_config = {}
                
                # String fields
                string_fields = ['model', 'api_base_url', 'log_level', 'payload_file']
                for field in string_fields:
                    value = request.form.get(field, '').strip()
                    if value:
                        new_config[field] = value
                
                # Numeric fields
                try:
                    new_config['temperature'] = float(request.form.get('temperature', 0.8))
                    new_config['max_tokens'] = int(request.form.get('max_tokens', 10000))
                    new_config['max_content_length_mb'] = int(request.form.get('max_content_length_mb', 16))
                    new_config['session_timeout_hours'] = int(request.form.get('session_timeout_hours', 24))
                except (ValueError, TypeError) as e:
                    flash(f"Invalid numeric value: {e}", 'error')
                    return redirect(url_for('show_config'))
                
                # Boolean fields
                new_config['log_to_file'] = 'log_to_file' in request.form
                
                # Validate temperature range
                if not 0.0 <= new_config['temperature'] <= 2.0:
                    flash('Temperature must be between 0.0 and 2.0', 'error')
                    return redirect(url_for('show_config'))
                
                # Validate max_tokens range
                if not 1 <= new_config['max_tokens'] <= 100000:
                    flash('Max tokens must be between 1 and 100,000', 'error')
                    return redirect(url_for('show_config'))
                
                # Update and save configuration
                self.flask_config.update(new_config)
                self._save_flask_config(self.flask_config)
                
                # Reload configuration
                self._reload_configuration()
                
                flash('Configuration updated successfully', 'success')
                return redirect(url_for('show_config'))
                
            except Exception as e:
                logging.error(f"Error updating configuration: {e}")
                flash(f"Error updating configuration: {e}", 'error')
                return redirect(url_for('show_config'))
        
        @self.app.route('/prompts_registry')
        def show_prompts_registry():
            """Show prompts registry management page."""
            prompts = self._load_prompts_registry()
            return render_template('prompts_registry.html', prompts=prompts)
        
        @self.app.route('/prompts_registry', methods=['POST'])
        def update_prompts_registry():
            """Update prompts registry."""
            try:
                action = request.form.get('action')
                
                if action == 'rescan':
                    # Rescan directory for JSON files
                    json_files = self.scanner.scan_for_prompts()
                    prompts = []
                    
                    for json_file in json_files:
                        try:
                            # Try to load prompt to get metadata
                            prompt_data = self.prompt_loader.load_prompt(json_file)
                            prompts.append({
                                'name': json_file.name,
                                'path': str(json_file),
                                'title': prompt_data.get('title', json_file.stem),
                                'description': prompt_data.get('description', ''),
                                'enabled': True
                            })
                        except Exception as e:
                            logging.warning(f"Could not load prompt {json_file}: {e}")
                            prompts.append({
                                'name': json_file.name,
                                'path': str(json_file),
                                'title': json_file.stem,
                                'description': f'Error loading: {e}',
                                'enabled': False
                            })
                    
                    self._save_prompts_registry(prompts)
                    flash(f'Registry updated: found {len(prompts)} prompt files', 'success')
                
                elif action == 'save':
                    # Save manual edits to registry
                    prompts = []
                    prompt_count = int(request.form.get('prompt_count', 0))
                    
                    for i in range(prompt_count):
                        name = request.form.get(f'prompt_{i}_name', '').strip()
                        path = request.form.get(f'prompt_{i}_path', '').strip()
                        title = request.form.get(f'prompt_{i}_title', '').strip()
                        description = request.form.get(f'prompt_{i}_description', '').strip()
                        enabled = f'prompt_{i}_enabled' in request.form
                        
                        if name and path:
                            prompts.append({
                                'name': name,
                                'path': path,
                                'title': title or name,
                                'description': description,
                                'enabled': enabled
                            })
                    
                    self._save_prompts_registry(prompts)
                    flash('Prompts registry saved successfully', 'success')
                
                return redirect(url_for('show_prompts_registry'))
                
            except Exception as e:
                logging.error(f"Error updating prompts registry: {e}")
                flash(f"Error updating prompts registry: {e}", 'error')
                return redirect(url_for('show_prompts_registry'))
        
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
                prompts = self._load_prompts_registry()
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
1. Load prompts from prompts_registry.yaml
2. Display them in a web interface with configuration management
3. Allow users to select prompts and provide input content
4. Execute prompts against inputs using OpenRouter API
5. Display responses and maintain session history
6. Allow downloading session history as markdown

Configuration files:
- flask_config.yaml: Application configuration
- prompts_registry.yaml: Registry of available prompts

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