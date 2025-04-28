# Changes.md

## Summary of Changes Made

### 1. OAuth Authentication Flow
- Replaced the use of `credentials.json` (service account or incorrect format) with `ClientSecret.json` for OAuth user authentication.
- Implemented logic to use `token.json` for storing user access/refresh tokens after successful authentication. If `token.json` does not exist or is invalid, the app launches the OAuth flow using `ClientSecret.json`.
- All API calls to Google Apps Script now use the credentials stored in `token.json`.

### 2. Error Handling
- Improved error messages for missing or invalid credential files.
- Added user feedback for authentication and project/file loading errors.

### 3. Project and File Management
- The app loads Apps Script projects using the authenticated user's account.
- If no projects are found, the app displays "No Apps Script projects found." in the Projects list.
- If no project is selected or the selection is invalid, the app displays "No project selected or invalid selection." in the Files list.

---

## What You May Need to Do to Connect Your Google Sheet Scripts to the App

### 1. Prerequisites
- Ensure you have a valid `ClientSecret.json` file in the `Sheet Manager` directory. This file should be downloaded from your Google Cloud Console (OAuth 2.0 Client ID for Desktop app).
- Enable the following APIs for your Google Cloud project:
  - Google Apps Script API
  - (Optionally) Google Drive API (if your scripts interact with Drive files)

### 2. Running the App for the First Time
- When you run the app, it will prompt you to log in to your Google account via a browser window. Use the account that owns or has access to your Apps Script projects.
- After successful login, a `token.json` file will be created in the `Sheet Manager` directory. This file stores your access and refresh tokens for future sessions.

### 3. Viewing Your Apps Script Projects
- The app lists all **standalone Apps Script projects** owned by or shared with the authenticated Google account.
- If you see "No Apps Script projects found":
  - Double-check that you logged in with the correct Google account (the one that owns your scripts).
  - Make sure you have at least one **standalone** Apps Script project. Bound scripts (scripts attached to Sheets/Docs) may not always show up unless you have opened them in the Apps Script Editor at least once.
  - Try creating a new standalone project at https://script.google.com and see if it appears in the app.
  - Ensure the Apps Script API is enabled for your project in the Google Cloud Console.

### 4. Selecting Projects and Files
- Select a project from the Projects list to load its files.
- If you see "No project selected or invalid selection" in the Files list, make sure you have selected a valid project.
- If you still see no files, the project may be empty or there may be an issue with API permissions.

### 5. Troubleshooting
- If you encounter errors about permissions or missing APIs, re-check your Cloud Console settings and OAuth scopes.
- If you want to access scripts bound to specific Google Sheets, open those Sheets, go to Extensions > Apps Script, and ensure you have visited the Apps Script Editor for each one.
- If you have multiple Google accounts, make sure you are authenticating with the correct one.

---

## Additional Notes
- You do **not** need to provide a deployment ID to list or manage your Apps Script projects via the API.
- If you want to deploy your script as a web app, that is only needed if you want to access it via a URL or as a REST endpoint; it is not required for API management.
- If you need further help connecting your scripts or understanding how to work with bound vs. standalone scripts, please ask!
