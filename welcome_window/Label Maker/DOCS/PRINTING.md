# Printing Configuration Guide

## Table of Contents

- [Overview](#overview)
- [Label Specifications](#label-specifications)
- [Printer Setup](#printer-setup)
- [Paper and Media Types](#paper-and-media-types)
- [Print Settings](#print-settings)
- [Advanced Printing Features](#advanced-printing-features)
- [Troubleshooting](#troubleshooting)
- [Printer Recommendations](#printer-recommendations)

## Overview

Label Maker is designed to work with standard label printers and regular printers using label paper. This guide provides detailed information about configuring your printer for optimal results with 2" x 2" (5.08cm x 5.08cm) labels.

## Label Specifications

Label Maker generates labels with the following specifications:

- **Dimensions**: 2" x 2" (5.08cm x 5.08cm)
- **Resolution**: 300 DPI (dots per inch)
- **Margins**: No margins (borderless printing)
- **Format**: RGB color image (even if printing in black and white)
- **Orientation**: Portrait

The application creates label images that are exactly 600 x 600 pixels (2 inches × 300 DPI) to match the physical dimensions of the label.

## Printer Setup

### General Printer Configuration

1. Open **Control Panel** > **Devices and Printers**
2. Right-click your printer and select **Printing Preferences**
3. Configure the following settings:
   - **Paper Size**: Custom (2" x 2" or 5.08cm x 5.08cm)
   - **Paper Type**: Labels or Card Stock
   - **Print Quality**: High or Photo Quality
   - **Margins**: None (for borderless printing)

### Creating a Custom Paper Size

Most printers require creating a custom paper size for 2" x 2" labels:

1. In **Printing Preferences**, click **Advanced** or **Custom Paper Size**
2. Create a new paper size with the following properties:
   - **Name**: "2x2 Label"
   - **Width**: 2.00 inches (5.08 cm)
   - **Height**: 2.00 inches (5.08 cm)
   - **Margins**: All set to 0 (zero)
3. Save the custom paper size
4. Select this paper size when printing labels

### Printer-Specific Instructions

#### Thermal Label Printers (DYMO, Zebra, Brother)

1. Install the latest printer drivers from the manufacturer's website
2. Configure the label size in the printer's software to 2" x 2"
3. Set print density to medium-high for optimal barcode scanning
4. Disable any automatic scaling options

#### Inkjet/Laser Printers

1. Select "Actual Size" or "100%" in the print dialog to prevent scaling
2. Disable "Fit to Page" options
3. For sheet labels, ensure you've selected the correct label layout in your printer settings

## Paper and Media Types

### Recommended Label Types

- **Pre-cut 2" x 2" Labels**: Available in sheets or rolls
- **Adhesive Type**: Permanent adhesive for standard applications
- **Material**: Matte white for best readability and barcode scanning
- **Thickness**: 20-24 lb paper weight recommended

### Label Sheets Configuration

If using label sheets (multiple labels per sheet):

1. Ensure the labels on the sheet are exactly 2" x 2"
2. When printing, select "Multiple pages per sheet" in your printer's advanced settings
3. Set the layout to match your label sheet configuration
4. Disable any scaling options

## Print Settings

### Optimal Print Settings

For best results with Label Maker, configure these settings in your printer:

1. **Resolution**: 300 DPI (to match the label's native resolution)
2. **Color Mode**: Color or Black & White depending on your needs
3. **Print Quality**: High or Best
4. **Media Type**: Labels or Card Stock
5. **Scaling**: None (100% / Actual Size)

### Application Print Settings

Label Maker includes several printing features that can be configured in the application:

1. **Mirror Printing**: Flips the label horizontally (useful for printing on the adhesive side of transparent labels)
   - Toggle with the mirror button in the View Files window
   - Keyboard shortcut: None (use the button)

2. **Auto-Switch**: Automatically selects the next label after printing
   - Toggle with the auto-switch button in the View Files window
   - Useful for batch printing multiple labels

3. **Print Minimize**: Automatically minimizes the window after printing
   - Toggle with the print minimize button in the View Files window
   - Helps streamline workflow when printing multiple labels

## Advanced Printing Features

### Batch Printing

When printing multiple labels from CSV files:

1. Import your CSV file using the CSV import feature
2. Labels will be generated in the output directory
3. Open the View Files window to see all generated labels
4. Use the Auto-Switch feature to quickly print multiple labels in sequence

### Mirror Printing

Mirror printing reverses the label horizontally, which is useful for:

1. Printing on the adhesive side of transparent labels
2. Creating window stickers that are viewed from the opposite side
3. Special application requirements where the label needs to be mirrored

To use mirror printing:

1. In the View Files window, click the mirror button (or use the toggle in settings)
2. The application will create a mirrored temporary copy of the label
3. This temporary copy is sent to the printer
4. The original file remains unchanged

## Troubleshooting

### Common Printing Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Label prints too small | Scaling is enabled | Set printer to "Actual Size" (100%) |
| Margins appear around label | Printer doesn't support borderless | Adjust printer settings or use "Borderless" option if available |
| Barcode doesn't scan | Print quality too low | Increase print resolution and ensure high contrast |
| Colors look different | Printer calibration | Calibrate printer colors or switch to black & white |
| Print dialog doesn't appear | System print dialog issue | Restart application or update printer drivers |
| "Failed to print" error | Printer connection issue | Check printer connection and status |

### Printer-Specific Issues

#### DYMO LabelWriter

- Ensure you're using DYMO Label Software v8.5 or higher
- Select "2x2" label size in DYMO settings

#### Zebra Printers

- Use ZDesigner driver for best results
- Configure label size in ZDesigner settings

#### Brother Label Printers

- Use P-touch Editor for configuration
- Set custom paper size to exactly 2" x 2"

#### Standard Inkjet/Laser Printers

- Use high-quality label paper
- Test alignment with a single label before batch printing

## Printer Recommendations

### Recommended Printers for Label Maker

The following printers have been tested and work well with Label Maker:

#### Dedicated Label Printers

- **DYMO LabelWriter 450** - Excellent for thermal printing of 2" x 2" labels
- **Zebra GK420d** - Industrial-grade thermal printer with excellent durability
- **Brother QL-800** - Fast thermal printing with good resolution

#### Standard Printers

- **HP OfficeJet Pro** series - Good color accuracy and label handling
- **Epson WorkForce** series - Excellent for high-volume label printing
- **Brother laser printers** - Good for black and white labels with sharp text

When selecting a printer, consider:

1. **Volume**: How many labels you'll print daily
2. **Speed**: Labels per minute requirements
3. **Resolution**: Minimum 300 DPI for barcode clarity
4. **Media support**: Ability to handle your preferred label type
5. **Cost**: Both initial purchase and per-label printing costs
