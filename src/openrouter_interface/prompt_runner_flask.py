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
import subprocess
import threading
import time
import uuid
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
from .prompt_chain_runner import PromptChainRunner


class FlaskPromptRunner:
    """Flask web application for OpenRouter Prompt Runner."""
    
    def __init__(self):
        """Initialize the Flask application."""
        # Set template folder to the project root's templates folder
        self.project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        template_folder = os.path.join(self.project_root, 'templates')
        self.app = Flask(__name__, template_folder=template_folder)
        self.app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')
        
        # Configure upload settings
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        self.app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
        
        # Configuration file paths - look in parent directory (project root)
        self.config_file = 'flask_config.yaml'
        self.prompts_registry_file = os.path.join(self.project_root, 'prompts_registry.yaml')
        
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
        
        # Initialize other components - point scanner to prompts directory in project root
        prompts_dir = os.path.join(self.project_root, 'prompts')
        self.scanner = PromptScanner(prompts_dir)
        self.prompt_loader = PromptLoader()
        self.processor = PromptProcessor()
        
        # Storage for session data
        self.session_responses = []
        
        # Chain runner management
        self.active_chains = {}  # Dict[chain_id, chain_info]
        self.chain_lock = threading.Lock()
    
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
                    # Build full path from project root + prompts directory + file name
                    if 'file' in prompt:
                        prompt_file_path = os.path.join(self.project_root, 'prompts', prompt['file'])
                        prompt_path = Path(prompt_file_path)
                        # Use relative path for URL routing (prompts/filename.json)
                        prompt['path'] = f"prompts/{prompt['file']}" 
                        prompt['full_path'] = str(prompt_path)  # Keep full path for file operations
                        
                        if prompt_path.exists():
                            file_size = prompt_path.stat().st_size
                            prompt.update({
                                'size': file_size,
                                'size_formatted': self._format_file_size(file_size),
                                'exists': True
                            })
                        else:
                            prompt['exists'] = False
                        verified_prompts.append(prompt)
                    else:
                        # Skip prompts without file reference
                        continue
                
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
                # If prompt_file is relative (e.g., "prompts/file.json"), resolve it to project root
                if not os.path.isabs(prompt_file):
                    prompt_path = Path(os.path.join(self.project_root, prompt_file))
                else:
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
                
                # If prompt_file is relative, resolve it to project root
                if not os.path.isabs(prompt_file):
                    prompt_path = Path(os.path.join(self.project_root, prompt_file))
                else:
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
                # If prompt_file is relative, resolve it to project root
                if not os.path.isabs(prompt_file):
                    prompt_path = Path(os.path.join(self.project_root, prompt_file))
                else:
                    prompt_path = Path(prompt_file)
                    
                if not prompt_path.exists():
                    return jsonify({'error': 'Prompt file not found'}), 404
                
                prompt_data = self.prompt_loader.load_prompt(prompt_path)
                return jsonify({'prompt': prompt_data})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chains/status')
        def api_chains_status():
            """API endpoint to get all chains status."""
            try:
                with self.chain_lock:
                    chains = self.active_chains.copy()
                
                return jsonify({'chains': chains})
                
            except Exception as e:
                return jsonify({'error': f'Failed to get chains status: {str(e)}'}), 500
        
        # Chain Runner Routes
        @self.app.route('/chains')
        def chains_index():
            """Show chain runner interface."""
            return render_template('chains.html')
        
        @self.app.route('/chains/create')
        def chains_create():
            """Show chain creation form."""
            # Get available prompts for selection
            prompts = self._get_available_prompts()
            configs = self._get_available_configs()
            return render_template('chain_create.html', prompts=prompts, configs=configs)
        
        @self.app.route('/chains/upload_config', methods=['POST'])
        def chains_upload_config():
            """Upload chain configuration file."""
            try:
                if 'config_file' not in request.files:
                    return jsonify({'error': 'No configuration file provided'}), 400
                
                config_file = request.files['config_file']
                if config_file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                if not config_file.filename.endswith(('.yaml', '.yml')):
                    return jsonify({'error': 'Configuration file must be YAML format'}), 400
                
                # Save uploaded config temporarily
                filename = secure_filename(config_file.filename)
                config_path = Path(tempfile.gettempdir()) / f"chain_config_{uuid.uuid4().hex}_{filename}"
                config_file.save(str(config_path))
                
                # Validate configuration
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                    self._validate_chain_config(config_data)
                except Exception as e:
                    config_path.unlink()  # Clean up
                    return jsonify({'error': f'Invalid configuration: {str(e)}'}), 400
                
                return jsonify({
                    'success': True,
                    'config_path': str(config_path),
                    'config_data': config_data
                })
                
            except Exception as e:
                return jsonify({'error': f'Upload failed: {str(e)}'}), 500
        
        @self.app.route('/chains/start', methods=['POST'])
        def chains_start():
            """Start a new chain execution."""
            try:
                data = request.get_json()
                
                # Generate unique chain ID
                chain_id = str(uuid.uuid4())
                
                # Get required parameters
                config_path = data.get('config_path')
                input_file = data.get('input_file')
                output_file = data.get('output_file')
                
                if not all([config_path, input_file]):
                    return jsonify({'error': 'Missing required parameters'}), 400
                
                # Create chain info
                chain_info = {
                    'id': chain_id,
                    'status': 'starting',
                    'progress': 0,
                    'total_prompts': 0,
                    'current_prompt': 0,
                    'started_at': datetime.now().isoformat(),
                    'config_path': config_path,
                    'input_file': input_file,
                    'output_file': output_file,
                    'log_file': None,
                    'temp_dir': None,
                    'error': None,
                    'results': []
                }
                
                # Store chain info
                with self.chain_lock:
                    self.active_chains[chain_id] = chain_info
                
                # Start chain execution in background thread
                thread = threading.Thread(
                    target=self._execute_chain,
                    args=(chain_id,),
                    daemon=True
                )
                thread.start()
                
                return jsonify({
                    'success': True,
                    'chain_id': chain_id,
                    'message': 'Chain execution started'
                })
                
            except Exception as e:
                logging.error(f"Failed to start chain: {e}")
                return jsonify({'error': f'Failed to start chain: {str(e)}'}), 500
        
        @self.app.route('/chains/status/<chain_id>')
        def chains_status(chain_id):
            """Get status of a running chain."""
            try:
                with self.chain_lock:
                    if chain_id not in self.active_chains:
                        return jsonify({'error': 'Chain not found'}), 404
                    
                    chain_info = self.active_chains[chain_id].copy()
                
                return jsonify(chain_info)
                
            except Exception as e:
                return jsonify({'error': f'Failed to get status: {str(e)}'}), 500
        
        @self.app.route('/chains/logs/<chain_id>')
        def chains_logs(chain_id):
            """Get logs for a running chain."""
            try:
                with self.chain_lock:
                    if chain_id not in self.active_chains:
                        return jsonify({'error': 'Chain not found'}), 404
                    
                    chain_info = self.active_chains[chain_id]
                    log_file = chain_info.get('log_file')
                
                if not log_file or not Path(log_file).exists():
                    return jsonify({'logs': 'No logs available yet'})
                
                # Read recent log entries (last 100 lines)
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        logs = ''.join(recent_lines)
                except Exception as e:
                    logs = f"Error reading logs: {e}"
                
                return jsonify({'logs': logs})
                
            except Exception as e:
                return jsonify({'error': f'Failed to get logs: {str(e)}'}), 500
        
        @self.app.route('/chains/stop/<chain_id>', methods=['POST'])
        def chains_stop(chain_id):
            """Stop a running chain."""
            try:
                with self.chain_lock:
                    if chain_id not in self.active_chains:
                        return jsonify({'error': 'Chain not found'}), 404
                    
                    chain_info = self.active_chains[chain_id]
                    if chain_info['status'] in ['completed', 'failed', 'stopped']:
                        return jsonify({'error': 'Chain is not running'}), 400
                    
                    # Mark as stopping
                    chain_info['status'] = 'stopping'
                    chain_info['stop_requested'] = True
                
                return jsonify({'success': True, 'message': 'Stop requested'})
                
            except Exception as e:
                return jsonify({'error': f'Failed to stop chain: {str(e)}'}), 500
        
        @self.app.route('/chains/delete/<chain_id>', methods=['POST'])
        def chains_delete(chain_id):
            """Delete a chain and clean up its files."""
            try:
                with self.chain_lock:
                    if chain_id not in self.active_chains:
                        return jsonify({'error': 'Chain not found'}), 404
                    
                    chain_info = self.active_chains[chain_id]
                    
                    # Clean up temporary files
                    self._cleanup_chain_files(chain_info)
                    
                    # Remove from active chains
                    del self.active_chains[chain_id]
                
                return jsonify({'success': True, 'message': 'Chain deleted'})
                
            except Exception as e:
                return jsonify({'error': f'Failed to delete chain: {str(e)}'}), 500
        
        @self.app.route('/chains/download/<chain_id>')
        def chains_download(chain_id):
            """Download results from a completed chain."""
            try:
                with self.chain_lock:
                    if chain_id not in self.active_chains:
                        return jsonify({'error': 'Chain not found'}), 404
                    
                    chain_info = self.active_chains[chain_id]
                
                if chain_info['status'] != 'completed':
                    return jsonify({'error': 'Chain not completed yet'}), 400
                
                output_file = chain_info.get('output_file')
                if not output_file or not Path(output_file).exists():
                    return jsonify({'error': 'Output file not found'}), 404
                
                return send_file(
                    output_file,
                    as_attachment=True,
                    download_name=f"chain_result_{chain_id[:8]}.md"
                )
                
            except Exception as e:
                return jsonify({'error': f'Failed to download results: {str(e)}'}), 500

        @self.app.route('/shutdown', methods=['POST'])
        def shutdown_server():
            """Shutdown the Flask development server."""
            try:
                # Only allow shutdown in development mode or if explicitly enabled
                import os
                if not os.environ.get('FLASK_ENV') == 'development' and not os.environ.get('ALLOW_SHUTDOWN') == 'true':
                    return jsonify({'error': 'Server shutdown not allowed in production mode'}), 403
                
                logging.info("Server shutdown requested via web interface")
                
                # Use werkzeug's shutdown function
                from flask import request
                func = request.environ.get('werkzeug.server.shutdown')
                if func is None:
                    # Alternative shutdown method for different WSGI servers
                    import threading
                    import time
                    
                    def delayed_shutdown():
                        time.sleep(1)
                        import os
                        os._exit(0)
                    
                    thread = threading.Thread(target=delayed_shutdown)
                    thread.daemon = True
                    thread.start()
                    
                    return jsonify({'message': 'Server shutting down...'}), 200
                else:
                    func()
                    return jsonify({'message': 'Server shutting down...'}), 200
                    
            except Exception as e:
                logging.error(f"Error during shutdown: {e}")
                return jsonify({'error': f'Shutdown failed: {str(e)}'}), 500

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
    
    def _get_available_prompts(self) -> List[Dict[str, Any]]:
        """Get list of available prompt files."""
        prompts = []
        prompt_dir = Path("prompts")
        
        if prompt_dir.exists():
            for prompt_file in prompt_dir.glob("*.json"):
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        prompt_data = json.load(f)
                    
                    prompts.append({
                        'file': str(prompt_file),
                        'name': prompt_file.stem.replace('_', ' ').title(),
                        'description': prompt_data.get('instruction', 'No description')[:100]
                    })
                except Exception as e:
                    logging.warning(f"Could not load prompt {prompt_file}: {e}")
        
        return sorted(prompts, key=lambda x: x['name'])
    
    def _get_available_configs(self) -> List[Dict[str, Any]]:
        """Get list of available configuration files."""
        configs = []
        config_dir = Path("config")
        
        if config_dir.exists():
            for config_file in config_dir.glob("*.yaml"):
                configs.append({
                    'file': str(config_file),
                    'name': config_file.stem.replace('_', ' ').title()
                })
        
        return sorted(configs, key=lambda x: x['name'])
    
    def _validate_chain_config(self, config_data: Dict[str, Any]):
        """Validate chain configuration data."""
        required_fields = ['prompts']
        
        for field in required_fields:
            if field not in config_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(config_data['prompts'], dict):
            raise ValueError("'prompts' must be a dictionary")
        
        if len(config_data['prompts']) == 0:
            raise ValueError("At least one prompt must be specified")
        
        # Validate each prompt entry
        for prompt_name, prompt_config in config_data['prompts'].items():
            if isinstance(prompt_config, str):
                # Simple format: prompt_name: "prompt_file.json"
                continue
            elif isinstance(prompt_config, dict):
                # Complex format with config file
                if 'prompt_file' not in prompt_config:
                    raise ValueError(f"Missing 'prompt_file' for prompt '{prompt_name}'")
            else:
                raise ValueError(f"Invalid format for prompt '{prompt_name}'")
    
    def _execute_chain(self, chain_id: str):
        """Execute a chain in the background."""
        try:
            with self.chain_lock:
                chain_info = self.active_chains[chain_id]
            
            # Update status
            with self.chain_lock:
                chain_info['status'] = 'running'
            
            # Create temporary input file if needed
            input_file = chain_info['input_file']
            if not Path(input_file).exists():
                # Assume it's content, create temp file
                temp_input = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
                temp_input.write(input_file)  # input_file contains content
                temp_input.flush()
                temp_input.close()
                input_file = temp_input.name
                
                with self.chain_lock:
                    chain_info['temp_input_file'] = input_file
            
            # Initialize chain runner with subprocess approach for better control
            success = self._run_chain_subprocess(chain_info, input_file)
            
            # Update final status
            with self.chain_lock:
                if success:
                    chain_info['status'] = 'completed'
                    chain_info['completed_at'] = datetime.now().isoformat()
                    chain_info['progress'] = 100
                else:
                    chain_info['status'] = 'failed'
                    chain_info['failed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            logging.error(f"Chain {chain_id} failed: {e}")
            with self.chain_lock:
                chain_info = self.active_chains.get(chain_id, {})
                chain_info['status'] = 'failed'
                chain_info['error'] = str(e)
                chain_info['failed_at'] = datetime.now().isoformat()
    
    def _run_chain_subprocess(self, chain_info: Dict[str, Any], input_file: str) -> bool:
        """Run chain using subprocess for better control and monitoring."""
        try:
            # Build command
            cmd = [
                'python', '-m', 'openrouter_interface.chain',
                '-c', chain_info['config_path'],
                '-i', input_file
            ]
            
            if chain_info.get('output_file'):
                cmd.extend(['-o', chain_info['output_file']])
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor process and track progress
            chain_id = chain_info['id']
            while process.poll() is None:
                # Check for stop request
                with self.chain_lock:
                    if chain_info.get('stop_requested'):
                        process.terminate()
                        time.sleep(1)
                        if process.poll() is None:
                            process.kill()
                        return False
                
                # Update progress by reading log file if available
                self._update_chain_progress_from_logs(chain_info)
                time.sleep(2)  # Check every 2 seconds
            
            # Final progress update
            self._update_chain_progress_from_logs(chain_info)
            
            return process.returncode == 0
            
        except Exception as e:
            logging.error(f"Chain subprocess failed: {e}")
            return False
    
    def _update_chain_progress_from_logs(self, chain_info: Dict[str, Any]):
        """Update chain progress by parsing log files."""
        try:
            log_file = chain_info.get('log_file')
            if not log_file or not Path(log_file).exists():
                return
            
            # Read log file and look for progress indicators
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Look for prompt execution indicators
                current_prompt = 0
                total_prompts = chain_info.get('total_prompts', 0)
                
                for line in lines:
                    if 'Total prompts loaded:' in line:
                        try:
                            total_prompts = int(line.split(':')[-1].strip())
                            chain_info['total_prompts'] = total_prompts
                        except:
                            pass
                    elif 'Processing prompt' in line or 'Step ' in line:
                        try:
                            # Extract step number from log
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part.isdigit() and int(part) > current_prompt:
                                    current_prompt = int(part)
                                    break
                        except:
                            pass
                
                # Update progress
                if total_prompts > 0:
                    progress = min(int((current_prompt / total_prompts) * 100), 99)  # Don't reach 100 until actually complete
                    with self.chain_lock:
                        chain_info['current_prompt'] = current_prompt
                        chain_info['progress'] = progress
                        
            except Exception as e:
                logging.debug(f"Error reading chain logs: {e}")
                
        except Exception as e:
            logging.debug(f"Error updating chain progress: {e}")
    
    def _cleanup_chain_files(self, chain_info: Dict[str, Any]):
        """Clean up temporary files for a chain."""
        try:
            # Clean up temp input file
            temp_input = chain_info.get('temp_input_file')
            if temp_input and Path(temp_input).exists():
                Path(temp_input).unlink()
            
            # Clean up config file (only if it's a temporary one)
            config_path = chain_info.get('config_path')
            if config_path and Path(config_path).exists() and 'chain_config_' in config_path:
                Path(config_path).unlink()
                
            # Note: We don't clean up the temp_dir as it contains useful logs and results
            # Users can manually clean these up or they'll be cleaned by system
            
        except Exception as e:
            logging.warning(f"Error cleaning up chain files: {e}")

    def run(self, host='0.0.0.0', port=5000, debug=False, foreground=False):
        """Run the Flask application."""
        import socket
        import subprocess
        import sys
        
        # Get local IP address
        local_ip = self._get_local_ip()
        
        print(f"🚀 Starting OpenRouter Prompt Runner Web Interface...")
        print(f"📊 Mode: {'Development' if debug else 'Production'}")
        print(f"🌐 Access URLs:")
        print(f"   • Local:    http://127.0.0.1:{port}")
        print(f"   • Network:  http://{local_ip}:{port}")
        print(f"")
        
        if not debug and not foreground:
            print("🔧 Running in background mode...")
            print("   • Web server will continue running after terminal closes")
            print("   • To stop: kill the process or restart your system")
            print("   • Logs will be written to openrouter_web.log")
            print(f"")
            
            # Run in background using nohup
            try:
                # Use the standalone background runner script to avoid import issues
                background_script = os.path.join(os.getcwd(), 'run-flask-background.py')
                
                cmd = [
                    sys.executable, background_script,
                    '--host', host, '--port', str(port)
                ]
                
                # Start the process in background
                with open('openrouter_web.log', 'w') as log_file:
                    process = subprocess.Popen(
                        ['nohup'] + cmd,
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        preexec_fn=os.setsid
                    )
                
                # Give it a moment to start
                import time
                time.sleep(2)
                
                print(f"✅ Web server started successfully!")
                print(f"📝 Process ID: {process.pid}")
                print(f"📄 Logs: openrouter_web.log")
                print(f"")
                print("🌐 Open your browser and navigate to:")
                print(f"   http://{local_ip}:{port}")
                
                return
                
            except Exception as e:
                print(f"❌ Failed to start in background mode: {e}")
                print("🔄 Falling back to foreground mode...")
                
        print("Press Ctrl+C to stop the server")
        print("="*50)
        self.app.run(host=host, port=port, debug=debug)
    
    def _get_local_ip(self):
        """Get the local IP address."""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"


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
        default='0.0.0.0',
        help='Host to bind the server to (default: 0.0.0.0 - all interfaces)'
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
        help='Run in debug mode (default: production mode)'
    )
    
    parser.add_argument(
        '--foreground',
        action='store_true',
        help='Run in foreground mode (default: background in production)'
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
        flask_runner.run(host=args.host, port=args.port, debug=args.debug, foreground=args.foreground)
        
    except Exception as e:
        logging.error(f"Failed to start Flask application: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())