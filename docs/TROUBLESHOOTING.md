# Troubleshooting Guide

Common issues and solutions for OpenRouter Interface. This guide covers problems fixed in recent updates and ongoing troubleshooting.

## 🔧 Installation Issues

### "No prompts configured" - Web Interface Shows Empty

**Problem**: Web interface displays "No prompts configured" even though prompt files exist.

**Fixed in latest version**: This was caused by a mismatch between the prompts registry format and the display code.

**Solution**: 
1. Update to latest version
2. Go to the Prompts Registry page (`/prompts_registry`)
3. Click "Rescan Directory for JSON Files"
4. Return to home page - prompts should now display

**Root cause fixed**: The web interface now correctly reads from the prompts registry YAML format.

### "openrouter-web command not found"

**Problem**: CLI entry points not working after installation.

**Fixed in latest version**: Added proper setup.py with correct entry point configuration.

**Solutions**:
1. **Use the new global installer**: `./install-global.sh` 
2. **Or use the wrapper scripts**: `./openrouter-runner`, `./openrouter-chain`
3. **Or run directly with PYTHONPATH**: `PYTHONPATH=src python3 -m openrouter_interface.cli`

### "build_editable hook missing" Error

**Problem**: `pip install -e .` fails with build backend error.

**Fixed in latest version**: Updated pyproject.toml and added setup.py for better compatibility.

**Solutions**:
1. **Use global installer**: `./install-global.sh` (recommended)
2. **Use regular install**: `pip install .` (not editable)
3. **Use wrapper scripts**: Provided as fallback

## 🌐 Web Interface Issues

### Web Server Won't Start

**Problem**: Flask server fails to start with module not found errors.

**Solution**:
```bash
# Use the updated start script
./start-web.sh --debug

# Or run directly with PYTHONPATH
PYTHONPATH=src python3 -m openrouter_interface.web --debug --foreground
```

**Fixed in latest version**: start-web.sh now properly sets PYTHONPATH.

### Prompts Not Loading in Web Interface

**Fixed in latest version**: Complete rewrite of the prompts loading system.

**What was fixed**:
- Prompts registry format now correctly matches display code
- File path resolution fixed for different installation types
- Template URLs now use correct relative paths

**Manual fix if needed**:
1. Visit `/prompts_registry`
2. Click "Rescan Directory"
3. Verify prompts show "enabled: true"
4. Return to home page

### "Romance Editor" JSON Error

**Problem**: One prompt file has JSON syntax errors.

**Solution**: 
```bash
# Find and fix the JSON error
python3 -m json.tool prompts/romance_editor.json
```

**Status**: This file is automatically disabled in the registry when JSON errors are detected.

## 💻 CLI Issues

### Commands Don't Work from Other Directories

**Fixed in latest version**: Added global installation option.

**Solutions**:
1. **Global install**: `./install-global.sh` - then use from anywhere
2. **Use absolute paths**: `openrouter-runner -p /full/path/to/prompt.json`
3. **Local wrapper scripts**: Use `./openrouter-runner` from project directory

### "Cannot find config file" Error

**Problem**: CLI tools can't find default config files when run from other directories.

**Solutions**:
1. **Specify config explicitly**: `-c /full/path/to/config.yaml`
2. **Create local config**: Copy config files to your working directory
3. **Use project directory**: Run from the OpenRouter-Interface directory

## 🔗 API and Networking Issues

### "API key not found" Error

**Solutions**:
```bash
# Set for current session
export OPENROUTER_API_KEY='your-key-here'

# Set permanently
echo 'export OPENROUTER_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc

# Verify it's set
echo $OPENROUTER_API_KEY
```

### Web Interface Not Accessible from Other Devices

**Problem**: Can't access from phones/tablets on network.

**Solutions**:
1. **Check firewall**: `sudo ufw allow 5000`
2. **Find your IP**: `ip addr show | grep inet`
3. **Use network IP**: `http://192.168.x.x:5000` (not localhost)
4. **Start with network binding**: The web interface already binds to `0.0.0.0`

## 📦 Package and Dependency Issues

### "UNKNOWN-0.0.0" Package Version

**Fixed in latest version**: Corrected pyproject.toml configuration.

**What was fixed**:
- Removed conflicting `dynamic = []` setting
- Updated build backend configuration
- Added proper setup.py with correct versioning

### Missing Dependencies

**Problem**: ImportError for requests, PyYAML, or Flask.

**Solution**:
```bash
# Global install includes all dependencies
./install-global.sh

# Or manual install
pip3 install requests PyYAML flask werkzeug
```

## 🔍 Debug Mode

### Enable Detailed Logging

**For CLI**:
```bash
openrouter-runner -p prompt.json -i input.md -v -l debug.log
```

**For Web Interface**:
```bash
./start-web.sh --debug
```

**For Chain Runner**:
```bash
openrouter-chain -c config.yaml --debug
```

## 📂 File and Path Issues

### "File not found" Errors

**Common causes**:
1. **Working directory confusion**: Global vs local install paths
2. **Relative vs absolute paths**: Use full paths with global install
3. **Missing prompt files**: Check that JSON files exist and are valid

**Solutions**:
```bash
# Verify files exist
ls -la prompts/
ls -la your-input-file.md

# Use absolute paths with global install
openrouter-runner -p /full/path/to/prompt.json -i /full/path/to/input.md

# Or use from project directory with relative paths
cd /path/to/OpenRouter-Interface
./openrouter-runner -p prompts/prompt.json -i input.md
```

## 🔧 Recovery Steps

### Complete Reset

If nothing else works:

```bash
# 1. Clean up any broken installations
pip3 uninstall openrouter-interface -y

# 2. Fresh clone (if needed)
git pull  # or git clone again

# 3. Use the working global installer
./install-global.sh

# 4. Test basic functionality
openrouter-runner --help
openrouter-chain --help
```

### Verify Installation

```bash
# Check commands are available
which openrouter-runner
which openrouter-chain

# Test help systems
openrouter-runner --help
openrouter-chain --help

# Test web interface
openrouter-web --help
```

## 📋 Getting Help

When reporting issues, please include:

1. **Installation method used**: Global vs local vs manual
2. **Command executed**: Full command line
3. **Working directory**: Where you ran the command
4. **Error output**: Complete error message
5. **Environment**: OS, Python version, pip version

**Logs locations**:
- CLI: `openrouter_editor.log` (in current directory)
- Web: Console output (when using `--debug --foreground`)
- Chain: Temp directory logs (shown in output)

## 🎯 Quick Fixes Summary

**Most common issues and their fixes**:

1. **Web prompts not showing**: Visit `/prompts_registry` and rescan
2. **CLI not global**: Use `./install-global.sh` 
3. **Commands not found**: Use wrapper scripts or set PYTHONPATH
4. **API key missing**: Set environment variable permanently
5. **Web not accessible**: Check firewall and use network IP
6. **JSON errors**: Validate with `python3 -m json.tool file.json`
7. **File not found**: Use absolute paths with global install