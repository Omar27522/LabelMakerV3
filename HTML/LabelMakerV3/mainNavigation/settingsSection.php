
<h3>Settings Section</h3>
<?php echo basename(__FILE__); ?>
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
            