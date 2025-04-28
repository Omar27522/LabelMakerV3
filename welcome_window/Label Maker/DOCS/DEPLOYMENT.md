# Deployment Guide

## Building and Distribution

### Prerequisites
1. Python 3.7+
2. Required packages:
   ```
   pip install pyinstaller
   pip install -r src/requirements.txt
   ```

### Application Execution Methods

Label Maker can be used in two ways:

1. **Python Script (Development/Simple Deployment)**
   - Run the `main.pyw` file directly with Python
   - Requires Python 3.7+ and all dependencies installed
   - Ideal for development or simple deployments

2. **Compiled Executable (Production Deployment)**
   - Create a standalone `.exe` file using PyInstaller
   - Does not require Python or dependencies to be installed on the target system
   - Recommended for production environments and end-user distribution

### Building the Application

1. **Using PyInstaller**
   ```bash
   pyinstaller --name="Label Maker V3" ^
               --windowed ^
               --icon=assets/icons/app.ico ^
               --add-data="assets;assets" ^
               --add-data="fonts;fonts" ^
               --add-data="docs;docs" ^
               main.pyw
   ```

2. **Output Structure**
   ```
   dist/
   └── Label Maker V3/
       ├── Label Maker V3.exe    # Standalone executable that doesn't require Python
       ├── assets/
       │   ├── icons/
       │   └── dependencies/
       ├── fonts/
       └── docs/
   ```

### Installation Package

1. **Creating Installer**
   - Use Inno Setup for Windows installer
   - Include all dependencies
   - Configure start menu shortcuts
   - Set up file associations

2. **Installer Options**
   ```
   [Setup]
   AppName=Label Maker V3
   AppVersion=1.0.2
   DefaultDirName={pf}\Label Maker V3
   DefaultGroupName=Label Maker V3
   OutputBaseFilename=LabelMakerV3_Setup
   ```

## System Requirements

### Minimum Requirements
- Windows 10 or later
- 4GB RAM
- 1GB free disk space
- 1280x720 screen resolution

### Recommended
- Windows 11
- 8GB RAM
- 2GB free disk space
- 1920x1080 screen resolution
- SSD storage

## Installation

### Simple Installation (Python Script)
1. Download the latest version from GitHub:
   - Repository: [https://github.com/current/LabelsV3.zip](https://github.com/Omar27522/Projects/tree/main/labels/current)
   - Download the ZIP file using the "Code" button and select "Download ZIP"
2. Extract the ZIP file to your preferred location
3. Run `main.pyw` to start the application
4. Configure printer settings and verify operation

### Requirements for Python Script Method
- Python 3.7 or higher must be installed on your system
- Required packages will be included in the ZIP file
- Windows 10 or higher recommended

### Executable Installation
If you have built the application using PyInstaller or have downloaded a pre-built executable:
1. Run the installer if available, or extract the distribution folder
2. Launch "Label Maker V3.exe" to start the application
3. No Python installation is required

## Configuration

### Initial Setup
1. Configure printer settings
2. Set default save location
3. Configure auto-switch behavior
4. Set preview preferences

## Updates

### Manual Updates
- No automatic update feature is currently available
- To update, download the latest ZIP file from GitHub
- Extract to a new location
- Copy any custom configurations from your previous installation
- Start using the new version

## Troubleshooting

### Common Installation Issues
1. **Permission Errors**
   - Run as administrator
   - Check file permissions
   - Verify user rights

2. **Missing Dependencies**
   - Ensure Python 3.7+ is installed
   - Required Python packages:
     - Pillow (PIL): For image processing
     - pywin32: For Windows-specific functionality
     - pandas: For data handling
     - pyautogui: For automation features
     - python-barcode: For barcode generation
   - Run `pip install -r src/requirements.txt` to install all dependencies

## Maintenance

### Regular Tasks
1. Clear temporary files
2. Backup configuration
3. Update printer settings
4. Check log files

### Backup Process
1. Export user settings
2. Backup label templates
3. Save printer configurations
4. Archive log files

## Uninstallation

### Removing the Application
1. Delete the application directory
2. No formal uninstaller is required as the application is portable

### Preserving Data (Optional)
1. Before deleting, back up any custom configurations or templates you wish to keep
2. Save any important generated labels or data files
