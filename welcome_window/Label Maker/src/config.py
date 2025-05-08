import os
import json
import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class LabelSettings:
    # Font settings
    font_size_large: int = 45
    font_size_medium: int = 45
    
    # Basic barcode dimensions
    barcode_width: int = 600
    barcode_height: int = 310
    
    # Window settings
    always_on_top: bool = False
    transparency_level: float = 0.9
    auto_close_browser_tabs: bool = True  # Whether to automatically close browser tabs when toggling buttons
    
    # Log settings
    automation_activity_log_enabled: bool = True  # Whether to enable detailed automation activity logging
    
    # Directory and counter
    last_directory: Optional[str] = None
    label_counter: int = 0
    
    # View files window preferences
    view_files_mirror_print: bool = False
    view_files_pin_window: bool = False
    view_files_auto_switch: bool = True
    view_files_print_minimize: bool = False  # Print minimize feature
    
    # JDL URL settings
    jdl_reverse_inbound_url: str = "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder"
    jdl_receive_url: str = "https://iwms.us.jdlglobal.com/#/scan"
    
    # Label dimensions
    DPI: int = 300
    LABEL_WIDTH: int = DPI * 2
    LABEL_HEIGHT: int = DPI * 2
    
    # Barcode appearance settings
    barcode_module_height: float = 120.0    # Taller bars for better visibility
    barcode_module_width: float = 2.5       # Wider individual bars with better spacing
    barcode_quiet_zone: float = 6.5         # Increased quiet zone for better scanning
    barcode_font_size: int = 12             # Size of UPC text
    barcode_text_distance: float = 6.0      # Distance of UPC text from bars
    barcode_write_text: bool = True         # Show the UPC number
    barcode_background: str = 'white'       # White background
    barcode_foreground: str = 'black'       # Black bars
    barcode_center_text: bool = True        # Center the UPC number
    barcode_dpi: int = 600                  # Higher DPI for much better print quality

class ConfigManager:
    def __init__(self):
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # Save settings in the program directory
        self.settings_file = os.path.join(script_dir, 'label_maker_settings.json')
        self.settings = LabelSettings()
        self.load_settings()

    def load_settings(self) -> None:
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    last_dir = data.get('last_directory', '')
                    # Only use the directory if it exists and is not empty
                    if not last_dir or not os.path.exists(last_dir):
                        last_dir = None
                        
                    self.settings = LabelSettings(
                        # Font settings
                        font_size_large=data.get('font_size_large', self.settings.font_size_large),
                        font_size_medium=data.get('font_size_medium', self.settings.font_size_medium),
                        
                        # Basic barcode dimensions
                        barcode_width=data.get('barcode_width', self.settings.barcode_width),
                        barcode_height=data.get('barcode_height', self.settings.barcode_height),
                        
                        # Window settings
                        always_on_top=data.get('always_on_top', self.settings.always_on_top),
                        transparency_level=data.get('transparency_level', self.settings.transparency_level),
                        auto_close_browser_tabs=data.get('auto_close_browser_tabs', self.settings.auto_close_browser_tabs),
                        
                        # Log settings
                        automation_activity_log_enabled=data.get('automation_activity_log_enabled', self.settings.automation_activity_log_enabled),
                        
                        # Directory and counter
                        last_directory=last_dir,
                        label_counter=data.get('label_counter', 0),
                        
                        # View files window preferences
                        view_files_mirror_print=data.get('view_files_mirror_print', False),
                        view_files_pin_window=data.get('view_files_pin_window', False),
                        view_files_auto_switch=data.get('view_files_auto_switch', True),
                        view_files_print_minimize=data.get('view_files_new_feature', False),
                        
                        # JDL URL settings
                        jdl_reverse_inbound_url=data.get('jdl_reverse_inbound_url', self.settings.jdl_reverse_inbound_url),
                        jdl_receive_url=data.get('jdl_receive_url', self.settings.jdl_receive_url),
                        
                        # DPI setting
                        DPI=data.get('DPI', self.settings.DPI),
                        
                        # Barcode appearance settings
                        barcode_module_height=data.get('barcode_module_height', self.settings.barcode_module_height),
                        barcode_module_width=data.get('barcode_module_width', self.settings.barcode_module_width),
                        barcode_quiet_zone=data.get('barcode_quiet_zone', self.settings.barcode_quiet_zone),
                        barcode_font_size=data.get('barcode_font_size', self.settings.barcode_font_size),
                        barcode_text_distance=data.get('barcode_text_distance', self.settings.barcode_text_distance),
                        barcode_write_text=data.get('barcode_write_text', self.settings.barcode_write_text),
                        barcode_background=data.get('barcode_background', self.settings.barcode_background),
                        barcode_foreground=data.get('barcode_foreground', self.settings.barcode_foreground),
                        barcode_center_text=data.get('barcode_center_text', self.settings.barcode_center_text),
                        barcode_dpi=data.get('barcode_dpi', self.settings.barcode_dpi)
                    )
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self) -> None:
        """Save settings to JSON file"""
        try:
            settings_dict = {
                # Font settings
                'font_size_large': self.settings.font_size_large,
                'font_size_medium': self.settings.font_size_medium,
                
                # Basic barcode dimensions
                'barcode_width': self.settings.barcode_width,
                'barcode_height': self.settings.barcode_height,
                
                # Window settings
                'always_on_top': self.settings.always_on_top,
                'transparency_level': self.settings.transparency_level,
                'auto_close_browser_tabs': self.settings.auto_close_browser_tabs,
                
                # Log settings
                'automation_activity_log_enabled': self.settings.automation_activity_log_enabled,
                
                # Directory and counter
                'last_directory': self.settings.last_directory if self.settings.last_directory else "",
                'label_counter': self.settings.label_counter,
                
                # View files window preferences
                'view_files_mirror_print': self.settings.view_files_mirror_print,
                'view_files_pin_window': self.settings.view_files_pin_window,
                'view_files_auto_switch': self.settings.view_files_auto_switch,
                'view_files_new_feature': self.settings.view_files_print_minimize,
                
                # JDL URL settings
                'jdl_reverse_inbound_url': self.settings.jdl_reverse_inbound_url,
                'jdl_receive_url': self.settings.jdl_receive_url,
                
                # DPI setting
                'DPI': self.settings.DPI,
                
                # Barcode appearance settings
                'barcode_module_height': self.settings.barcode_module_height,
                'barcode_module_width': self.settings.barcode_module_width,
                'barcode_quiet_zone': self.settings.barcode_quiet_zone,
                'barcode_font_size': self.settings.barcode_font_size,
                'barcode_text_distance': self.settings.barcode_text_distance,
                'barcode_write_text': self.settings.barcode_write_text,
                'barcode_background': self.settings.barcode_background,
                'barcode_foreground': self.settings.barcode_foreground,
                'barcode_center_text': self.settings.barcode_center_text,
                'barcode_dpi': self.settings.barcode_dpi
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings_dict, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
