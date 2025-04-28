"""
Settings Manager for the Sheets Manager application.
Handles loading, saving, and accessing application settings.
"""
import os
import json
import logging
from typing import Any, Dict, Optional, Union

# Default settings file path
DEFAULT_SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    'config', 
    'sheet_manager_settings.json'
)

# Default settings to use if file doesn't exist or is corrupted
DEFAULT_SETTINGS = {
    "app": {
        "version": "1.0.0",
        "theme": "light",
        "window": {
            "width": 560,
            "height": 525,
            "remember_position": True,
            "position": {
                "x": None,
                "y": None
            }
        },
        "startup": {
            "check_for_updates": True,
            "show_welcome": True
        }
    },
    "google_sheets": {
        "google_sheet_url": None,
        "google_sheet_name": None,
        "google_sheet_id": None,
        "google_sheets_connection_status": "Not Connected",
        "auto_sync": False,
        "sync_interval_minutes": 5,
        "last_sync_time": None,
        "columns": {
            "tracking_column": "A",
            "tracking_row": 1,
            "sku_column": "B",
            "sku_row": 1,
            "steps_column": "C",
            "steps_row": 1
        }
    },
    "user_preferences": {
        "confirm_before_edit": True,
        "auto_save": True,
        "save_interval_minutes": 2,
        "default_view": "table",
        "show_tooltips": True,
        "date_format": "MM/DD/YYYY",
        "language": "en-US",
        "notifications": {
            "enabled": True,
            "sound": True,
            "sync_complete": True,
            "sync_error": True
        }
    },
    "recent_files": [],
    "advanced": {
        "debug_mode": False,
        "log_level": "INFO",
        "max_log_size_mb": 5,
        "max_log_files": 3,
        "backup_enabled": True,
        "backup_interval_days": 7,
        "backup_location": None,
        "max_backups": 5
    }
}


class SettingsManager:
    """
    Manages application settings, providing methods to load, save, and access settings.
    Uses a singleton pattern to ensure only one instance exists.
    """
    _instance = None
    
    def __new__(cls, settings_path=None):
        """Ensure only one instance of SettingsManager exists (singleton)."""
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, settings_path=None):
        """Initialize the settings manager if not already initialized."""
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SheetsManager')
        self.settings_path = settings_path or DEFAULT_SETTINGS_PATH
        self.settings = {}
        self._initialized = True
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        
        # Load settings
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """
        Load settings from the settings file.
        If the file doesn't exist or is corrupted, use default settings.
        """
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to ensure all expected keys exist
                self.settings = self._merge_with_defaults(loaded_settings)
                self.logger.info(f"Settings loaded from {self.settings_path}")
            else:
                self.settings = DEFAULT_SETTINGS.copy()
                self.logger.info(f"Settings file not found. Using defaults.")
                # Save defaults to create the file
                self.save()
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
            self.settings = DEFAULT_SETTINGS.copy()
        
        return self.settings
    
    def _merge_with_defaults(self, loaded_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge loaded settings with defaults to ensure all keys exist.
        """
        result = DEFAULT_SETTINGS.copy()
        
        def merge_dict(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value
        
        merge_dict(result, loaded_settings)
        return result
    
    def save(self) -> bool:
        """
        Save current settings to the settings file.
        Returns True if successful, False otherwise.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            self.logger.info(f"Settings saved to {self.settings_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            return False
    
    def get(self, *keys, default=None) -> Any:
        """
        Get a setting value using dot notation or nested keys.
        Example: settings_manager.get('app', 'window', 'width')
        Returns the default value if the key doesn't exist.
        """
        if not keys:
            return self.settings
            
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, value: Any, *keys) -> bool:
        """
        Set a setting value using dot notation or nested keys.
        Example: settings_manager.set(800, 'app', 'window', 'width')
        Returns True if successful, False otherwise.
        """
        if not keys:
            return False
            
        target = self.settings
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            elif not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
            
        target[keys[-1]] = value
        return True
    
    def update(self, section: str, values: Dict[str, Any], save: bool = True) -> bool:
        """
        Update multiple settings in a section at once.
        Example: settings_manager.update('app', {'theme': 'dark', 'version': '1.0.1'})
        Returns True if successful, False otherwise.
        """
        if section not in self.settings:
            self.settings[section] = {}
            
        if not isinstance(self.settings[section], dict):
            self.settings[section] = {}
            
        for key, value in values.items():
            self.settings[section][key] = value
            
        if save:
            return self.save()
        return True
    
    def reset_to_defaults(self, save: bool = True) -> bool:
        """
        Reset all settings to default values.
        Returns True if successful, False otherwise.
        """
        self.settings = DEFAULT_SETTINGS.copy()
        if save:
            return self.save()
        return True
    
    def reset_section(self, section: str, save: bool = True) -> bool:
        """
        Reset a specific section to default values.
        Returns True if successful, False otherwise.
        """
        if section in DEFAULT_SETTINGS:
            self.settings[section] = DEFAULT_SETTINGS[section].copy()
            if save:
                return self.save()
            return True
        return False
    
    def backup(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the current settings file.
        Returns True if successful, False otherwise.
        """
        import shutil
        from datetime import datetime
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(
                os.path.dirname(self.settings_path), 
                'backups'
            )
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(
                backup_dir, 
                f"settings_backup_{timestamp}.json"
            )
            
        try:
            if os.path.exists(self.settings_path):
                shutil.copy2(self.settings_path, backup_path)
                self.logger.info(f"Settings backed up to {backup_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error backing up settings: {str(e)}")
            return False
    
    def migrate_from_old_settings(self, old_settings_path: str) -> bool:
        """
        Migrate settings from an old settings file.
        Returns True if successful, False otherwise.
        """
        try:
            if not os.path.exists(old_settings_path):
                return False
                
            with open(old_settings_path, 'r') as f:
                old_settings = json.load(f)
                
            # Backup current settings before migration
            self.backup()
            
            # Perform migration logic here
            # This is a simple example - customize based on your needs
            if 'google_sheet_url' in old_settings:
                self.set(old_settings['google_sheet_url'], 'google_sheets', 'google_sheet_url')
                
            if 'google_sheet_name' in old_settings:
                self.set(old_settings['google_sheet_name'], 'google_sheets', 'google_sheet_name')
                
            if 'google_sheet_id' in old_settings:
                self.set(old_settings['google_sheet_id'], 'google_sheets', 'google_sheet_id')
                
            if 'google_sheets_connection_status' in old_settings:
                self.set(old_settings['google_sheets_connection_status'], 'google_sheets', 'google_sheets_connection_status')
            
            # Save the migrated settings
            return self.save()
        except Exception as e:
            self.logger.error(f"Error migrating settings: {str(e)}")
            return False


# Create a global instance for easy import
settings_manager = SettingsManager()

# Example usage:
# from config.settings_manager import settings_manager
# 
# # Get a setting
# window_width = settings_manager.get('app', 'window', 'width')
# 
# # Set a setting
# settings_manager.set(800, 'app', 'window', 'width')
# settings_manager.save()
# 
# # Update multiple settings
# settings_manager.update('user_preferences', {'theme': 'dark', 'auto_save': False})
