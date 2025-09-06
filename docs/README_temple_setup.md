# OpenRouter Prompt Runner Flask App - Template Setup

This document explains how to set up the HTML templates for the refactored Flask application.

## Overview

The Flask application has been refactored to separate HTML templates from the Python code, following Flask best practices. All HTML templates are now stored in separate files in the `templates/` directory.

## Quick Setup

1. **Create templates automatically** (recommended):
   ```bash
   python create_templates.py
   ```

2. **Run the Flask application**:
   ```bash
   python prompt_runner_flask.py
   ```

## Manual Template Setup

If you prefer to create the templates manually, create a `templates/` directory and add the following files:

### Directory Structure
```
project/
├── prompt_runner_flask.py
├── create_templates.py
└── templates/
    ├── base.html
    ├── index.html
    ├── prompt_form.html
    └── history.html
```

### Template Files

#### 1. `templates/base.html`
Base template with shared layout, navigation, and CSS styling. Contains:
- Responsive design with modern CSS
- Navigation bar with Home and History links
- Flash message display
- Loading spinner animations
- Common styling for forms, buttons, and alerts

#### 2. `templates/index.html`
Main page template that:
- Extends base.html
- Displays available JSON prompt files in a grid layout
- Shows file metadata (name, size)
- Provides "Use This Prompt" buttons for each prompt
- Shows helpful message when no prompts are found

#### 3. `templates/prompt_form.html`
Prompt execution form template that:
- Extends base.html
- Shows prompt metadata and details
- Provides input method selection (text or file upload)
- Handles form submission via JavaScript
- Displays loading spinner during API calls
- Shows response results with metadata

#### 4. `templates/history.html`
Session history display template that:
- Extends base.html
- Shows all responses from the current session
- Provides download and clear history functionality
- Displays response metadata and content
- Handles empty history state

## Features

### Responsive Design
- Mobile-friendly layout
- Grid-based prompt listing
- Flexible form layouts

### Interactive Elements
- AJAX form submission
- Loading indicators
- Input method toggling
- Confirmation dialogs

### User Experience
- Flash messages for feedback
- Proper error handling
- Intuitive navigation
- Clean, modern styling

## Customization

You can customize the appearance by modifying the CSS in `templates/base.html`. The styling uses:
- CSS Grid for layouts
- Flexbox for component alignment
- CSS animations for interactions
- Semantic color scheme
- Responsive breakpoints

## Benefits of This Refactor

1. **Separation of Concerns**: HTML templates are separate from Python logic
2. **Maintainability**: Easier to modify UI without touching Python code
3. **Reusability**: Template inheritance reduces code duplication
4. **Standards Compliance**: Follows Flask best practices
5. **Collaboration**: Designers can work on templates independently

## Running the Application

1. Ensure you have the required dependencies installed
2. Set your `OPENROUTER_API_KEY` environment variable
3. Create templates using `python create_templates.py`
4. Run the Flask app with `python prompt_runner_flask.py`
5. Navigate to `http://localhost:5000` in your browser

## Troubleshooting

- **Templates not found**: Ensure the `templates/` directory exists and contains all required files
- **Styling issues**: Check that the CSS in `base.html` is properly formatted
- **JavaScript errors**: Verify that the script blocks in templates are correctly formatted
- **Flask template errors**: Check Jinja2 syntax in template files

## Development

When developing new features:
1. Add new routes to the Python file
2. Create corresponding templates in the `templates/` directory
3. Use template inheritance by extending `base.html`
4. Test the templates with various screen sizes and browsers