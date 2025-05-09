<section id="getting-started">
    <h2>2. Getting Started</h2>
    <h3>System Requirements</h3>
    <p>Before installing LabelMakerV3, ensure your computer meets the following requirements:</p>
    <ul>
        <li>Windows operating system (Windows 10 or later recommended)</li>
        <li>At least 4GB of RAM</li>
        <li>500MB of available disk space</li>
        <li>Internet connection (for Google Sheets integration)</li>
        <li>Python 3.10 or later (included in the installation package)</li>
    </ul>

    <h3>Installation Process</h3>

    <p>To install LabelMakerV3 on your computer:</p>
    <ol><img src="media/software/label_maker_installation.jpg" alt="LabelMakerV3 Software"
            style="width: 10%; float: right;margin-right: 30%;">
        <li>Double-click on the LabelMakerV3 installer file you received</li>
        <li>Follow the on-screen instructions in the installation wizard</li>
        <li>When prompted, choose the installation location (the default location is recommended)</li>
        <li>Wait for the installation to complete</li>
        <li>Click "Finish" to complete the installation</li>
    </ol>

    <h3>First Launch</h3>
    <p>After installation, you can launch LabelMakerV3 by:</p>
    <ul>
        <li>Finding the LabelMakerV3 icon on your desktop and double-clicking it, or</li>
        <li>Going to the Start menu, finding LabelMakerV3 in the programs list, and clicking on it</li>
    </ul>
    <p>The first time you launch the application, it may take a few moments to initialize and set up necessary files.
    </p>

    <h3>Understanding the Welcome Screen</h3>
    <p>When you first open LabelMakerV3, you'll see the Welcome screen:</p>

    <div class="container">
        <main>
            <section>
                <h2>Interactive LabelMaker Interface</h2>
                <p>Click on the highlighted areas of the image to learn more about each section of the interface.</p>
                <aside style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="instructions">
                        <h3>How to Use This Interactive Guide</h3>
                        <p>The highlighted areas on the image are clickable. Click on any highlighted area to see
                            detailed information about that part of the interface.</p>
                        <p>You can also use the Tab key to navigate between the clickable areas and press Enter to view
                            the information.</p>
                    </div>

                    <div class="image-map-container" id="numberOfLabels">
                        <img src="media/software/welcome_connected.jpg" alt="LabelMakerV3 Software"
                            class="clickable-image">
                        <!-- Clickable areas - these are positioned with CSS -->
                        <a href="#numberOfLabels">
                            <div class="clickable-area" id="wNumberOfLabels" data-tooltip="Number of Labels"
                                tabindex="0">
                                <div class="tooltip-content">
                                    <h3>Number of Labels in Database</h3>
                                    <p>Labels Counter: Shows how many labels you've created (displays "0 Labels" when you first start)</p>
                                </div>
                            </div>
                        </a>

                        <div class="clickable-area" id="wUser" data-tooltip="User Button"
                                tabindex="0">
                                <div class="tooltip-content">
                                    <h3>Create Label Record</h3>
                                    <img src="media/software/create_label_default.jpg" alt="User Button"
                                        style="width: 100%;">
                                </div>
                        </div>
                        
                        <div class="clickable-area" id="wManagement" data-tooltip="Management Button"
                                tabindex="0">
                                <div class="tooltip-content">
                                    <h3>Management Button</h3>
                                    <img src="media/software/management_thumbnail.jpg" alt="Management Button"
                                        style="width: 200%;">
                                </div>
                        </div>

                        <div class="clickable-area" id="wLabels" data-tooltip="Labels Button"
                                tabindex="0">
                                <div class="tooltip-content">
                                    <h3>Labels Button</h3>
                                    <img src="media/software/returns_data_records_thumbnail.jpg" alt="Labels Button"
                                        style="width: 200%;">
                                </div>
                        </div>

                        <div class="clickable-area" id="wSettings" data-tooltip="Settings Button"
                                tabindex="0">
                                <div class="tooltip-content">
                                    <h3>Settings Button</h3>
                                    <img src="media/software/settings.jpg" alt="Settings Button"
                                        style="width: 200%;">
                                </div>
                        </div>

                        <div class="clickable-area" id="wReset" data-tooltip="Reset action"
                                tabindex="0">
                                <div class="tooltip-content">
                                    <h3>Reset action</h3>
                                    <img src="media/software/reset_google_sheets_rows.jpg" alt="Reset action"
                                        style="width: 200%;">
                                </div>
                        </div>

                        <div class="clickable-area" id="wNoRecord" data-tooltip="No Record action"
                                tabindex="0">
                                <div class="tooltip-content">
                                    <h3>No Record action</h3>
                                    <img src="media/software/no_record_label.jpg" alt="No Record action"
                                        style="width: 200%;">
                                </div>
                        </div>
                        <aside>
            </section>
        </main>

    </div>

    <div class="highlight-box">
        <p><strong>Note:</strong> The Welcome Screen is your main dashboard for accessing all features of LabelMakerV3.
        </p>
    </div>

    <p>The Welcome screen is your starting point for using LabelMakerV3. Let's look at the key elements:</p>
    <ul>
        <li><strong>Title Bar:</strong> At the top of the window, showing "Welcome" and window controls (minimize,
            maximize, close)</li>
        <li><strong>Labels Counter:</strong> Shows how many labels you've created (displays "0 Labels" when you first
            start)</li>
        <li><strong>Application Name:</strong> Displays "Label Maker V3"</li>
        <li><strong>Main Navigation Buttons:</strong>
            <ul><br />
                <li><span class="button green">User</span>: Access user-specific functions</li>
                <br />
                <li><span class="button">Management</span>: Access management features</li>
                <br />
                <li><span class="button orange">Labels</span>: Access label creation and management</li>
                <br />
                <li><span class="button gray">Settings</span>: Access application settings</li>
            </ul><br />
        </li>
        <li><strong>Connection Status:</strong> At the bottom left, shows "Not Connected" if Google Sheets integration
            is not set up</li>
        <li><strong>Version Number:</strong> At the bottom right, shows the current version of the application (e.g.,
            "Ver. 1.0.1.1")</li>
    </ul>
    <p>This Welcome screen serves as your dashboard for navigating to different parts of the application. In the
        following sections, we'll explore each of these areas in detail.</p>
</section>