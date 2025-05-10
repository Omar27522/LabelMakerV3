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