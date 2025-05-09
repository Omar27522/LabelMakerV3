<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LabelMakerV3 User Guide</title>
    <link rel="stylesheet" href="styles/styles.css">
    <link rel="stylesheet" href="styles/gettingStarted.css">
    <link rel="stylesheet" href="styles/mainNavigation.css">
</head>
<body>
    <header>
        <h1>LabelMakerV3 User Guide</h1>
    </header>
    
    <nav>
        <ul>
            <li><a href="#introduction">Introduction</a></li>
            <li><a href="#getting-started">Getting Started</a></li>
            <li><a href="#main-navigation">Main Navigation</a></li>
            <li><a href="#creating-labels">Creating Labels</a></li>
            <li><a href="#no-record-labels">No Record Labels</a></li>
            <li><a href="#google-sheets">Google Sheets</a></li>
        </ul>
    </nav>
    
    <div class="container">
        <div class="toc">
            <h3>Table of Contents</h3>
            <ul>
                <li><a href="#introduction">1. Introduction</a></li>
                <li><a href="#getting-started">2. Getting Started</a></li>
                <li><a href="#main-navigation">3. Main Navigation</a></li>
                <li><a href="#creating-labels">4. Creating Labels</a></li>
                <li><a href="#no-record-labels">5. No Record Labels</a></li>
                <li><a href="#google-sheets">6. Google Sheets Integration</a></li>
            </ul>
        </div>
        
        <main>
            <?php
            // PHP code can be placed here if needed
            ?>
            
            <?php include 'introduction.php'; ?>
            <?php include 'gettingStarted.php'; ?>
            <?php include 'mainNavigation.php'; ?>
            
            <section id="creating-labels">
                <h2>4. Creating Labels</h2>
                <p>Creating labels is the core functionality of LabelMakerV3. This section will guide you through the process of creating, previewing, and saving labels for your products.</p>
                
                <h3>Basic Label Creation</h3>
                <div class="highlight-box">
                    <p><strong>Quick Tip:</strong> Always verify your UPC code is correct before creating a label, as this generates the barcode.</p>
                </div>
                
                <p>To create a new label:</p>
                <ol>
                    <li>From the Welcome screen, click the <span class="button green">User</span> button to access the Label Maker interface</li>
                    <li>You'll see the Label Maker screen</li>
                    <li>Fill in the product information fields:
                        <ul>
                            <li><strong>Product Name Line 1:</strong> Enter the main product name (e.g., "Stainless Steel Water Bottle")</li>
                            <li><strong>Line 2 (optional):</strong> Enter additional product information if needed (e.g., "BPA Free")</li>
                            <li><strong>Variant:</strong> Enter the product variant, model, or SKU (e.g., "200234STNWBV1Standard")</li>
                            <li><strong>UPC Code (12 digits):</strong> Enter the Universal Product Code (e.g., "010101010101")</li>
                        </ul>
                    </li>
                </ol>
                
                <h3>Previewing Labels</h3>
                <p>Before saving or printing a label, you can preview how it will look:</p>
                <ol>
                    <li>After filling in the product information, click the <strong>Preview</strong> button</li>
                    <li>A new window will open showing exactly how your label will appear</li>
                </ol>
                
                <h3>Saving and Printing Labels</h3>
                <p>Once you're satisfied with your label preview:</p>
                <ol>
                    <li>Click the <strong>Save Label</strong> button in the preview window</li>
                    <li>The label will be saved as a PNG image file in your designated labels directory</li>
                    <li>To print the label, you can either:
                        <ul>
                            <li>Print directly from the preview window by clicking <strong>Print</strong></li>
                            <li>Open the saved PNG file and print it using your preferred image viewer</li>
                        </ul>
                    </li>
                </ol>
                
                <div class="highlight-box">
                    <p><strong>Note:</strong> Labels are automatically saved with a filename that includes the product name, variant, and UPC code for easy identification.</p>
                </div>
            </section>
            
            <section id="no-record-labels">
                <h2>5. No Record Labels</h2>
                <p>Sometimes you may need to print a label quickly without recording it in your database. LabelMakerV3 provides a special "No Record Label" feature for these situations.</p>
                
                <h3>When to Use No Record Labels</h3>
                <p>No Record Labels are useful when:</p>
                <ul>
                    <li>You need a temporary label</li>
                    <li>You're testing label printing</li>
                    <li>You need a one-time label that doesn't need to be stored</li>
                    <li>You're creating a label for an item that isn't in your regular inventory</li>
                </ul>
            </section>
            
            <section id="google-sheets">
                <h2>6. Google Sheets Integration</h2>
                <p>LabelMakerV3 offers powerful integration with Google Sheets, allowing you to track your shipments and inventory in the cloud.</p>
                
                <h3>Benefits of Google Sheets Integration</h3>
                <p>Integrating LabelMakerV3 with Google Sheets provides several advantages:</p>
                <ul>
                    <li>Access your inventory data from anywhere with internet access</li>
                    <li>Share inventory information with team members</li>
                    <li>Create automatic backups of your label data</li>
                    <li>Generate reports and analytics using Google Sheets features</li>
                    <li>Synchronize data across multiple devices</li>
                </ul>
            </section>
        </main>
    </div>
    
    <footer>
        <p>&copy; <?php echo date('Y'); ?> LabelMakerV3. All rights reserved.</p>
    </footer>
</body>
</html>