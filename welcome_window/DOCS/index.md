# Label Maker Application Documentation

## Overview

This documentation provides detailed information about the Label Maker application, its components, and how they interact.

## Table of Contents

### Core Components

- [Welcome Window](welcome_window.md): Main welcome interface
- [UI Components](ui_components.md): Standardized UI elements
- [Returns Operations](returns_operations.md): Returns data and record management
- [Google Sheets Integration](google_sheets_integration.md): Sheets API integration

### Configuration

- [Configuration Management](configuration.md): Application settings management
- [Settings Operations](settings_operations.md): Settings dialog and persistence

### User Interface

- [Window State Management](window_state.md): Tracking and restoring window state
- [Button Styling](button_styling.md): Material-inspired button styles
- [Form Components](form_components.md): Form field creation and validation
- [Edit Record Window](edit_record_window.md): Scrollable, paginated, and accessible record editing
- [Create Label Window](create_label_window.md): Label creation interface with print and Sheets features
- [Labels Tab](labels_tab.md): Comprehensive label search, import, export, and management tab
- [Label Details Dialog](label_details_dialog.md): Visual label preview, metadata, and enhanced controls

### Features

- [Label Count Display](label_count.md): Dynamic label count in UI
- [Directory Management](directory_management.md): Selecting and managing label directories
- [Returns Data Management](returns_data.md): Managing and editing shipping records
- [Google Sheets Tracking](sheets_tracking.md): Syncing tracking info with Google Sheets
- [Application Windows Map](application_windows_map.md): Overview of all major windows and dialogs
- [Codebase Map](CODEBASE_MAP.md): Up-to-date map of all modules and files

## Development

### Development Guidelines

- [Project Structure](project_structure.md): Overview of the project's directory structure
- [Code Style Guide](code_style.md): Coding standards and style guidelines
- [Testing](testing.md): Testing procedures and guidelines
- [Project Cleanup Standards](project_cleanup_standards.md): Standards and procedures for maintaining a clean project structure

### Adding New Features

1. Create appropriate documentation in the `DOCS/` directory
2. Add comprehensive docstrings to your code
3. Update the README.md with information about the new feature
4. Follow the existing code style and structure

### Code Style

- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Use type hints where appropriate
- Follow PEP 8 guidelines

### UI Development

- Use the standardized UI components from `src/utils/ui_components.py`
- Follow the Material Design color scheme
- Ensure all interfaces are responsive and user-friendly
- Implement proper validation for all user inputs

## Troubleshooting

### Common Issues

- **ModuleNotFoundError**: Ensure you're running the application from the correct directory or using the main.py entry point
- **Directory Access Issues**: Make sure the application has appropriate permissions to access the labels directory
- **Google Sheets Connection Issues**: Verify your credentials.json file and internet connection
- **UI Scaling Issues**: Check your system's DPI settings if UI elements appear too small or large
