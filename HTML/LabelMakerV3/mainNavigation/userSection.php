<h3>User Section</h3>
<?php echo basename(__FILE__); ?>
<div class="container">
    <main>


        <span class="button green">User</span>
        <p>When you click on the User button, you'll be taken to the Create Label interface:</p>


        <ul style="column-count: 2;">
            <p>
                <li><strong>Control Buttons:</strong></li>
            <ul>
                <li>Return: Returns to the Welcome screen</li>
                <li>Page blue button: Returns Data Label Tab</li>
                <li>Pin: Pins the window to the top of the screen</li>
            </ul>
            </p>



            <p>
                <li><strong>Create New Label Record Field:</strong>
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
                </li>
            </p>

            <p style="column-break-before: always;">
                <li><strong>MP:</strong>
                    <ul>
                        <li>Mirror Print</li>
                        <li>It prints the label in reverse. useful for thermal printers.</li>
                    </ul>
                </li>
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
            </p>
            <p>
                <li><strong>Print Label:</strong>
                    <ul>
                        <li>Sends the data to the cloud for record keeping.</li>
                    </ul>
                </li>
            </p>
        </ul>
        <section>
            <aside style="display: grid;
  grid-template-columns: 1fr 1fr; /* Creates two equal columns */
  gap: 10px; /* Adds space between columns */
">
                <div class="image-map-container" id="return">
                    <img src="media/software/create_label_default.jpg" alt="LabelMakerV3 Software"
                        class="clickable-image">

                    <!-- Clickable areas - these are positioned with CSS -->
                    <a href="#return">
                        <div class="clickable-area" id="clReturn" data-tooltip="Return Button" tabindex="0">
                            <div class="tooltip-content">
                                <h3>Go back to the Welcome screen</h3>
                            </div>
                        </div>
                    </a>

                    <a href="#returnsData">
                        <div class="clickable-area" id="clReturnsData" data-tooltip="Returns Data Button" tabindex="0">
                            <div class="tooltip-content">
                                <h3>Returns Data</h3>
                                Brings up a new window.
                                <p>Labels
                                    <br />
                                    Records
                                </p>
                            </div>
                        </div>
                    </a>

                    <a href="#returnsData">
                        <div class="clickable-area" id="clPinButton" data-tooltip="Pin Button" tabindex="0">
                            <div class="tooltip-content">
                                <h3>Pin Button</h3>
                                <p>
                                    Pinned window.
                                </p>
                            </div>
                        </div>
                    </a>

                    <div class="clickable-area" id="clTrackingNumber" data-tooltip="Tracking Number" tabindex="0">
                        <div class="tooltip-content">
                            <h3>Tracking Number Field</h3>
                            <p>Enter the tracking number for the package here. A browser window will open CTRL+V the
                                tracking number.</p>
                        </div>
                    </div>

                    <div class="clickable-area" id="clSKU" data-tooltip="SKU Field" tabindex="0">
                        <div class="tooltip-content">
                            <h3>SKU Field</h3>
                            <p>This field is not enabled until a tracking number is entered. Enter the SKU for the
                                package here.</p>
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
                            <p>Label will be recorded into the system, and the software will print a label by default.
                            </p>
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
                                <li><strong>MP:</strong> Mirror Print - prints the label in reverse for thermal printers
                                </li>
                                <li><strong>Print:</strong> Enable/disable printing (will still record the label if
                                    disabled)</li>
                                <li><strong>TR:</strong> Enable Transparency - makes the program transparent when
                                    inactive</li>
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