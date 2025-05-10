<h3>Management Section</h3>
<?php echo '<h1>' . basename(__FILE__) . '</h1>'; ?>
                <div class="container">
        <main>
            <section>
                <aside style="display: grid;
  grid-template-columns: 1fr 1fr; /* Creates two equal columns */
  gap: 10px; /* Adds space between columns */
">


<fieldset class="instructions">
                <legend class="highlight">
                    <span class="button green" style="display:inline;">Label Maker</span>
                </legend>
                <ul>
                    <li><strong>Control Buttons:</strong>
                        <ul>
                            <li><strong>Always on Top:</strong> Keeps the window visible above other windows</li>
                            <li><strong>Settings:</strong> Opens application settings</li>
                            <li><strong>Labels:</strong> Shows the number of labels created (0 in this example)</li>
                            <li><strong>Reset:</strong> Clears all fields to start a new label</li>
                        </ul>
                    </li>
                    <li><strong>Label Information Fields:</strong>
                        <ul>
                            <li><strong>Product Name Line 1:</strong> Main product name</li>
                            <li><strong>Line 2 (optional):</strong> Additional product information</li>
                            <li><strong>Variant:</strong> Product variant, model, or SKU</li>
                            <li><strong>UPC Code (12 digits):</strong> Universal Product Code for barcode generation</li>
                        </ul>
                    </li>
                    <li><strong>Action Buttons:</strong>
                        <ul>
                            <li><strong>Preview:</strong> Shows how the label will look before printing</li>
                            <li><strong>View Files:</strong> Opens the file browser to view existing labels</li>
                        </ul>
                    </li>
                </ul>
</fieldset>

                <div class="image-map-container" id="return">
                    <img src="media/software/label_maker.jpg" alt="LabelMakerV3 Software" class="clickable-image">
                    
                    <!-- Clickable areas - these are positioned with CSS -->
                    <a href="#return"><div class="clickable-area" id="clReturn" data-tooltip="Return Button" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Go back to the Welcome screen</h3>
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
            </section>
            
            <aside style="display: grid;
  grid-template-columns: 1fr 1fr; /* Creates two equal columns */
  gap: 10px; /* Adds space between columns */
">


<fieldset class="instructions">
                <legend class="highlight">
                <span class="button" style="display:inline;">Management</span>
                </legend>
                <ul>
                    <li><strong>Control Buttons:</strong>
                        <ul>
                            <li>Return: Returns to the Welcome screen</li>
                            <li>Page blue button: Returns Data Label Tab</li>
                            <li>Pin: Pins the window to the top of the screen</li>
                        </ul>
                    </li>
                    <li><strong>Create New Label Record Field:</strong></li>
                        <ul>
                            <li><strong>Tracking Number:</strong></li>
                            <li><strong>SKU:</strong></li>
                            <li><strong>MP:Mirror Print</strong></li>
                            <li><strong>Print:</strong></li>
                            <li><strong>TR:transparency</strong></li>
                        </ul>
                    </li>
                </ul>
</fieldset>

                <div class="image-map-container" id="return">
                    <img src="media/software/view_files.jpg" alt="LabelMakerV3 Software" class="clickable-image">
                    
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

        <fieldset>
                <legend><div class="highlight-box">
                    <p><span class="button">Management</span> - For administrative functions and database management</p>
                </div></legend>
                <p>The Management section (blue button on the Welcome screen) provides access to administrative functions for managing your label database and integrations.</p>
                <p>This section includes:</p>
                <ul>
                    <li>Database management</li>
                    <li>User permissions (if applicable)</li>
                    <li>System status information</li>
                    <li>Integration management</li>
                </ul>
                </fieldset>
