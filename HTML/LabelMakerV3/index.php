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
            <?php include 'creatingLabels/creatingLabels.php'; ?>
            <?php include 'noRecordLabels/noRecordLabels.php'; ?>
            <?php include 'googleSheetIntegration/googleSheetIntegration.php'; ?>
            
            
            
            
            
        </main>
    </div>
    
    <footer>
        <p>&copy; <?php echo date('M Y'); ?> LabelMakerV3. All rights reserved.</p>
    </footer>
</body>
</html>