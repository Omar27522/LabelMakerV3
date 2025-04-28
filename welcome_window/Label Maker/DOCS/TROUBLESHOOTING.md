# Troubleshooting Guide

## Table of Contents

- [Quick Reference](#quick-reference)
- [Common Issues and Solutions](#common-issues-and-solutions)
  - [Print Issues](#print-issues)
  - [Window Management](#window-management)
  - [Preview Issues](#preview-issues)
  - [File Management](#file-management)
  - [Performance Issues](#performance-issues)
- [Error Messages](#error-messages)
- [System Requirements](#system-requirements)
- [Logging and Diagnostics](#logging-and-diagnostics)
- [Contact Support](#contact-support)

## Quick Reference

| Issue | Quick Solution |
|-------|---------------|
| Print preview not showing | Check default printer, restart application |
| Auto-switch not working | Verify auto-switch is enabled in settings |
| Preview not updating | Reduce preview size, clear preview cache |
| CSV import failures | Verify CSV format and required columns |
| Application freezing | Check system resources, reduce batch size |
| "Invalid barcode format" error | Ensure UPC is exactly 12 digits |
| Window position reset | Check write permissions in app directory |

## Common Issues and Solutions

### Print Issues

#### Print Preview Not Showing
**Problem**: Print preview window doesn't appear when clicking print.

**Solution**: 
1. Check if a default printer is set
2. Verify print spooler service is running
3. Restart the application

#### Print Quality Issues
**Problem**: Labels print with poor quality or scaling issues.

**Solution**:
1. Verify DPI settings in configuration
2. Check printer resolution settings
3. Ensure correct label size is selected

### Window Management

#### Auto-Switch Not Working
**Problem**: Windows don't automatically switch as expected.

**Solution**:
1. Verify auto-switch is enabled in settings
2. Check if any windows are pinned
3. Ensure no dialog windows are open

#### Window Position Reset
**Problem**: Windows don't remember their positions.

**Solution**:
1. Check write permissions in app directory
2. Clear window position cache
3. Reset window settings

### Preview Issues

#### Preview Not Updating
**Problem**: Label preview doesn't update with changes.

**Solution**:
1. Check available memory
2. Reduce preview size
3. Clear preview cache

#### Preview Size Issues
**Problem**: Preview appears too large or small.

**Solution**:
1. Cycle through preview sizes (3->4->5)
2. Check display scaling settings
3. Reset preview settings

### File Management

#### CSV Import Failures
**Problem**: CSV files fail to import.

**Solution**:
1. Verify CSV format
2. Check for special characters
3. Ensure required columns exist

#### File Access Errors
**Problem**: Cannot access or save files.

**Solution**:
1. Check file permissions
2. Verify path exists
3. Close files in other applications

### Performance Issues

#### Slow Preview Generation
**Problem**: Label previews generate slowly.

**Solution**:
1. Reduce preview quality
2. Clear temporary files
3. Check available memory

#### Application Freezing
**Problem**: Application becomes unresponsive.

**Solution**:
1. Check system resources
2. Reduce batch size
3. Clear application cache

## Error Messages

### Common Error Messages and Resolutions

#### "Failed to initialize printer"
**Cause**: Printer configuration or access issues

**Resolution**:
1. Check printer connection
2. Verify printer drivers
3. Reset print spooler

#### "Invalid barcode format"
**Cause**: Incorrect barcode input

**Resolution**:
1. Verify barcode format
2. Check input length
3. Remove special characters

#### "Configuration file corrupted"
**Cause**: Settings file issues

**Resolution**:
1. Restore from backup
2. Reset to defaults
3. Check file permissions

## System Requirements

### For Python Script Method
- Windows 10 or later
- Python 3.7+
- 4GB RAM
- 1GB free disk space
- Required Python packages (see requirements.txt)

### For Executable Method
- Windows 10 or later
- 4GB RAM
- 1GB free disk space
- No Python installation required

### Recommended Requirements
- Windows 11
- 8GB RAM
- 2GB free disk space
- SSD storage

### Application Startup Issues

#### Application Fails to Start
**Problem**: Application doesn't start when clicking the Python script or executable.

**Solution for Python Script Method**:
1. Verify Python 3.7+ is installed and in PATH
2. Check that all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```
3. Try running from command line to see error messages:
   ```
   python main.pyw
   ```

**Solution for Executable Method**:
1. Verify "Label Maker V3.exe" exists in the installation directory
2. Check for missing DLL errors in Event Viewer
3. Try reinstalling the application
4. Ensure Windows is up to date with latest updates

#### Multiple Instances Error
**Problem**: Error message about another instance already running.

**Solution**:
1. Check Task Manager for existing instances
2. Restart your computer if no instances are visible
3. Delete any temporary lock files in the application directory

## Logging and Diagnostics

The Label Maker application includes a comprehensive logging system that can help diagnose issues. For detailed information about the logging system, error codes, and how to use logs for troubleshooting, please refer to the [Logging and Error Handling Guide](LOGGING.md).

### Finding Log Files

Log files are stored in the `logs` directory within the application's installation folder:

```
[Installation Directory]/logs/label_maker_YYYYMM.log
```

Where `YYYYMM` represents the year and month (e.g., `label_maker_202502.log` for February 2025).

### Using Logs for Troubleshooting

When encountering an error:

1. Note the exact error message shown in the application
2. Check the log file for more detailed information about the error
3. Use the error details to identify the specific solution in this guide or the [Logging and Error Handling Guide](LOGGING.md)

### Submitting Logs for Support

When contacting support, it's helpful to provide:

1. A copy of the relevant log file
2. A description of the steps that led to the error
3. Screenshots of any error messages
4. Your system information (Windows version, available memory, etc.)

## Contact Support

If issues persist:
1. Check documentation
2. Search existing issues
3. Create new issue with:
   - Error details
   - Steps to reproduce
   - System information
