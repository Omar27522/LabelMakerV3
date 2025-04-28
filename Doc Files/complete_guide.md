---
title: "LabelMakerV3 User Guide"
author: "Prepared for User"
date: "April 18, 2025"
geometry: "margin=1in"
output: pdf_document
toc: true
toc_depth: 3
---

# LabelMakerV3 User Guide

## 1. Introduction

Welcome to the LabelMakerV3 User Guide! This comprehensive guide will help you learn how to use the LabelMakerV3 application to create, manage, and print labels for your products. Whether you're a small business owner, an inventory manager, or someone who needs to organize products, this guide will walk you through every aspect of the application.

### Purpose of this Guide

This guide is designed to provide step-by-step instructions for using all features of the LabelMakerV3 application. By following this guide, you'll learn how to:

- Create and print professional product labels
- Manage your product inventory
- Integrate with Google Sheets for data tracking
- Handle product returns
- Configure application settings
- Troubleshoot common issues

### Overview of LabelMakerV3

LabelMakerV3 is a powerful yet user-friendly application that helps you create and manage product labels. The application allows you to:

- Generate barcodes automatically
- Create labels with product names, variants, and UPC codes
- Preview labels before printing
- Track your inventory through Google Sheets integration
- Manage product returns and shipping records
- Customize application settings for your specific needs

The application is designed with simplicity in mind, featuring an intuitive interface that makes label creation quick and easy, even for users with limited computer experience.

### Who This Guide Is For

This guide is written specifically for users with little to no computer knowledge. We've broken down complex processes into simple, easy-to-follow steps with clear explanations and visual aids. Whether you're using LabelMakerV3 for the first time or need a refresher on specific features, this guide will provide the information you need.

### What You'll Learn

By the end of this guide, you'll be able to:

1. Navigate the LabelMakerV3 interface confidently
2. Create and print professional labels for your products
3. Set up Google Sheets integration for inventory tracking
4. Manage product returns and shipping records
5. Configure application settings to suit your needs
6. Troubleshoot common issues that may arise

Let's get started with learning how to use LabelMakerV3!
## 2. Getting Started

### System Requirements

Before installing LabelMakerV3, ensure your computer meets the following requirements:

- Windows operating system (Windows 10 or later recommended)
- At least 4GB of RAM
- 500MB of available disk space
- Internet connection (for Google Sheets integration)
- Python 3.10 or later (included in the installation package)

### Installation Process

To install LabelMakerV3 on your computer:

1. Double-click on the LabelMakerV3 installer file you received
2. Follow the on-screen instructions in the installation wizard
3. When prompted, choose the installation location (the default location is recommended)
4. Wait for the installation to complete
5. Click "Finish" to complete the installation

### First Launch

After installation, you can launch LabelMakerV3 by:

1. Finding the LabelMakerV3 icon on your desktop and double-clicking it, or
2. Going to the Start menu, finding LabelMakerV3 in the programs list, and clicking on it

The first time you launch the application, it may take a few moments to initialize and set up necessary files.

### Understanding the Welcome Screen

When you first open LabelMakerV3, you'll see the Welcome screen:

![Welcome Screen](https://github.com/Omar27522/LabelMakerV3/blob/main/Screen-Shots/welcome.jpg))

The Welcome screen is your starting point for using LabelMakerV3. Let's look at the key elements:

1. **Title Bar**: At the top of the window, showing "Welcome" and window controls (minimize, maximize, close)

2. **Labels Counter**: Shows how many labels you've created (displays "0 Labels" when you first start)

3. **Application Name**: Displays "Label Maker V3"

4. **Main Navigation Buttons**:
   - **User** (green button): Access user-specific functions
   - **Management** (blue button): Access management features
   - **Labels** (orange button): Access label creation and management
   - **Settings** (gray button): Access application settings

5. **Connection Status**: At the bottom left, shows "Not Connected" if Google Sheets integration is not set up

6. **Version Number**: At the bottom right, shows the current version of the application (e.g., "Ver. 1.0.1.1")

This Welcome screen serves as your dashboard for navigating to different parts of the application. In the following sections, we'll explore each of these areas in detail.
## 3. Main Navigation

The LabelMakerV3 application is organized into four main sections, accessible from the Welcome screen. This section will help you understand how to navigate through these areas and what each one offers.

### User Section

The User section (green button on the Welcome screen) is designed for day-to-day label creation and printing tasks. This is where you'll spend most of your time if you're primarily creating labels for products.

When you click on the User button, you'll be taken to the Label Maker interface:

![Label Maker](/home/ubuntu/guide/images/Label Maker.jpg)

The Label Maker interface includes:

1. **Control Buttons**:
   - **Always on Top**: Keeps the window visible above other windows
   - **Settings**: Access label-specific settings
   - **Labels**: Shows how many labels you've created

2. **Product Information Fields**:
   - **Product Name Line 1**: Enter the main product name
   - **Line 2 (optional)**: Enter additional product information
   - **Variant**: Enter the product variant or model
   - **UPC Code (12 digits)**: Enter the Universal Product Code

3. **Action Buttons**:
   - **Preview**: Shows how the label will look
   - **View Files**: Browse label files you've created

### Management Section

The Management section (blue button on the Welcome screen) provides access to administrative functions for managing your label database and integrations.

This section includes:
- Database management
- User permissions (if applicable)
- System status information
- Integration management

### Labels Section

The Labels section (orange button on the Welcome screen) allows you to access and manage all the labels you've created.

When you click on the Labels button, you'll see a list of all your labels with options to:
- Search for specific labels
- Filter labels by various criteria
- Edit existing labels
- Delete labels
- Export label data

### Settings Section

The Settings section (gray button on the Welcome screen) allows you to configure the application according to your preferences.

When you click on the Settings button, you'll see the Settings screen:

![Settings](https://github.com/Omar27522/LabelMakerV3/blob/main/Screen-Shots/Settings.jpg)

The Settings screen includes:

1. **Labels Directory**: Set where label files are saved on your computer

2. **Transparency Settings**:
   - Enable/disable window transparency when inactive
   - Adjust transparency level (1-10)

3. **Google Sheets Integration**:
   - View connection status
   - Configure Google Sheets connection

4. **Log Management**:
   - Manage shipping logs
   - Migrate from legacy systems

5. **Action Buttons**:
   - **Cancel**: Exit without saving changes
   - **Save**: Save your settings changes

### Status Indicators

At the bottom of the Welcome screen, you'll find important status information:

1. **Connection Status** (bottom left): Shows whether you're connected to Google Sheets
   - "Not Connected" means Google Sheets integration is not set up
   - "Connected" means Google Sheets integration is active

2. **Version Number** (bottom right): Shows which version of LabelMakerV3 you're using

These status indicators help you quickly understand the current state of your application.
## 4. Creating Labels

Creating labels is the core functionality of LabelMakerV3. This section will guide you through the process of creating, previewing, and saving labels for your products.

### Basic Label Creation

To create a new label:

1. From the Welcome screen, click the green **User** button to access the Label Maker interface
2. You'll see the Label Maker screen:

![Label Maker](/home/ubuntu/guide/images/Label Maker.jpg)

3. Fill in the product information fields:
   - **Product Name Line 1**: Enter the main product name (e.g., "Stainless Steel Water Bottle")
   - **Line 2 (optional)**: Enter additional product information if needed (e.g., "BPA Free")
   - **Variant**: Enter the product variant, model, or SKU (e.g., "200234STNWBV1Standard")
   - **UPC Code (12 digits)**: Enter the Universal Product Code (e.g., "010101010101")

4. Here's an example of a filled-out form:

![Label Maker Label Creation](/home/ubuntu/guide/images/Label Maker Label Creation.jpg)

### Previewing Labels

Before saving or printing a label, you can preview how it will look:

1. After filling in the product information, click the **Preview** button
2. A new window will open showing exactly how your label will appear:

![Label Maker Label Creation Preview](/home/ubuntu/guide/images/Label Maker Label Creation Preview.jpg)

3. The preview shows:
   - Product name and additional information
   - Variant/SKU information
   - Barcode generated from the UPC code
   - UPC number displayed below the barcode

4. If you're satisfied with the label, click **Save Label** to save it
5. If you need to make changes, close the preview window and modify the information in the Label Maker screen

### Creating a New Label

If you want to create a completely new label (clearing all fields):

1. From the Label Maker screen, click the **Reset** button to clear all fields
2. Alternatively, you can click **Create New Label** if that option is available:

![Create New Label](/home/ubuntu/guide/images/Create New Label.jpg)

3. Fill in the information for your new label
4. Preview and save as described above

### Viewing Label Files

To view the labels you've created:

1. From the Label Maker screen, click the **View Files** button
2. A file browser will open showing your saved label files:

![Label Maker View Files](/home/ubuntu/guide/images/Label Maker Viw Files.jpg)

3. You can:
   - Double-click a label file to open it
   - Right-click for additional options
   - Sort files by name, date, or type
   - Search for specific label files

### Label Settings

You can customize how labels are created and displayed:

1. From the Label Maker screen, click the **Settings** button
2. The Label Maker Settings window will appear:

![Label Maker Settings](/home/ubuntu/guide/images/Label Maker Settings.jpg)

3. Here you can adjust:
   - Label size and dimensions
   - Font settings
   - Barcode type and size
   - Print settings
   - Default values

4. After making changes, click **Save** to apply them or **Cancel** to discard changes

### Understanding Label Output

When you save a label, LabelMakerV3 creates a PNG image file that looks like this:

![Sample Label](/home/ubuntu/guide/images/Stainless Steel Water Bottle_200234STNWBV1Standard_label_910031470224.png)

The label includes:
- Product name at the top
- Variant/SKU information in the middle
- Barcode generated from the UPC code
- UPC number displayed below the barcode

These label files can be printed directly or used in other applications as needed.
## 5. No Record Labels

Sometimes you may need to print a label quickly without recording it in your database. LabelMakerV3 provides a special "No Record Label" feature for these situations.

### When to Use No Record Labels

No Record Labels are useful when:
- You need a temporary label
- You're testing label printing
- You need a one-time label that doesn't need to be stored
- You're creating a label for an item that isn't in your regular inventory

### Creating a No Record Label

To create a No Record Label:

1. From the Welcome screen, navigate to the No Record Label section (this may be accessible through the User section or directly from the Welcome screen)

2. You'll see the No Record Label screen:

![No Record Label](/home/ubuntu/guide/images/No Record Label.jpg)

3. The No Record Label screen includes:
   - A title explaining this is for printing labels without recording them
   - A **Return** button to go back to the previous screen
   - A **Pin** option to keep the window on top
   - An **SKU** field to enter the product SKU or identifier
   - A **Mirror Print** option with color selection
   - A **Print Label** button to print the label

4. Enter the SKU or product identifier in the SKU field

5. If needed, enable Mirror Print by clicking the colored square (this is useful for certain types of printers or special label applications)

6. Click the **Print Label** button to print your label

### Mirror Printing Option

The Mirror Print option reverses the label image horizontally, which is useful for:
- Heat transfer applications
- Certain types of transparent labels
- Special printing materials that require reversed images

To use Mirror Print:
1. Click the colored square next to "Mirror Print" to enable it
2. The square will change color to indicate it's active
3. When you print the label, the image will be reversed horizontally

### Printing Without Recording

When you use the No Record Label feature, the label will be printed but no record of it will be saved in your database. This means:
- The label won't appear in your label count on the Welcome screen
- The label won't be included in any reports or exports
- The label won't be visible in the Returns Data section

This feature is designed for convenience and flexibility when you need a quick label without the overhead of recording it in your system.
## 6. Google Sheets Integration

LabelMakerV3 offers powerful integration with Google Sheets, allowing you to track your shipments and inventory in the cloud. This section explains how to set up and use this integration.

### Benefits of Google Sheets Integration

Integrating LabelMakerV3 with Google Sheets provides several advantages:
- Access your inventory data from anywhere with internet access
- Share inventory information with team members
- Create automatic backups of your label data
- Generate reports and analytics using Google Sheets features
- Synchronize data across multiple devices

### Prerequisites

Before setting up Google Sheets integration, make sure you have:

1. A Google account
2. A Google Sheet that you want to write data to
3. Python libraries: `gspread` and `oauth2client` (these are included with LabelMakerV3, but if you're developing your own integration, you'll need to install them)

### Setting Up Google Sheets API Access

To use Google Sheets with LabelMakerV3, you need to set up API access:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - In the sidebar, click on "APIs & Services" > "Library"
   - Search for "Google Sheets API" and click on it
   - Click "Enable"
4. Create a service account:
   - In the sidebar, click on "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Enter a name for the service account and click "Create"
   - Skip the optional steps and click "Done"
5. Create a key for the service account:
   - In the service accounts list, click on the email address of the service account you just created
   - Click on the "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Select "JSON" and click "Create"
   - The key file will be downloaded to your computer
6. Rename the downloaded file to `credentials.json` and place it in the root directory of the LabelMakerV3 application

### Setting Up Your Google Sheet

Before configuring LabelMakerV3, you need to prepare your Google Sheet:

1. Create a new Google Sheet or use an existing one
2. Share the Google Sheet with the service account ema
(Content truncated due to size limit. Use line ranges to read in chunks)
