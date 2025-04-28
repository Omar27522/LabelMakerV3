# CSV Import Guide

## Table of Contents

- [Overview](#overview)
- [CSV File Format](#csv-file-format)
- [Required Columns](#required-columns)
- [Product Name Format](#product-name-format)
- [Variant Format](#variant-format)
- [UPC Code Requirements](#upc-code-requirements)
- [Sample CSV Files](#sample-csv-files)
- [Label Output Format](#label-output-format)
- [Import Process](#import-process)
- [Troubleshooting](#troubleshooting)

## Overview

Label Maker allows you to import multiple labels at once using a CSV (Comma-Separated Values) file. This guide explains how to format your CSV file correctly for successful imports.

## CSV File Format

The CSV file should follow these formatting rules:

- Use comma (,) as the delimiter
- Include a header row with column names
- Text values may be enclosed in double quotes (recommended for values containing commas)
- Save the file with UTF-8 encoding for best compatibility
- File extension should be `.csv`

## Required Columns

Your CSV file must include these two columns with exact spelling and capitalization:

1. **Goods Name** - The product name that will appear on the label
2. **Goods Barcode** - The 12-digit UPC code for the barcode

**Note:** The order of columns doesn't matter. The application identifies columns by their names, not their positions in the file.

Example header row:
```
Goods Name,Goods Barcode
```

## Product Name Format

The "Goods Name" column supports a special format that controls how text appears on the label:

### Basic Format
A simple product name will be displayed on a single line:
```
Quantum Flux Capacitor
```

### Name with Variant
To include a variant, add a hyphen (-) followed by the variant name:
```
Quantum Flux Capacitor - PLUTONIUM_FREE
```

The text before the hyphen will be the product name, and the text after will be the variant.

### Automatic Line Wrapping
The software automatically splits long product names:
- First line: Maximum 18 characters
- Second line: Maximum 20 characters
- Any remaining text is truncated

For example, "Super Deluxe Quantum Flux Capacitor" would be displayed as:
```
Super Deluxe
Quantum Flux Capacitor
```

## Variant Format

Variants are extracted from the product name using the hyphen (-) separator:

- Everything after the last hyphen is considered the variant
- Variants are typically displayed in uppercase
- No specific character limit, but shorter is better for readability
- Variants appear centered on the label below the product name

Examples:
```
Banana Phone - YELLOW
Invisible Paint - CLEAR
Moon Cheese - BLEU
```

## UPC Code Requirements

The "Goods Barcode" column must follow these rules:

- Exactly 12 digits (no more, no less)
- Numbers only (0-9)
- No spaces, dashes, or other characters
- Scientific notation (e.g., 1.23456e+11) will be converted to standard format
- Decimal values will have the decimal portion removed

Valid examples:
```
123456789012
987654321098
```

Invalid examples:
```
123-456-789-012  (contains dashes)
12345678901     (only 11 digits)
1234567890123   (13 digits)
ABCDEFGHIJKL    (contains letters)
```

## Sample CSV Files

### Basic Example

```
Goods Name,Goods Barcode
Quantum Flux Capacitor,314159265358
Banana Phone,123456789012
Invisible Paint,234567890123
Moon Cheese,345678901234
```

### Example with Variants

```
Goods Name,Goods Barcode
Quantum Flux Capacitor - PLUTONIUM_FREE,314159265358
Banana Phone - YELLOW,123456789012
Invisible Paint - CLEAR,234567890123
Moon Cheese - BLEU,345678901234
Unicorn Kibble - RAINBOW,456789012345
Gravity Boots - ORBITER,567890123456
```

## Label Output Format

Labels created from CSV imports have the following characteristics:

### Label Dimensions
- Width: 600 pixels (2 inches at 300 DPI)
- Height: 600 pixels (2 inches at 300 DPI)

### Label Elements
1. **Product Name**: Positioned at the top of the label
   - Line 1: First 18 characters or first few words that fit within 18 characters
   - Line 2 (if needed): Next 20 characters or words that fit within 20 characters

2. **Variant**: Centered in the middle of the label (if provided)

3. **Barcode**: 
   - UPC-A format
   - Positioned at the bottom of the label
   - Includes human-readable UPC number
   - High-quality 600 DPI rendering for optimal scanning

### Output File Format
- PNG image files
- Saved to the last used directory or user's Documents/Labels folder
- Filename format: `ProductName_Variant_label_UPCCode.png`
- If the product name has two lines, the format becomes: `ProductName Line1 ProductName Line2_Variant_label_UPCCode.png`

## Import Process

To import labels from a CSV file:

1. Open the Settings window
2. Scroll to the "Batch Import" section
3. Click "Upload CSV File"
4. Select your CSV file
5. The application will process the file and create labels for each row
6. A progress bar will show the import status
7. A confirmation message will show the number of labels successfully imported

## Troubleshooting

### Common Import Issues

1. **Invalid UPC Codes**
   - Error: "Skipping invalid barcode"
   - Solution: Ensure all UPC codes are exactly 12 digits (numbers only)

2. **Missing Required Columns**
   - Error: "Missing required columns in CSV"
   - Solution: Verify your CSV has both "Goods Name" and "Goods Barcode" columns with exact spelling and capitalization

3. **Character Encoding Problems**
   - Symptom: Special characters appear as gibberish
   - Solution: Save your CSV with UTF-8 encoding

4. **Scientific Notation**
   - Symptom: Some spreadsheet programs may convert large numbers to scientific notation
   - Solution: Format cells as "Text" before entering UPC codes, or use leading apostrophe ('123456789012)

5. **Hyphen in Product Name**
   - Symptom: Variant is extracting part of the product name
   - Solution: Only use hyphens to separate variants. If you need a hyphen in the product name, consider using an en dash (–)

6. **Label Counter**
   - Note: Each successfully generated label increases the application's label counter, which is displayed in the main window
