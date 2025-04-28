from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from dataclasses import dataclass
from typing import Optional, Tuple
import os

def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename"""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*\'"'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove any other non-printable characters
    name = ''.join(char for char in name if char.isprintable())
    return name

@dataclass
class LabelData:
    name_line1: str
    name_line2: str
    variant: str
    upc_code: str

class BarcodeGenerator:
    def __init__(self, settings):
        self.settings = settings
        self._setup_fonts()

    def _setup_fonts(self):
        """Setup font paths and sizes"""
        try:
            fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
            
            # Check if fonts directory exists
            if not os.path.exists(fonts_dir):
                raise FileNotFoundError("Fonts directory not found. Please make sure the 'fonts' directory exists with arial.ttf and arialbd.ttf")
            
            # Use Arial Bold for large text
            arial_bold_path = os.path.join(fonts_dir, "arialbd.ttf")
            if not os.path.exists(arial_bold_path):
                raise FileNotFoundError("arialbd.ttf not found in fonts directory")
            self.font_large = ImageFont.truetype(arial_bold_path, self.settings.font_size_large)
            
            # Use Regular Arial for medium text
            arial_path = os.path.join(fonts_dir, "arial.ttf")
            if not os.path.exists(arial_path):
                raise FileNotFoundError("arial.ttf not found in fonts directory")
            self.font_medium = ImageFont.truetype(arial_path, self.settings.font_size_medium)
            # Add small font for long variants (30pt)
            self.font_small = ImageFont.truetype(arial_path, 30)
            
        except Exception as e:
            print(f"Error setting up fonts: {e}")
            print("Using default font as fallback")
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def generate_barcode_image(self, upc_code: str) -> Optional[Image.Image]:
        """Generate barcode image using python-barcode, cleaning Excel/CSV artifacts."""
        try:
            from src.utils.csv_processor import clean_and_validate_barcode
            cleaned_upc = clean_and_validate_barcode(upc_code)
            if not cleaned_upc:
                raise ValueError(f"Invalid UPC code: {upc_code}. Must be exactly 12 digits.")
            upc_code = cleaned_upc

            # Create UPC-A barcode
            barcode_class = barcode.get_barcode_class('upc')
            barcode_writer = ImageWriter()
            
            # Use settings from config for barcode appearance
            barcode_writer.set_options({
                'module_width': self.settings.barcode_module_width,
                'quiet_zone': self.settings.barcode_quiet_zone,
                'font_size': self.settings.barcode_font_size,
                'text_distance': self.settings.barcode_text_distance,
                'write_text': self.settings.barcode_write_text,
                'background': self.settings.barcode_background,
                'foreground': self.settings.barcode_foreground,
                'center_text': self.settings.barcode_center_text,
                'dpi': self.settings.barcode_dpi
            })
            
            # Generate barcode
            barcode_obj = barcode_class(upc_code, writer=barcode_writer)
            barcode_image = barcode_obj.render()
            
            # Use settings from config for dimensions
            target_width = self.settings.barcode_width
            target_height = self.settings.barcode_height
            
            # Resize using high-quality resampling
            barcode_image = barcode_image.resize(
                (target_width, target_height), 
                Image.Resampling.LANCZOS
            )
            
            return barcode_image
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None

    def process_camel_case(self, text):
        """
        Process text to add spaces after capital letters that are followed by lowercase letters.
        Example: 'RedShirt' becomes 'Red Shirt'
        
        Args:
            text (str): The text to process
            
        Returns:
            str: Processed text with spaces added after capital letters
        """
        import re
        
        # Handle edge cases
        if not text or not isinstance(text, str):
            return text
            
        # This is a more comprehensive approach that handles multiple occurrences
        result = text
        
        # Handle special case for names that are all uppercase
        if result.isupper() and len(result) > 3:
            # Don't process all uppercase names
            return result
            
        # Process camelCase (lowercase followed by uppercase)
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', result)
        
        # Process PascalCase (capital letters at start of words)
        result = re.sub(r'(^|\s)([A-Z][a-z]+)([A-Z])', r'\1\2 \3', result)
        
        # Handle consecutive capital letters (like "HTML") - don't split these
        # But do split if a capital is followed by lowercase (like "HTMLFile" -> "HTML File")
        result = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', result)
        
        return result
    
    def generate_label(self, data: LabelData) -> Optional[Image.Image]:
        """Generate complete label with text and barcode"""
        try:
            # Create blank label
            label = Image.new('RGB', (self.settings.LABEL_WIDTH, self.settings.LABEL_HEIGHT), 'white')
            draw = ImageDraw.Draw(label)

            # Configure default colors
            text_color = (0, 0, 0)  # Black color for text
            
            # Process the text to handle camelCase/PascalCase
            # This ensures the text is properly formatted on the label
            name_line1 = self.process_camel_case(data.name_line1)
            name_line2 = self.process_camel_case(data.name_line2)
            variant = self.process_camel_case(data.variant)
            
            # Draw text elements
            # Name Line 1 (fixed position at 20,20)
            if name_line1:
                draw.text((20, 20), name_line1, font=self.font_large, fill=text_color)
            
            # Name Line 2 (position depends on Name Line 1)
            if name_line2:
                name1_height = draw.textbbox((0, 0), name_line1 if name_line1 else "", font=self.font_large)[3]
                draw.text((20, 20 + name1_height), name_line2, font=self.font_large, fill=text_color)

            # Variant text position (dynamic font size)
            if variant:
                # Use 30pt font if variant is over 21 characters, else use standard medium
                variant_font = self.font_small if len(variant) > 21 else self.font_medium
                text_width = draw.textlength(variant, font=variant_font)
                x = (self.settings.LABEL_WIDTH - text_width) // 2
                draw.text((x, 165), variant, font=variant_font, fill=text_color)

            # Generate barcode
            barcode_image = self.generate_barcode_image(data.upc_code)
            if barcode_image:
                # Calculate position to center barcode
                x = (self.settings.LABEL_WIDTH - barcode_image.width) // 2
                y = 260  # Adjusted to be lower
                
                # Create a white background for the barcode
                bg_width = barcode_image.width + 20  # Add padding
                bg_height = barcode_image.height + 20
                bg_x = x - 10  # Adjust for padding
                bg_y = y - 10
                draw.rectangle([bg_x, bg_y, bg_x + bg_width, bg_y + bg_height], fill='white')
                
                # Paste barcode onto label
                label.paste(barcode_image, (x, y))

            return label
        except Exception as e:
            print(f"Error generating label: {e}")
            return None

    def _add_text_to_label(self, draw: ImageDraw.ImageDraw, data: LabelData):
        """Add text elements to the label"""
        # Calculate text positions
        name1_pos = self._center_text(data.name_line1, self.font_large, self.settings.LABEL_WIDTH)
        name2_pos = self._center_text(data.name_line2, self.font_large, self.settings.LABEL_WIDTH)
        variant_pos = self._center_text(data.variant, self.font_medium, self.settings.LABEL_WIDTH)

        # Draw text
        draw.text((name1_pos, 20), data.name_line1, font=self.font_large, fill='black')
        draw.text((name2_pos, 80), data.name_line2, font=self.font_large, fill='black')
        draw.text((variant_pos, 140), data.variant, font=self.font_medium, fill='black')

    def _center_text(self, text: str, font: ImageFont.FreeTypeFont, width: int) -> int:
        """Calculate x position to center text"""
        text_width = font.getlength(text)
        return (width - text_width) // 2

    def generate_and_save(self, data: LabelData, save_dir: str):
        """Generate and save label with consistent filename format"""
        # Generate the label
        label_image = self.generate_label(data)
        if label_image:
            # Create filename in same format as CSV: NAME Second NAME_Variant_label_123456789123
            safe_name1 = sanitize_filename(data.name_line1)
            safe_name2 = sanitize_filename(data.name_line2) if data.name_line2 else ""
            safe_variant = sanitize_filename(data.variant)
            
            if safe_name2:
                filename = f"{safe_name1} {safe_name2}_{safe_variant}_label_{data.upc_code}.png"
            else:
                filename = f"{safe_name1}_{safe_variant}_label_{data.upc_code}.png"
            
            filepath = os.path.join(save_dir, filename)
            label_image.save(filepath)
            return True
        return False
