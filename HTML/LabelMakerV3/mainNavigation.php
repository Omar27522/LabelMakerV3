<section id="main-navigation">
                <h2>3. Main Navigation</h2>
                <p>The LabelMakerV3 application is organized into four main sections, accessible from the Welcome screen. This section will help you understand how to navigate through these areas and what each one offers.</p>
                
                <h3>User Section</h3>
                
                <div class="container">
        <main>
            <section>
                <aside style="display: grid;
  grid-template-columns: 1fr 1fr; /* Creates two equal columns */
  gap: 10px; /* Adds space between columns */
">
                <div class="image-map-container" id="return">
                    <img src="media/software/create_label_default.jpg" alt="LabelMakerV3 Software" class="clickable-image">
                    
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
                
                <div>
                    <fieldset class="instructions">
                <legend class="highlight">
                    <span class="button green" style="display:inline;">User</span>
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
                </div>
				<aside>
            </section>
        </main>
        
    </div>
                <h2>Image Text Blocks</h2>
<p>How to place text blocks over an image:</p>


                <details>
                <summary class="highlight-box">
                    <span class="button green">User</span> - For day-to-day label creation and printing tasks
                </summary>
                <p>When you click on the User button, you'll be taken to the Create Label interface:</p>
                
                <p>The Create Label interface includes:</p>
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
                                <ul>
                                    <li>Enter the tracking number for the package.</li>
                                    <li>A Browser window will open to enter the tracking number.</li>
                            </ul>
                            <li><strong>SKU:</strong></li>
                                <ul>
                                    <li>The field is not enabled until a tracking number is entered.</li>
                                    <li>Enter the SKU for the package.</li>
                            </ul>
                    </ul>
                        
                            <li><strong>MP:</strong></li>
                                <ul>
                                    <li>Mirror Print</li>
                                    <li>It prints the label in reverse. useful for thermal printers.</li>
                            </ul>
                            <li><strong>Print:</strong></li>
                                <ul>
                                    <li>Prints the label.</li>
                                    <li>Disable it and it will still record the label, but it will not print.</li>
                            </ul>
                            <li><strong>TR:</strong></li>
                                <ul>
                                    <li>
                                        Enable Transparency
                                    </li>
                                    <li>The program will become transparent when inactive.</li>
                                    <li>Adjust transparency level (1-10) in Settings.</li>
                            </ul>
                        
                    </li>
                    <li><strong>Action Buttons:</strong>
                        <ul>
                            <li>Preview: Shows how the label will look</li>
                            <li>View Files: Browse label files you've created</li>
                        </ul>
                    </li>
                </ul>
            </details>
                
                <h3>Management Section</h3>
                <details>
                <summary><div class="highlight-box">
                    <p><span class="button">Management</span> - For administrative functions and database management</p>
                </div></summary>
                <p>The Management section (blue button on the Welcome screen) provides access to administrative functions for managing your label database and integrations.</p>
                <p>This section includes:</p>
                <ul>
                    <li>Database management</li>
                    <li>User permissions (if applicable)</li>
                    <li>System status information</li>
                    <li>Integration management</li>
                </ul>
                
                <h3>Labels Section</h3>
                <div class="highlight-box">
                    <p><span class="button orange">Labels</span> - For accessing and managing all your created labels</p>
                </div>
                <p>The Labels section (orange button on the Welcome screen) allows you to access and manage all the labels you've created.</p>
                <p>When you click on the Labels button, you'll see a list of all your labels with options to:</p>
                <ul>
                    <li>Search for specific labels</li>
                    <li>Filter labels by various criteria</li>
                    <li>Edit existing labels</li>
                    <li>Delete labels</li>
                    <li>Export label data</li>
                </ul>
                
                <h3>Settings Section</h3>
                <div class="highlight-box">
                    <p><span class="button gray">Settings</span> - For configuring application preferences</p>
                </div>
                <p>The Settings section (gray button on the Welcome screen) allows you to configure the application according to your preferences.</p>
                <p>When you click on the Settings button, you'll see the Settings screen:</p>
                
                <p>The Settings screen includes:</p>
                <ul>
                    <li><strong>Labels Directory:</strong> Set where label files are saved on your computer</li>
                    <li><strong>Transparency Settings:</strong>
                        <ul>
                            <li>Enable/disable window transparency when inactive</li>
                            <li>Adjust transparency level (1-10)</li>
                        </ul>
                    </li>
                    <li><strong>Google Sheets Integration:</strong>
                        <ul>
                            <li>View connection status</li>
                            <li>Configure Google Sheets connection</li>
                        </ul>
                    </li>
                    <li><strong>Log Management:</strong>
                        <ul>
                            <li>Manage shipping logs</li>
                            <li>Migrate from legacy systems</li>
                        </ul>
                    </li>
                    <li><strong>Action Buttons:</strong>
                        <ul>
                            <li>Cancel: Exit without saving changes</li>
                            <li>Save: Save your settings changes</li>
                        </ul>
                    </li>
                </ul>
                
                <h3>Status Indicators</h3>
                <p>At the bottom of the Welcome screen, you'll find important status information:</p>
                <ul>
                    <li><strong>Connection Status</strong> (bottom left): Shows whether you're connected to Google Sheets
                        <ul>
                            <li>"Not Connected" means Google Sheets integration is not set up</li>
                            <li>"Connected" means Google Sheets integration is active</li>
                        </ul>
                    </li>
                    <li><strong>Version Number</strong> (bottom right): Shows which version of LabelMakerV3 you're using</li>
                </ul>
                <p>These status indicators help you quickly understand the current state of your application.</p>
            </details>
            </section>