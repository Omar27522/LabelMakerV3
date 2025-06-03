<h3>Management Section</h3>

<?php echo basename(__FILE__); ?>
                <div class="container">
        <main>
        <?php navigationButtons('Management'); ?>
<details class="mainNavigationButtons"><summary><span id="ManagementSection" class="<?= $buttons ?>"><?= $details ?></span></summary>
    <summary><a href="#UserSection"><span class="<?= $buttons1 ?>"><?= $details1 ?></span></a></summary>
    <summary><a href="#LabelsSection"><span class="<?= $buttons2 ?>"><?= $details2 ?></span></a></summary>
    <summary><a href="#SettingsSection"><span class="<?= $buttons3 ?>"><?= $details3 ?></span></a></summary>
    </details>
    

            <section>
                <aside style="display: grid;
  grid-template-columns: 1fr 1fr; /* Creates two equal columns */
  gap: 10px; /* Adds space between columns */
">


<fieldset class="instructions">
                <legend class="highlight">
                <span class="button" style="display:inline;">Label Maker</span>
                </legend>
                <ul>
                    <li><strong>Control Buttons:</strong>
                        <ul>
                            <li>Always on Top: Keeps the window on top of other windows</li>
                            <li>Settings: Opens the Settings window</li>
                            <li>Labels: Opens the Labels directory selection window</li>
                            <li>Reset: Resets the Label to default settings</li>
                        </ul>
                    </li>
                    <li><strong>Create New Label Record Field:</strong></li>
                        <ul>
                            <li><strong>Product Name Line 1:</strong></li>
                            <li><strong>Product Name Line 2:</strong></li>
                            <li><strong>Variant:</strong></li>
                            <li><strong>UPC Code:</strong></li>
                        </ul>
                    </li>
                    <li><strong>Navigation:</strong></li>
                        <ul>
                            <li>Preview: When All text fields are filled, this will open a preview window</li>
                            <li>View Files: Opens the View Files window</li>
                        </ul>
                    </li>
                </ul>
</fieldset>

                <div class="image-map-container" id="labelMaker">
                    <img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/LabelMakerV3/media/software/label_maker.jpg" style="width: 100%;" alt="LabelMakerV3 Software" class="clickable-image">
                    
                    <!-- Clickable areas - these are positioned with CSS -->
                    <a href="#labelMaker"><div class="clickable-area" id="lmTop" data-tooltip="Always on Top of other windows" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Always on Top of other windows</h3>
                        </div>
                    </div></a>

                    <a href="#returnsData"><div class="clickable-area" id="lmSettings" data-tooltip="Settings Button" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Settings</h3>
                            Brings up a new window.
                            <p>Labels
                                <br />
                                Records
                            </p>
                        </div>
                    </div></a>

                    <a href="#returnsData"><div class="clickable-area" id="lmLabels" data-tooltip="Labels Button" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Labels Button</h3>
                            <p>
                            Brings up a new window.
                            </p>
                        </div>
                    </div></a>

                    <a href="#returnsData"><div class="clickable-area" id="lmReset" data-tooltip="Reset Button" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Reset Button</h3>
                            <p>
                            Resets the Label to default settings.
                            </p>
                        </div>
                    </div></a>
                    
                    <div class="clickable-area" id="lmProductNameLine1" data-tooltip="Product Name Line 1" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Product Name Line 1</h3>
                            <p>Enter the product name for the package here.</p>
                        </div>
                    </div>
                    
                    <div class="clickable-area" id="lmProductNameLine2" data-tooltip="Product Name Line 2" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Product Name Line 2</h3>
                            <p>Enter the product name for the package here.</p>
                        </div>
                    </div>
                    
                    <div class="clickable-area" id="lmVariant" data-tooltip="Variant" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Variant</h3>
                            <p>Enter the variant for the package here.</p>
                        </div>
                    </div>
                    
                    <div class="clickable-area" id="lmUPC" data-tooltip="UPC" tabindex="0">
                        <div class="tooltip-content">
                            <h3>UPC</h3>
                            <p>Enter the UPC for the package here.</p>
                        </div>
                    </div>
                    
					<div class="clickable-area" id="lmPreview" data-tooltip="Preview" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Preview</h3>
                            <p>Preview the Label before printing.</p>
                        </div>
                    </div>
					
                    <div class="clickable-area" id="lmViewFiles" data-tooltip="View Files" tabindex="0">
                        <div class="tooltip-content">
                            <h3>View Files</h3>
                            <p>Opens the View Files window.</p>
                        </div>
                    </div>
					
                   
					
					
					
                    
                </div>
                
                
				<aside>        
            </section>
            
            <aside style="display: grid;
  grid-template-columns: 1fr 1fr; /* Creates two equal columns */
  gap: 10px; /* Adds space between columns */
">


<fieldset class="instructions">
                <legend class="highlight">
                <span class="button" style="display:inline;">View Files</span>
                </legend>
                <ul>
                    <li><strong>Control Buttons:</strong>
                        <ul>
                            <li>Pin: Pins the window to the top of the screen</li>
                            <li>Margnify: Zooms in on the text</li>
                            <li>Plus: Zooms in on the text</li>
                            <li>Printer: Mirror Print</li>
                            <li>Paper: minimizes the window after each print</li>
                            <li>Light: Adjusts the lighting of the image</li>
                        </ul>
                    </li>
                    <li><strong>Search:</strong></li>
                        <ul>
                            <li>Search for a label by tracking number, name, or SKU</li>
                            <li>Enter the number, name, or SKU in the search field</li>
                            <li>Open the label</li>
                            <li>Print</li>
                        </ul>
                    </li>
                    <li><strong>System Links:</strong></li>
                        <ul>
                            <li>Reverse Inbound</li>
                            <li>Receive</li>
                        </ul>
                    </li>
                </ul>
</fieldset>

                <div class="image-map-container" id="return">
                    <img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/LabelMakerV3/media/software/view_files.jpg" alt="LabelMakerV3 Software" class="clickable-image" style="width: 100%;">
                    
                    <!-- Clickable areas - these are positioned with CSS -->
                    <a href="#return"><div class="clickable-area" id="clReturn" data-tooltip="Return Button" tabindex="0">
                        <div class="tooltip-content">
                            <h3>View Files</h3>
                        </div>
                    </div></a>

                    <a href="#returnsData"><div class="clickable-area" id="clReturnsData" data-tooltip="Returns Data Button" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Returns Data</h3>
                            Brings up a new window.
                            <p>Labels
                                <br />
                                Records
                            </p>
                        </div>
                    </div></a>

                    <a href="#returnsData"><div class="clickable-area" id="clPinButton" data-tooltip="Pin Button" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Pin Button</h3>
                            <p>
                            Pinned window.
                            </p>
                        </div>
                    </div></a>
                    
                    <div class="clickable-area" id="clTrackingNumber" data-tooltip="Tracking Number" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Tracking Number Field</h3>
                            <p>Enter the tracking number for the package here. A browser window will open CTRL+V the tracking number.</p>
                        </div>
                    </div>
                    
                    <div class="clickable-area" id="clSKU" data-tooltip="SKU Field" tabindex="0">
                        <div class="tooltip-content">
                            <h3>SKU Field</h3>
                            <p>This field is not enabled until a tracking number is entered. Enter the SKU for the package here.</p>
                        </div>
                    </div>
                    
					<div class="clickable-area" id="clMirrorPrint" data-tooltip="Mirror Print" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Mirror Print</h3>
                            <p>Prints the Label in Mirror View.</p>
                        </div>
                    </div>
					
                    <div class="clickable-area" id="clTransparency" data-tooltip="Action Buttons" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Transparency</h3>
                            <p>Enables or Disables window Transparency, when out of focus.</p>
							<p>Default Transparency set to: 7.</p>
                            <!-- <ul>
                                <li><strong>Preview:</strong> Shows how the label will look</li>
                                <li><strong>View Files:</strong> Browse label files you've created</li>
                            </ul> -->
                        </div>
                    </div>
                    
					<div class="clickable-area" id="clPrint" data-tooltip="Print" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Print</h3>
                            <p>Label will be recorded into the system, and the software will print a label by default.</p>
                            <ul>
                                <li><strong>Enabled:</strong> Label will print.</li>
                                <li><strong>Disabled:</strong> Label will not print.</li>
                            </ul>
                        </div>
                    </div>
					
					
                    <div class="clickable-area" id="clPrintOptions" data-tooltip="Print Options" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Print Options</h3>
                            <p>Configure how your label will be printed:</p>
                            <ul>
                                <li><strong>MP:</strong> Mirror Print - prints the label in reverse for thermal printers</li>
                                <li><strong>Print:</strong> Enable/disable printing (will still record the label if disabled)</li>
                                <li><strong>TR:</strong> Enable Transparency - makes the program transparent when inactive</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                
				<aside>

        </main>

        <fieldset class="highlight-box">
                <legend>
                    <span class="button">Settings</span>
                </legend>

                <aside style="display: grid; grid-template-columns: 1fr 1fr;">
                    <img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/Screen-Shots/Label%20Maker%20Settings.jpg" alt="LabelMakerV3 Software" class="clickable-image" style="width: 100%;">
                <div>
                <p>The Management section (blue button on the Welcome screen) provides access to administrative functions for managing your label database and integrations.</p>
                <p>This section includes:</p>
                <ul>
                    <li>Large Font Size</li>
                    <li>Medium Font Size</li>
                    <li>Barcode Width</li>
                    <li>Barcode height</li>
                    <li>Upload CSV File</li>
                    <li>Transparency Level</li>
                    <li>Overlay over windows setting</li>
                    <li>Save Settings</li>
                </ul>
                </div
                </aside>
                </fieldset>