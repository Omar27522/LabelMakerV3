# Project Cleanup Standards

This document outlines the standards and procedures for maintaining a clean and organized project structure for the Label Maker application.

## Directory Structure Standards

1. **Root Directory**
   - Should contain only essential files: `main.pyw`, `start_label_maker.pyw`, `label_maker_settings.json`, `.windsurf`, `.gitignore`, and top-level directories
   - No duplicate or redundant directories
   - No empty directories

2. **Source Code (`src/`)**
   - Organized by module type: `ui/`, `utils/`, `config/`
   - Each module should have a clear, single responsibility
   - Include `__init__.py` files in all Python packages

3. **Documentation (`docs/`)**
   - One file per major component or feature
   - Index file (`index.md`) to navigate all documentation
   - Documentation should be kept up-to-date with code changes

4. **Assets**
   - Images, fonts, and other static resources in appropriate directories
   - Use consistent naming conventions

## File Management Standards

1. **Temporary Files**
   - No `.pyc` files or `__pycache__` directories should be committed
   - No `.bak`, `.tmp`, or other temporary files should be kept in the repository

2. **Configuration Files**
   - Settings should be stored in `label_maker_settings.json` at the root level
   - No duplicate configuration files

3. **Logs**
   - Log files should be stored in the `logs/` directory
   - Implement log rotation to prevent files from growing too large
   - Old logs should be archived or deleted periodically

## Code Quality Standards

1. **Imports**
   - Organize imports: standard library, third-party, local
   - Remove unused imports

2. **Comments and Documentation**
   - All functions should have docstrings
   - Complex logic should have inline comments
   - Keep comments up-to-date with code changes

3. **Dead Code**
   - Remove commented-out code that is no longer needed
   - Remove unused functions and classes

## Periodic Cleanup Tasks

### Weekly

1. **Remove Cache Files**
   ```powershell
   Get-ChildItem -Path . -Recurse -Include "__pycache__" -Directory | Remove-Item -Recurse -Force
   ```

2. **Check for Temporary Files**
   ```powershell
   Get-ChildItem -Path . -Recurse -Include "*.bak", "*.tmp", "*.pyc" -File | Remove-Item -Force
   ```

### Monthly

1. **Log Rotation**
   - Archive logs older than 30 days
   - Delete logs older than 90 days

2. **Dependency Review**
   - Review and update dependencies
   - Remove unused dependencies

3. **Documentation Review**
   - Ensure documentation matches current functionality
   - Update any outdated information

### Quarterly

1. **Code Review**
   - Check for unused functions and classes
   - Refactor duplicated code
   - Review error handling

2. **Full Project Structure Review**
   - Ensure directory structure follows standards
   - Check for any duplicate or redundant files
   - Update CODEBASE_MAP.md

## Cleanup Script

A cleanup script can be created to automate many of these tasks. Here's a sample script that could be implemented:

```python
# cleanup.py
import os
import shutil
import datetime
import glob

def remove_cache_files():
    """Remove all __pycache__ directories and .pyc files"""
    # Find and remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            print(f"Removing {cache_dir}")
            shutil.rmtree(cache_dir)
    
    # Find and remove .pyc files
    for pyc_file in glob.glob('**/*.pyc', recursive=True):
        print(f"Removing {pyc_file}")
        os.remove(pyc_file)

def clean_logs(days_to_keep=30):
    """Archive or remove old log files"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        return
    
    current_time = datetime.datetime.now()
    for log_file in os.listdir(log_dir):
        if not log_file.endswith('.log'):
            continue
        
        log_path = os.path.join(log_dir, log_file)
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(log_path))
        
        # If file is older than days_to_keep, remove it
        if (current_time - file_time).days > days_to_keep:
            print(f"Removing old log file: {log_path}")
            os.remove(log_path)

def remove_temp_files():
    """Remove temporary files"""
    temp_extensions = ['.bak', '.tmp']
    for ext in temp_extensions:
        for temp_file in glob.glob(f'**/*{ext}', recursive=True):
            print(f"Removing temporary file: {temp_file}")
            os.remove(temp_file)

if __name__ == "__main__":
    print("Starting project cleanup...")
    remove_cache_files()
    clean_logs()
    remove_temp_files()
    print("Cleanup complete!")
```

## Implementation Checklist

When implementing these cleanup standards:

- [ ] Update .gitignore to exclude temporary files
- [ ] Set up log rotation
- [ ] Create cleanup script
- [ ] Schedule regular cleanup tasks
- [ ] Review and refactor code for unused components
- [ ] Update documentation to reflect current state

## Conclusion

Following these cleanup standards will help maintain a clean, organized, and efficient codebase. Regular maintenance reduces technical debt and makes the project easier to understand and modify.
