

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
    <ol><img src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/LabelMakerV3/media/software/label_maker_installation.jpg" alt="LabelMakerV3 Software"
            style="width: 10%; float: right;margin-right: 30%;">
        <li>Double-click on the LabelMakerV3 installer file you received</li>
        <li>Follow the on-screen instructions in the installation wizard</li>
        <li>When prompted, choose the installation location (the default location is recommended)</li>
        <li>Wait for the installation to complete</li>
        <li>Click "Finish" to complete the installation</li>
    </ol>

    <div style="display: flex; gap: 2rem; margin: 1.5rem 0;">
        <div style="flex: 1;">
            <h3>First Launch</h3>
            <p>After installation, you can launch LabelMakerV3 by:</p>
            <ul>
                <li>Finding the LabelMakerV3 icon on your desktop and double-clicking it, or</li>
                <li>Going to the Start menu, finding LabelMakerV3 in the programs list, and clicking on it</li>
            </ul>
            <p>The first time you launch the application, it may take a few moments to initialize and set up necessary files. 
            You'll need to go into Settings and specify the location where the Labels are (or will be) stored, then click SAVE.</p>
        </div>
        <div style="flex: 1; display: flex; justify-content: center; align-items: flex-start;">
            <img alt="LabelMakerV3 Software" src="https://raw.githubusercontent.com/Omar27522/LabelMakerV3/refs/heads/main/HTML/LabelMakerV3/media/software/getting_started.jpg" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        </div>
    </div>

    <h3 style="display:inline;">Understanding the Welcome Screen</h3>
    <p>When you first open LabelMakerV3, you'll see the Welcome screen:</p>

    <?php include 'software/gettingStarted/InteractiveLabelMakerInterface.php'; ?>

    <div class="highlight-box">
        <p><strong>Note:</strong> The Welcome Screen is your main dashboard for accessing all features of LabelMakerV3.
        </p>
    </div>

    <p>The Welcome screen is your starting point for using LabelMakerV3. Let's look at the key elements:</p>
    <ul>
        <li><strong>Title Bar:</strong> At the top of the window, showing "Welcome".</li>
        <li><strong>Labels Counter:</strong> Shows how many labels you've created (displays "0 Labels" when you first
            start)</li>
        <li><strong>Application Name:</strong> Displays "Label Maker V3"</li>
        <li><strong>Main Navigation Buttons:</strong>
            <ul><br />
                <li><span class="button green">User</span>: Access user-specific functions such as send labels, and record tracking data.</li>
                <br />
                <li><span class="button">Management</span>: Access management features. Like creating new labels, and managing existing labels.</li>
                <br />
                <li><span class="button orange">Labels</span>: Access record label creation and management of labels.</li>
                <br />
                <li><span class="button gray">Settings</span>: Access application settings.</li>
            </ul><br />
        </li>
        <li><strong>Connection Status:</strong> At the bottom left, shows "Not Connected" if Google Sheets integration
            is not set up</li>
            <li><strong>Connection Status:</strong> At the bottom left, shows "Connected" The user can reset daily data records, by clicking the Reset action button.</li>
        <li><strong>Version Number:</strong> At the bottom right, shows the current version of the application (e.g.,
            "Ver. 1.0.1.1"). 
        Here the user can print labels with-out record tracking data.</li>
    </ul>
    <p>This Welcome screen serves as your dashboard for navigating to different parts of the application. In the
        following sections, we'll explore each of these areas in detail.</p>
</section>