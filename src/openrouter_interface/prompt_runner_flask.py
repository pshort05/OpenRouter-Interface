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
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from flask import Response, make_response

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
        logging.info("INIT DEBUG: Starting Flask initialization")
        
        # Set template folder to the project root's templates folder
        self.project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        self.project_root_abs = os.path.abspath(self.project_root)
        logging.info(f"INIT DEBUG: Project root calculated as: {self.project_root}")
        logging.info(f"INIT DEBUG: Project root absolute: {self.project_root_abs}")
        
        template_folder = os.path.join(self.project_root, 'templates')
        template_folder_abs = os.path.abspath(template_folder)
        logging.info(f"INIT DEBUG: Template folder: {template_folder_abs}")
        
        self.app = Flask(__name__, template_folder=template_folder)
        self.app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')
        
        # Configure upload settings
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        self.app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
        
        # Configuration file paths - look in parent directory (project root)
        self.config_file = os.path.join(self.project_root, 'flask_config.yaml')
        self.config_file_abs = os.path.abspath(self.config_file)
        
        print(f"STARTUP PATH DEBUG: Config file path set to: {self.config_file}")
        print(f"STARTUP PATH DEBUG: Config file absolute path: {self.config_file_abs}")
        print(f"STARTUP PATH DEBUG: Project root is: {self.project_root}")
        print(f"STARTUP PATH DEBUG: Project root absolute: {self.project_root_abs}")
        print(f"STARTUP PATH DEBUG: Current working directory: {os.getcwd()}")
        print(f"STARTUP PATH DEBUG: __file__ location: {__file__}")
        print(f"STARTUP PATH DEBUG: __file__ dirname: {os.path.dirname(os.path.abspath(__file__))}")
        print(f"STARTUP PATH DEBUG: Config file exists: {os.path.exists(self.config_file_abs)}")
        
        logging.info(f"STARTUP PATH DEBUG: Config file path set to: {self.config_file}")
        logging.info(f"STARTUP PATH DEBUG: Config file absolute path: {self.config_file_abs}")
        logging.info(f"STARTUP PATH DEBUG: Project root is: {self.project_root}")
        logging.info(f"STARTUP PATH DEBUG: Project root absolute: {self.project_root_abs}")
        logging.info(f"STARTUP PATH DEBUG: Current working directory: {os.getcwd()}")
        logging.info(f"STARTUP PATH DEBUG: Config file exists: {os.path.exists(self.config_file_abs)}")
        
        self.prompts_registry_file = os.path.join(self.project_root, 'prompts_registry.yaml')
        self.prompts_registry_file_abs = os.path.abspath(self.prompts_registry_file)
        logging.info(f"STARTUP PATH DEBUG: Prompts registry file: {self.prompts_registry_file_abs}")
        print(f"STARTUP PATH DEBUG: Prompts registry file: {self.prompts_registry_file_abs}")
        
        # Model cache setup
        self.cache_dir = os.path.join(self.project_root, 'cache')
        self.cache_dir_abs = os.path.abspath(self.cache_dir)
        self.models_cache_file = os.path.join(self.cache_dir, 'openrouter_models.json')
        self.models_cache_file_abs = os.path.abspath(self.models_cache_file)
        
        print(f"STARTUP PATH DEBUG: Cache directory: {self.cache_dir_abs}")
        print(f"STARTUP PATH DEBUG: Models cache file: {self.models_cache_file_abs}")
        logging.info(f"STARTUP PATH DEBUG: Cache directory: {self.cache_dir_abs}")
        logging.info(f"STARTUP PATH DEBUG: Models cache file: {self.models_cache_file_abs}")
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
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
        
        absolute_path = config_path.absolute()
        logging.info(f"LOAD CONFIG PATH DEBUG: Loading from path: {self.config_file}")
        logging.info(f"LOAD CONFIG PATH DEBUG: Absolute path: {absolute_path}")
        logging.info(f"LOAD CONFIG PATH DEBUG: Path exists: {config_path.exists()}")
        logging.info(f"LOAD CONFIG PATH DEBUG: Current working directory: {os.getcwd()}")
        logging.info(f"LOAD CONFIG PATH DEBUG: Path parent directory: {config_path.parent}")
        logging.info(f"LOAD CONFIG PATH DEBUG: Path parent exists: {config_path.parent.exists()}")
        logging.info(f"LOAD CONFIG PATH DEBUG: Path is file: {config_path.is_file()}")
        logging.info(f"LOAD CONFIG PATH DEBUG: Path is readable: {os.access(str(config_path), os.R_OK) if config_path.exists() else False}")
        
        print(f"LOAD CONFIG PATH DEBUG: Loading from path: {self.config_file}")
        print(f"LOAD CONFIG PATH DEBUG: Absolute path: {absolute_path}")
        print(f"LOAD CONFIG PATH DEBUG: Path exists: {config_path.exists()}")
        print(f"LOAD CONFIG PATH DEBUG: Current working directory: {os.getcwd()}")
        print(f"LOAD CONFIG PATH DEBUG: Path parent directory: {config_path.parent}")
        print(f"LOAD CONFIG PATH DEBUG: Path parent exists: {config_path.parent.exists()}")
        print(f"LOAD CONFIG PATH DEBUG: Path is file: {config_path.is_file()}")
        print(f"LOAD CONFIG PATH DEBUG: Path is readable: {os.access(str(config_path), os.R_OK) if config_path.exists() else False}")
        print(f"LOAD CONFIG: Loading from {absolute_path}")
        
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
            print(f"LOADING CONFIG from {self.config_file}")
            with open(config_path, 'r', encoding='utf-8') as f:
                file_contents = f.read()
                print(f"CONFIG FILE CONTENTS:\n{file_contents}")
                f.seek(0)  # Reset file pointer
                user_config = yaml.safe_load(f) or {}
            logging.info(f"Loaded config contains model: {user_config.get('model', 'NOT SET')}")
            print(f"PARSED CONFIG MODEL: {user_config.get('model', 'NOT SET')}")
            logging.debug(f"Full loaded user config: {user_config}")
            default_config.update(user_config)
            logging.info(f"Final merged config model: {default_config.get('model', 'NOT SET')}")
            print(f"FINAL CONFIG MODEL: {default_config.get('model', 'NOT SET')}")
        else:
            logging.info(f"Configuration file {self.config_file} not found, using defaults")
            self._save_flask_config(default_config)
            
        return default_config
    
    def _save_flask_config(self, config: Dict[str, Any]):
        """Save Flask configuration to YAML file."""
        config_path = Path(self.config_file)
        absolute_path = config_path.absolute()
        
        logging.info(f"SAVE CONFIG DEBUG: Saving to path: {self.config_file}")
        logging.info(f"SAVE CONFIG DEBUG: Absolute path: {absolute_path}")
        logging.info(f"SAVE CONFIG DEBUG: Path exists: {config_path.exists()}")
        logging.info(f"SAVE CONFIG DEBUG: Parent directory exists: {config_path.parent.exists()}")
        logging.info(f"SAVE CONFIG DEBUG: Parent directory path: {config_path.parent}")
        logging.debug(f"SAVE CONFIG DEBUG: Config data to save: {config}")
        print(f"SAVE CONFIG: Saving to {absolute_path}")
        print(f"SAVE CONFIG: Data = {config}")
        print(f"SAVE CONFIG: Parent directory = {config_path.parent}")
        print(f"SAVE CONFIG: Parent exists = {config_path.parent.exists()}")
        print(f"SAVE CONFIG: File writable = {os.access(config_path.parent, os.W_OK)}")
        
        # Check if directory exists and create if needed
        if not config_path.parent.exists():
            logging.info(f"Creating parent directory: {config_path.parent}")
            print(f"Creating parent directory: {config_path.parent}")
            config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Test write permissions first
            test_file = config_path.parent / f".test_write_{uuid.uuid4().hex[:8]}"
            try:
                with open(test_file, 'w') as tf:
                    tf.write("test")
                test_file.unlink()
                print("SAVE CONFIG: Write permissions verified")
            except Exception as perm_error:
                logging.error(f"SAVE CONFIG: Permission test failed: {perm_error}")
                print(f"SAVE CONFIG: Permission test failed: {perm_error}")
                raise Exception(f"No write permission to directory {config_path.parent}: {perm_error}")
            
            # Read current file to compare before writing
            old_content = None
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                        print(f"SAVE CONFIG: Old file content:\n{old_content}")
                except Exception as read_error:
                    logging.warning(f"Could not read old config file: {read_error}")
                    print(f"SAVE CONFIG: Could not read old config file: {read_error}")
            
            # Write new config
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=True)
            
            # Verify write by reading back
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    new_content = f.read()
                    print(f"SAVE CONFIG: New file content:\n{new_content}")
                    
                # Parse to verify YAML is valid
                parsed = yaml.safe_load(new_content)
                expected_model = config.get('model', 'NOT SET')
                actual_model = parsed.get('model', 'NOT SET')
                print(f"SAVE CONFIG: Expected model: {expected_model}")
                print(f"SAVE CONFIG: Actual model in saved file: {actual_model}")
                
                if actual_model != expected_model:
                    raise Exception(f"Verification failed: expected model '{expected_model}' but file contains '{actual_model}'")
                    
            except Exception as verify_error:
                logging.error(f"SAVE CONFIG: Verification failed: {verify_error}")
                print(f"SAVE CONFIG: Verification failed: {verify_error}")
                raise
                
            logging.info(f"SAVE CONFIG DEBUG: Successfully saved to {absolute_path}")
            print(f"SAVE CONFIG: Successfully saved to {absolute_path}")
        except Exception as e:
            logging.error(f"SAVE CONFIG DEBUG: Failed to save to {absolute_path}: {e}")
            print(f"SAVE CONFIG ERROR: Failed to save to {absolute_path}: {e}")
            raise
    
    def _reload_configuration(self):
        """Reload configuration and reinitialize components."""
        logging.info("Reloading configuration...")
        old_model = self.flask_config.get('model', 'NOT SET')
        self.flask_config = self._load_flask_config()
        new_model = self.flask_config.get('model', 'NOT SET')
        logging.info(f"Configuration reloaded. Model changed from '{old_model}' to '{new_model}'")
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
            try:
                logging.info("CONFIG PAGE: Loading configuration page")
                logging.info(f"CONFIG PAGE PATH: Config file path: {self.config_file}")
                logging.info(f"CONFIG PAGE PATH: Config file absolute path: {self.config_file_abs}")
                logging.info(f"CONFIG PAGE PATH: Config file exists: {os.path.exists(self.config_file_abs)}")
                logging.info(f"CONFIG PAGE PATH: Current working directory: {os.getcwd()}")
                
                print(f"CONFIG PAGE PATH DEBUG: Config file path: {self.config_file}")
                print(f"CONFIG PAGE PATH DEBUG: Config file absolute path: {self.config_file_abs}")
                print(f"CONFIG PAGE PATH DEBUG: Config file exists: {os.path.exists(self.config_file_abs)}")
                print(f"CONFIG PAGE PATH DEBUG: Current working directory: {os.getcwd()}")
                
                logging.debug(f"Current model in config: {self.flask_config.get('model', 'NOT SET')}")
                
                # Get available models (cached if available)
                models = self._get_available_models()
                model_count = len(models)
                
                # Get cache info
                cache_info = None
                if os.path.exists(self.models_cache_file):
                    cache_time = datetime.fromtimestamp(os.path.getmtime(self.models_cache_file))
                    cache_age_days = (datetime.now() - cache_time).days
                    cache_info = {
                        'last_updated': cache_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'age_days': cache_age_days,
                        'is_stale': cache_age_days >= 7
                    }
                
                # Get current config file info for debugging
                config_file_exists = os.path.exists(self.config_file)
                config_file_contents = None
                
                logging.info(f"CONFIG PAGE PATH: Checking file existence at: {self.config_file}")
                logging.info(f"CONFIG PAGE PATH: File exists check result: {config_file_exists}")
                print(f"CONFIG PAGE PATH DEBUG: Checking file existence at: {self.config_file}")
                print(f"CONFIG PAGE PATH DEBUG: File exists check result: {config_file_exists}")
                
                if config_file_exists:
                    try:
                        logging.info(f"CONFIG PAGE PATH: Reading config file from: {self.config_file}")
                        print(f"CONFIG PAGE PATH DEBUG: Reading config file from: {self.config_file}")
                        with open(self.config_file, 'r', encoding='utf-8') as f:
                            config_file_contents = f.read()
                        logging.info(f"CONFIG PAGE PATH: Successfully read {len(config_file_contents)} characters from config file")
                        print(f"CONFIG PAGE PATH DEBUG: Successfully read {len(config_file_contents)} characters from config file")
                    except Exception as e:
                        logging.error(f"CONFIG PAGE PATH: Could not read config file for display: {e}")
                        print(f"CONFIG PAGE PATH ERROR: Could not read config file for display: {e}")
                else:
                    logging.warning(f"CONFIG PAGE PATH: Config file does not exist at: {self.config_file}")
                    print(f"CONFIG PAGE PATH WARNING: Config file does not exist at: {self.config_file}")
                
                logging.info(f"Rendering config page with {model_count} models, current model: {self.flask_config.get('model', 'NOT SET')}")
                
                return render_template('config.html', 
                                     config=self.flask_config, 
                                     models=models,
                                     model_count=model_count,
                                     cache_info=cache_info,
                                     config_file_path=self.config_file,
                                     config_file_exists=config_file_exists,
                                     config_file_contents=config_file_contents)
                                     
            except Exception as e:
                logging.error(f"Error loading models for config: {e}")
                flash(f'Warning: Could not load models - {str(e)}', 'warning')
                return render_template('config.html', 
                                     config=self.flask_config, 
                                     models=[],
                                     model_count=0,
                                     cache_info=None)
        
        @self.app.route('/config', methods=['POST'])
        def update_config():
            """Update configuration."""
            try:
                logging.info("ROUTE DEBUG: /config POST route hit")
                logging.info("Processing configuration update request")
                logging.info(f"SAVE OPERATION PATH: Config file to save: {self.config_file}")
                logging.info(f"SAVE OPERATION PATH: Config file absolute: {self.config_file_abs}")
                logging.info(f"SAVE OPERATION PATH: Config file exists: {os.path.exists(self.config_file_abs)}")
                logging.info(f"SAVE OPERATION PATH: Current working directory: {os.getcwd()}")
                
                print("FORM UPDATE: Processing configuration update request")
                print(f"SAVE OPERATION PATH DEBUG: Config file to save: {self.config_file}")
                print(f"SAVE OPERATION PATH DEBUG: Config file absolute: {self.config_file_abs}")
                print(f"SAVE OPERATION PATH DEBUG: Config file exists: {os.path.exists(self.config_file_abs)}")
                print(f"SAVE OPERATION PATH DEBUG: Current working directory: {os.getcwd()}")
                print(f"ROUTE DEBUG: Request method = {request.method}")
                print(f"ROUTE DEBUG: Request URL = {request.url}")
                print(f"ROUTE DEBUG: Request headers = {dict(request.headers)}")
                print(f"ROUTE DEBUG: Content type = {request.content_type}")
                print(f"ROUTE DEBUG: Content length = {request.content_length}")
                
                # Log all form data for debugging
                logging.info(f"Form data received: {dict(request.form)}")
                print(f"FORM DATA: {dict(request.form)}")
                print(f"FORM DATA KEYS: {list(request.form.keys())}")
                print(f"FORM DATA LENGTH: {len(request.form)}")
                
                # Check if form is empty
                if not request.form:
                    logging.error("ERROR: No form data received!")
                    print("ERROR: No form data received!")
                    flash('No form data received. Please check your browser settings and try again.', 'error')
                    return redirect(url_for('show_config'))
                
                # Get form data
                new_config = {}
                
                # String fields
                string_fields = ['model', 'api_base_url', 'log_level', 'payload_file']
                for field in string_fields:
                    value = request.form.get(field, '').strip()
                    if value:
                        new_config[field] = value
                        logging.debug(f"Config field {field}: {value}")
                        print(f"FORM FIELD {field}: {value}")
                
                # Log the model change specifically
                old_model = self.flask_config.get('model', 'NOT SET')
                new_model = new_config.get('model', 'NOT CHANGED')
                logging.info(f"Model change: '{old_model}' -> '{new_model}'")
                print(f"MODEL CHANGE: '{old_model}' -> '{new_model}'")
                
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
                
                # Validate selected model (optional but helpful)
                if 'model' in new_config:
                    try:
                        available_models = self._get_available_models()
                        model_ids = [model['id'] for model in available_models]
                        if model_ids and new_config['model'] not in model_ids:
                            flash(f'Warning: Selected model "{new_config["model"]}" not found in available models. You may need to refresh the model cache.', 'warning')
                    except Exception as e:
                        logging.warning(f"Could not validate model selection: {e}")
                
                # Update and save configuration
                logging.info(f"Updating flask_config with new values: {list(new_config.keys())}")
                print(f"BEFORE UPDATE: flask_config model = {self.flask_config.get('model', 'NOT SET')}")
                print(f"NEW CONFIG: {new_config}")
                
                self.flask_config.update(new_config)
                print(f"AFTER UPDATE: flask_config model = {self.flask_config.get('model', 'NOT SET')}")
                
                logging.info("Saving configuration to file")
                print("SAVE: About to call _save_flask_config")
                try:
                    self._save_flask_config(self.flask_config)
                    print("SAVE: _save_flask_config completed successfully")
                except Exception as save_error:
                    logging.error(f"SAVE ERROR: {save_error}")
                    print(f"SAVE ERROR: {save_error}")
                    raise
                
                # Reload configuration
                logging.info("Reloading configuration")
                print("RELOAD: About to call _reload_configuration")
                try:
                    self._reload_configuration()
                    print("RELOAD: _reload_configuration completed successfully")
                except Exception as reload_error:
                    logging.error(f"RELOAD ERROR: {reload_error}")
                    print(f"RELOAD ERROR: {reload_error}")
                    raise
                
                # Verify the change was applied
                current_model = self.flask_config.get('model', 'NOT SET')
                logging.info(f"Configuration updated successfully. Current model is now: {current_model}")
                print(f"FINAL VERIFICATION: Current model is now: {current_model}")
                
                # Double-check by reading the file back
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        file_contents = f.read()
                        print(f"FILE VERIFICATION: Config file now contains:\n{file_contents}")
                except Exception as read_error:
                    logging.error(f"FILE READ ERROR: {read_error}")
                    print(f"FILE READ ERROR: {read_error}")
                
                flash('Configuration updated successfully', 'success')
                return redirect(url_for('show_config'))
                
            except Exception as e:
                logging.error(f"Error updating configuration: {e}")
                flash(f"Error updating configuration: {e}", 'error')
                return redirect(url_for('show_config'))
        
        @self.app.route('/config/reset', methods=['POST'])
        def reset_config():
            """Reset configuration to recommended defaults."""
            try:
                logging.info("Resetting configuration to defaults")
                
                # Reset to default configuration with recommended model
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
                
                logging.info("Saving reset configuration")
                self._save_flask_config(default_config)
                
                logging.info("Reloading configuration after reset")
                self._reload_configuration()
                
                current_model = self.flask_config.get('model', 'NOT SET')
                logging.info(f"Configuration reset completed. Model is now: {current_model}")
                
                flash('Configuration reset to defaults successfully', 'success')
                return redirect(url_for('show_config'))
                
            except Exception as e:
                logging.error(f"Error resetting configuration: {e}")
                flash(f"Error resetting configuration: {e}", 'error')
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
                logging.info(f"Loading prompt form for: {prompt_file}")
                
                # If prompt_file is relative (e.g., "prompts/file.json"), resolve it to project root
                if not os.path.isabs(prompt_file):
                    prompt_path = Path(os.path.join(self.project_root, prompt_file))
                else:
                    prompt_path = Path(prompt_file)
                
                logging.debug(f"Resolved prompt path: {prompt_path}")
                
                if not prompt_path.exists():
                    logging.error(f"Prompt file not found: {prompt_path}")
                    flash(f"Prompt file not found: {prompt_file}", 'error')
                    return redirect(url_for('index'))
                
                # Load and validate prompt
                prompt_data = self.prompt_loader.load_prompt(prompt_path)
                logging.debug(f"Current model from config: {self.flask_config.get('model', 'NOT SET')}")
                
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
                
                # Get all available prompts for dropdown
                try:
                    all_prompts = self._load_prompts_registry()
                    available_prompts = [p for p in all_prompts if p.get('enabled', False) and p.get('exists', False)]
                except Exception as e:
                    logging.warning(f"Could not load prompts registry: {e}")
                    available_prompts = []
                
                logging.info(f"Rendering prompt form for: {prompt_info['title']} with model: {self.flask_config.get('model', 'NOT SET')}")
                
                response = make_response(render_template('prompt_form.html', 
                                                       prompt=prompt_info, 
                                                       config=self.flask_config,
                                                       available_prompts=available_prompts))
                # Prevent caching to ensure fresh data
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response
                
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
                system_prompt = request.form.get('system_prompt', '').strip()
                output_format = request.form.get('output_format', 'markdown')
                
                logging.info(f"Executing prompt: {prompt_file}")
                logging.debug(f"Input method: {input_method}, Output format: {output_format}")
                logging.debug(f"System prompt provided: {'Yes' if system_prompt else 'No'}")
                
                if not prompt_file:
                    logging.error("No prompt file specified in form submission")
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
                
                # Create full prompt with system prompt and output format
                full_prompt = self.processor.create_full_prompt(prompt_data, input_content)
                
                # Add system prompt and output format instructions
                full_prompt = self._enhance_prompt_with_system_and_format(
                    full_prompt, system_prompt, output_format)
                
                # Call API
                response = self.api_client.call_api(full_prompt)
                
                # Store response for session history
                response_data = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'prompt_name': prompt_path.name,
                    'input_name': input_name,
                    'response': response,
                    'input_length': len(input_content),
                    'response_length': len(response),
                    'system_prompt': system_prompt if system_prompt else 'None',
                    'output_format': output_format.title()
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
                        'response_length': len(response),
                        'system_prompt': response_data['system_prompt'],
                        'output_format': response_data['output_format']
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

        @self.app.route('/api/models')
        def api_get_models():
            """API endpoint to get available OpenRouter models."""
            try:
                force_refresh = request.args.get('refresh', 'false').lower() == 'true'
                models = self._get_available_models(force_refresh=force_refresh)
                return jsonify({'models': models, 'count': len(models)})
            except Exception as e:
                logging.error(f"Error fetching models: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/refresh_models', methods=['POST'])
        def refresh_models():
            """Refresh the model cache."""
            try:
                models = self._get_available_models(force_refresh=True)
                flash(f'Model cache refreshed! Loaded {len(models)} models from OpenRouter.', 'success')
                return redirect(url_for('show_config'))
            except Exception as e:
                flash(f'Error refreshing models: {str(e)}', 'error')
                return redirect(url_for('show_config'))

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
    
    def _enhance_prompt_with_system_and_format(self, full_prompt: str, system_prompt: str, output_format: str) -> str:
        """Enhance the prompt with system prompt and output format instructions."""
        enhanced_prompt = ""
        
        # Add system prompt if provided
        if system_prompt:
            enhanced_prompt += f"SYSTEM: {system_prompt}\n\n"
        
        # Add output format instructions
        format_instructions = {
            'markdown': "Please format your response in clear, well-structured Markdown with appropriate headers, lists, and formatting for readability.",
            'json': "Please format your response as valid JSON. Use appropriate keys and structure the data logically.",
            'xml': "Please format your response as well-formed XML with appropriate tags and structure.",
            'text': "Please format your response as plain text with clear paragraphs and structure."
        }
        
        if output_format in format_instructions:
            enhanced_prompt += f"OUTPUT FORMAT: {format_instructions[output_format]}\n\n"
        
        # Add the original prompt
        enhanced_prompt += full_prompt
        
        return enhanced_prompt
    
    def _get_cached_models(self) -> Optional[List[Dict[str, Any]]]:
        """Get cached OpenRouter models if cache is valid (less than 7 days old)."""
        try:
            if not os.path.exists(self.models_cache_file):
                return None
                
            # Check cache age
            cache_time = datetime.fromtimestamp(os.path.getmtime(self.models_cache_file))
            if datetime.now() - cache_time > timedelta(days=7):
                logging.info("Model cache is older than 7 days, will refresh")
                return None
                
            # Load cached models
            with open(self.models_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            logging.info(f"Loaded {len(cache_data.get('models', []))} models from cache")
            return cache_data.get('models', [])
            
        except Exception as e:
            logging.warning(f"Error reading model cache: {e}")
            return None
    
    def _fetch_openrouter_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from OpenRouter API."""
        try:
            logging.info("Fetching models from OpenRouter API...")
            
            headers = {
                'Authorization': f'Bearer {os.environ.get("OPENROUTER_API_KEY", "")}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://openrouter.ai/api/v1/models',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            models = data.get('data', [])
            
            # Filter and format models for display
            formatted_models = []
            for model in models:
                # Skip models that are not active or have issues
                if model.get('pricing', {}).get('prompt', 0) == -1:
                    continue
                    
                formatted_models.append({
                    'id': model['id'],
                    'name': model.get('name', model['id']),
                    'description': model.get('description', ''),
                    'context_length': model.get('context_length', 0),
                    'pricing': model.get('pricing', {}),
                    'owned_by': model.get('owned_by', ''),
                    'architecture': model.get('architecture', {})
                })
            
            # Sort by name for better UX
            formatted_models.sort(key=lambda x: x['name'].lower())
            
            # Cache the results
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'models': formatted_models
            }
            
            with open(self.models_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
                
            logging.info(f"Fetched and cached {len(formatted_models)} models from OpenRouter")
            return formatted_models
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error fetching models: {e}")
            raise Exception(f"Failed to fetch models from OpenRouter: {str(e)}")
        except Exception as e:
            logging.error(f"Error fetching models: {e}")
            raise Exception(f"Error processing models: {str(e)}")
    
    def _get_available_models(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get available OpenRouter models, using cache when possible."""
        if not force_refresh:
            cached_models = self._get_cached_models()
            if cached_models is not None:
                return cached_models
        
        # Fetch fresh models if no cache or force refresh
        return self._fetch_openrouter_models()
    
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