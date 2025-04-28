# Logging and Error Handling Guide

## Table of Contents

- [Overview](#overview)
- [Log File Location](#log-file-location)
- [Log Format](#log-format)
- [Error Types](#error-types)
- [Common Error Messages](#common-error-messages)
- [Troubleshooting with Logs](#troubleshooting-with-logs)
- [Advanced Log Analysis](#advanced-log-analysis)
  - [Enabling Debug Logging](#enabling-debug-logging)
  - [Log File Management](#log-file-management)
  - [Common Patterns in Logs](#common-patterns-in-logs)
  - [Edge Cases and Unusual Errors](#edge-cases-and-unusual-errors)
  - [Using Logs for Support](#using-logs-for-support)

## Overview

Label Maker uses a comprehensive logging system to track application activity, errors, and warnings. This guide explains how to use the logging system to troubleshoot issues and understand error messages.

## Log File Location

Log files are stored in the `logs` directory, but the exact location depends on how you're running the application:

### Python Script Method

When running the application using the Python script (`main.pyw`), log files are stored in:

```
[Application Directory]/logs/label_maker_YYYYMM.log
```

### Executable Method

When running the application using the compiled executable ("Label Maker V3.exe"), log files are stored in:

```
[Installation Directory]/logs/label_maker_YYYYMM.log
```

In both cases, `YYYYMM` represents the year and month (e.g., `label_maker_202502.log` for February 2025).

The application uses a rotating file system with the following characteristics:
- Monthly log files (new file each month)
- Maximum file size of 5MB
- Keeps up to 5 backup files when size limit is reached
- Files are named with a numeric suffix when rotated (e.g., `label_maker_202502.log.1`)

## Log Format

Each log entry follows this format:

```
YYYY-MM-DD HH:MM:SS,mmm - LabelMaker - LEVEL - Message
```

Example:
```
2025-02-26 10:15:30,123 - LabelMaker - ERROR - Failed to process CSV: Invalid UPC code format
```

### Log Levels

The application uses standard logging levels:

| Level | Description |
|-------|-------------|
| INFO | Normal application operations |
| WARNING | Potential issues that don't prevent operation |
| ERROR | Problems that prevent a specific operation |
| CRITICAL | Severe issues that may cause application failure |

## Error Types

The application handles several types of errors:

### 1. CSV Processing Errors

These occur when importing labels from CSV files:
- Invalid UPC codes
- Missing required columns
- File format issues

### 2. Barcode Generation Errors

These occur when generating barcode images:
- Invalid UPC format
- Image processing failures

### 3. File System Errors

These occur when reading or writing files:
- Permission issues
- Invalid file paths
- Disk space problems

### 4. UI and Window Management Errors

These occur in the user interface:
- Window creation failures
- Control rendering issues

### 5. Printing Errors

These occur when printing labels:
- Printer connection issues
- Print job failures

## Common Error Messages

### CSV Import Errors

| Log Message | User Message | Cause | Solution |
|-------------|--------------|-------|----------|
| `Skipping invalid barcode: {barcode}` | Not shown to user | UPC code is not 12 digits | Ensure UPC codes are exactly 12 digits |
| `Error processing CSV: {error}` | "Failed to process CSV file" | General CSV processing error | Check CSV format and content |
| `Missing required columns in CSV` | "Missing required columns" | CSV is missing required columns | Ensure CSV has "Goods Name" and "Goods Barcode" columns |

### Barcode Generation Errors

| Log Message | User Message | Cause | Solution |
|-------------|--------------|-------|----------|
| `Error generating barcode: {error}` | "Failed to generate preview" | Invalid UPC code or barcode library error | Verify UPC code format |
| `Error generating label: {error}` | "Failed to generate preview" | Error creating complete label | Check input data and system resources |

### File System Errors

| Log Message | User Message | Cause | Solution |
|-------------|--------------|-------|----------|
| `Failed to read directory: {error}` | "Failed to read directory" | Directory access issues | Check permissions and path validity |
| `Failed to save label: {error}` | "Failed to save label" | File write error | Check disk space and permissions |

### Printing Errors

| Log Message | User Message | Cause | Solution |
|-------------|--------------|-------|----------|
| `Failed to print: {error}` | "Failed to print" | Printer connection or job error | Verify printer status and connection |

## Troubleshooting with Logs

Follow these steps to use logs for troubleshooting:

1. **Locate the log file**:
   - Navigate to the `logs` directory in the application folder
   - Open the most recent log file (highest date in filename)

2. **Identify the error**:
   - Search for "ERROR" or "WARNING" entries
   - Note the timestamp to correlate with when the issue occurred

3. **Understand the context**:
   - Look at log entries before the error for related operations
   - Check if multiple related errors occurred in sequence

4. **Apply the solution**:
   - Refer to the [Common Error Messages](#common-error-messages) section
   - Implement the recommended solution

## Advanced Log Analysis

For persistent or complex issues:

### Enabling Debug Logging

By default, the application logs at INFO level. To enable more detailed logging:

1. Create a file named `debug.flag` in the application directory
2. Restart the application
3. The log will now include DEBUG level messages with more details

### Log File Management

- Log files are automatically rotated and managed
- Old log files can be safely deleted if disk space is a concern
- For support purposes, you may be asked to provide log files

### Common Patterns in Logs

- Multiple "Skipping invalid barcode" warnings indicate a CSV with many invalid UPCs
- Repeated "Failed to generate barcode" errors may indicate a system library issue
- File system errors often point to permission problems or disk space issues

### Edge Cases and Unusual Errors

The following edge cases may produce unique log patterns that require special attention:

#### Large Batch Processing

When processing extremely large CSV files (10,000+ records):
- Log entries may show `"Memory allocation error"` or `"Process timeout"`
- Solution: Split the CSV into smaller batches of 5,000 records or fewer

#### Network Printers

When using network printers:
- Intermittent `"Failed to connect to printer"` errors may appear
- Log entries may show varying timeout durations
- Solution: Increase network timeout settings or use a local printer

#### Unicode and Special Characters

When product names contain non-ASCII characters:
- Log may show `"Encoding error"` or `"UnicodeEncodeError"`
- Labels may print with missing or incorrect characters
- Solution: Ensure all text is UTF-8 encoded and check printer font compatibility

#### Concurrent Access

When multiple users access the application simultaneously:
- Log may show `"File lock error"` or `"Access denied"`
- Configuration changes may not persist
- Solution: Implement file locking or use separate configuration files per user

#### Disk Space Exhaustion

When system disk space is critically low:
- Log rotation may fail with `"Disk full"` errors
- Application may crash without proper error logging
- Solution: Monitor disk space and maintain at least 500MB free space

#### System Sleep/Hibernation

When system enters sleep mode during operations:
- Log may show `"Connection reset"` or `"Unexpected termination"`
- Print jobs may be incomplete
- Solution: Disable sleep mode during batch operations

### Using Logs for Support

When contacting support:

1. Describe the exact steps that led to the error
2. Provide the relevant section of the log file
3. Include the error message shown in the application
4. Note your operating system and application version
