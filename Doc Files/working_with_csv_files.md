## 9. Working with CSV Files

LabelMakerV3 can work with CSV (Comma-Separated Values) files to import and export data. This section explains how to use CSV files with the application.

### Understanding CSV Data Structure

CSV files are simple text files that store tabular data (like a spreadsheet) in a plain text format. Each line in the file represents a row of data, and values within a row are separated by commas.

LabelMakerV3 uses CSV files for:
- Importing product data in bulk
- Exporting label records
- Backing up your database
- Sharing data with other systems

The CSV files provided with LabelMakerV3 contain structured data about your products, including:
- Product names
- SKUs/Variants
- UPC codes
- Categories
- Pricing information
- Other product attributes

### Importing Data from CSV Files

To import data from a CSV file:

1. Prepare your CSV file with the required columns and data format
2. From the appropriate section of LabelMakerV3 (such as the Returns Data screen), look for an import option
3. Select the CSV file you want to import
4. Map the columns in your CSV file to the fields in LabelMakerV3
5. Confirm the import operation

The application will read the data from your CSV file and add it to the database.

### Exporting Data to CSV Files

To export your label data to a CSV file:

1. Navigate to the section containing the data you want to export (such as Returns Data)
2. Look for an export or "Save as CSV" option
3. Select where you want to save the CSV file
4. Choose which fields to include in the export (if this option is available)
5. Confirm the export operation

The application will create a CSV file containing your selected data.

### Troubleshooting CSV Issues

If you encounter problems with CSV files:

1. **Format Issues**: Ensure your CSV file uses the correct format:
   - Values should be separated by commas
   - Text containing commas should be enclosed in quotes
   - Each record should be on a new line

2. **Character Encoding**: CSV files should use UTF-8 encoding to properly display special characters

3. **Column Mapping**: Make sure the columns in your CSV file match what LabelMakerV3 expects:
   - Check column headers
   - Verify data is in the correct columns
   - Ensure required fields are present

4. **Data Validation**: Check that your data meets any validation requirements:
   - UPC codes should be 12 digits
   - Required fields should not be empty
   - Data should be in the expected format (text, numbers, dates, etc.)
