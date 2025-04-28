# Developer Guide

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Coding Standards](#coding-standards)
- [Key Components](#key-components)
- [Extension Points](#extension-points)
- [Development Environment](#development-environment)
- [Testing](#testing)
- [Building and Packaging](#building-and-packaging)
- [Contributing](#contributing)

## Overview

Label Maker is a Python-based application built primarily with Tkinter for the user interface. This guide provides information for developers who want to understand, modify, or extend the application.

## Architecture

### High-Level Architecture

Label Maker follows a modular architecture with these main components:

1. **User Interface (UI)** - Tkinter-based windows and controls
2. **Configuration Management** - Settings persistence and management
3. **Barcode Generation** - Label creation and barcode rendering
4. **CSV Processing** - Batch import functionality
5. **File Management** - Output file handling and organization
6. **Printing System** - Label printing and printer integration

### Directory Structure

```
label_maker/
├── src/
│   ├── ui/
│   │   ├── main_window.py    # Main application window
│   │   └── dialogs.py        # Additional dialog windows
│   ├── utils/
│   │   ├── csv_processor.py  # CSV import functionality
│   │   └── file_utils.py     # File operations utilities
│   ├── barcode_generator.py  # Label and barcode generation
│   ├── config.py             # Configuration management
│   └── main.py               # Application entry point
├── resources/
│   ├── fonts/                # Font files
│   └── images/               # Image resources
├── logs/                     # Application logs
└── DOCS/                     # Documentation
```

### Data Flow

1. User inputs product information or imports CSV
2. Data is validated and processed
3. Barcode is generated using python-barcode
4. Label is created with Pillow (PIL)
5. Label is saved to the output directory
6. User can view and print labels

## Coding Standards

### Python Style Guide

Label Maker follows PEP 8 conventions with these specifics:

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 100 characters
- **Naming Conventions**:
  - Classes: `CamelCase`
  - Functions/Methods: `snake_case`
  - Variables: `snake_case`
  - Constants: `UPPER_CASE`
- **Docstrings**: Google style docstrings

### Example Docstring Format

```python
def function_name(param1, param2):
    """Short description of function.
    
    Longer description explaining details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When and why this exception is raised
    """
    # Function implementation
```

### Error Handling

- Use explicit exception types when possible
- Log exceptions with appropriate levels
- Present user-friendly error messages
- Include detailed information in logs

## Key Components

### MainWindow Class

The `MainWindow` class in `main_window.py` is the central UI component that:

- Manages the main application window
- Handles user interactions
- Coordinates between different components
- Manages the View Files window

### BarcodeGenerator Class

The `BarcodeGenerator` class in `barcode_generator.py`:

- Creates label images with product information
- Generates UPC barcodes
- Handles text positioning and layout
- Manages fonts and image composition

### ConfigManager Class

The `ConfigManager` class in `config.py`:

- Loads and saves application settings
- Manages default values
- Handles configuration file I/O
- Provides access to settings throughout the application

### CSVProcessor Class

The `CSVProcessor` class in `csv_processor.py`:

- Parses CSV files
- Validates data
- Extracts product information
- Generates labels in batch

## Extension Points

### Adding New Features

The most common extension points are:

1. **New UI Controls**:
   - Add to the appropriate section in `main_window.py`
   - Follow existing patterns for consistency

2. **New Label Formats**:
   - Extend the `BarcodeGenerator` class
   - Add new layout methods

3. **Additional Import Formats**:
   - Create new processor classes similar to `CSVProcessor`
   - Implement the appropriate parsing logic

4. **New Configuration Options**:
   - Add properties to the `Settings` class in `config.py`
   - Update the UI to expose these settings

### Example: Adding a New Label Format

```python
def generate_circular_label(self, data):
    """Generate a circular label format.
    
    Args:
        data: LabelData object containing product information
        
    Returns:
        PIL Image object of the generated label
    """
    # Create a circular mask
    mask = Image.new('L', (self.settings.LABEL_WIDTH, self.settings.LABEL_HEIGHT), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, self.settings.LABEL_WIDTH, self.settings.LABEL_HEIGHT), fill=255)
    
    # Create the base label
    label = self.generate_label(data)
    
    # Apply the circular mask
    circular_label = Image.new('RGB', (self.settings.LABEL_WIDTH, self.settings.LABEL_HEIGHT), 'white')
    circular_label.paste(label, (0, 0), mask)
    
    return circular_label
```

## Development Environment

### Required Software

- Python 3.8 or higher
- Git for version control
- Visual Studio Code (recommended) or your preferred IDE

### Setting Up the Development Environment

1. Clone the repository:
   ```
   git clone https://github.com/your-org/label-maker.git
   cd label-maker
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```
   pip install -r requirements-dev.txt
   ```

### Running in Development Mode

```
python src/main.pyw
```

For debugging purposes, you can also run the application with console output:

```
python -m src.main
```

## Testing

### Testing Framework

Label Maker uses pytest for testing:

```
pytest tests/
```

### Test Structure

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- UI tests in `tests/ui/`

### Writing Tests

Example test for the barcode generator:

```python
def test_barcode_generation():
    """Test that barcodes are generated correctly."""
    from src.barcode_generator import BarcodeGenerator
    from src.config import Settings
    
    # Setup
    settings = Settings()
    generator = BarcodeGenerator(settings)
    
    # Test valid UPC
    barcode = generator.generate_barcode("123456789012")
    assert barcode is not None
    assert barcode.width > 0
    assert barcode.height > 0
    
    # Test invalid UPC
    with pytest.raises(ValueError):
        generator.generate_barcode("1234")
```

## Building and Packaging

### Creating an Executable

Label Maker uses PyInstaller for creating standalone executables:

```
pyinstaller --name="Label Maker V3" ^
            --windowed ^
            --icon=resources/icon.ico ^
            --add-data="resources;resources" ^
            src/main.pyw
```

This creates a standalone executable ("Label Maker V3.exe") that doesn't require Python to be installed on the target system.

### Packaging for Distribution

1. Build the executable using PyInstaller
2. Include necessary resources:
   - fonts/
   - images/
   - config.ini (template)
3. Create an installer using Inno Setup or similar

For more detailed instructions on building and packaging, see the [Deployment Guide](DEPLOYMENT.md).

## Contributing

### Contribution Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Code Review Process

All contributions go through code review:

1. Automated checks (linting, tests)
2. Manual review by maintainers
3. Feedback and iteration
4. Approval and merge

### Versioning

Label Maker follows Semantic Versioning (SemVer):

- **Major version**: Incompatible API changes
- **Minor version**: New features (backward compatible)
- **Patch version**: Bug fixes (backward compatible)

### Release Process

1. Update version number in `config.py`
2. Update CHANGELOG.md
3. Create a release tag
4. Build release artifacts
5. Publish release
