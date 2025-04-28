# Sheets Manager: Core Features Roadmap

**Current Status & Next Steps:**
- The Google Apps Script API is enabled and uses the same OAuth2 credentials as the rest of the app.
- Authentication and credential management for both Google Sheets and Apps Script are unified—no additional credential setup is required.
- The app can now be extended to list, edit, and deploy Apps Script projects using the existing authentication flow.
- Next steps: Integrate Apps Script API endpoints, build a Scripts Manager UI, and connect deployment actions to the unified credential system.

This document outlines the core features required for the Sheets Manager application, with a new focus on robust Google Apps Script integration, direct script editing, deployment management, and Google Sheets automation.

---

## 1. Google Apps Script Integration & Deployment

**Description:**
This feature enables users to view, edit, and deploy Google Apps Scripts directly to their Google Sheets from within the Sheets Manager application. It provides a bridge between your local desktop environment and Google Apps Script projects, allowing for rapid iteration and deployment of custom sheet automations.

**How it works:**
- The app authenticates with Google and lists available Apps Script projects linked to the user's Google Sheets.
- Users can open, edit, and save Apps Script files (e.g., `.gs`, `.js`, `.json`) using an embedded code editor within the app.
- The app provides tools to deploy new script versions, manage deployments, and roll back to previous versions using the Google Apps Script API.
- Users can trigger deployments directly from the Settings dialog or a dedicated Scripts Manager UI.
- The integration supports both standalone and container-bound scripts.

## 2. Google Sheets Integration

**Description:**
This feature enables seamless connectivity between the Sheets Manager app and Google Sheets, allowing users to securely authenticate, manage multiple accounts, and perform a wide range of spreadsheet operations directly from the application. The integration will use the Google Sheets API and OAuth2 authentication to ensure data privacy and security.

**How it works:**
- Users will authenticate using a Google account via a secure OAuth2 flow.
- The app will store and manage tokens for multiple accounts if needed.
- All spreadsheet operations (view, create, rename, delete, read, write, import/export) will be performed using the Google Sheets API.
- Connection status will be displayed in the UI, and troubleshooting or re-authentication options will be provided if issues occur.
- **Authentication:**
  - Implement OAuth2 flow for secure Google account authentication.
  - Support managing multiple Google accounts.
- **Sheet Operations:**
  - View, create, rename, and delete spreadsheets.
  - Read, write, and update sheet data.
  - Import/export CSV and Excel files.
- **Connection Management:**
  - Connection status indicator.
  - Connection troubleshooting and re-authentication workflows.

## 3. Data Viewer/Editor

**Description:**
This module provides an interactive, spreadsheet-like interface for users to view and edit Google Sheets data. In the context of Apps Script automation, it also allows users to preview how Apps Script changes will affect sheet data and to validate automation outcomes.

**How it works:**
- Data from the selected Google Sheet will be displayed in a grid format.
- Users can edit cells directly, with changes synced back to Google Sheets.
- Filtering, sorting, and searching tools will help users quickly find and manipulate data.
- Bulk update features allow users to modify large data sets efficiently.
- Undo/redo support ensures users can safely experiment with changes.
- The UI will provide feedback on Apps Script automation runs, including logs or errors.
- **Spreadsheet-like Grid:**
  - Display sheet data in a familiar, editable grid.
  - Support filtering, sorting, and searching within sheets.
  - Bulk update and undo/redo functionality.
- **User Experience:**
  - Responsive UI with clear error and status messages.

## 4. Settings Module (Apps Script Deployment)

**Description:**
The Settings Module centralizes configuration for user preferences and, crucially, for Apps Script deployment and automation. It allows users to connect their Google account, manage Apps Script deployment endpoints, and configure triggers for automated Apps Script runs (such as EOD archival or custom workflows).

**How it works:**
- Users can manage API keys/credentials and connect Google accounts for Apps Script access.
- Configure Apps Script project IDs, deployment IDs, and select which scripts to manage.
- Test deployment connections and view deployment status/logs.
- Schedule or manually trigger Apps Script automations from the settings interface.
- All configuration is stored securely and can be updated as needed.
- **User Preferences:**
  - Theme selection (light/dark).
  - Autosave interval and behavior.
  - API key and credential management.
  - Default sheet and view configuration.
- **Deployment & Automation:**
  - Configure and test deployment endpoints (for EOD archival automation, etc.).
  - Schedule or trigger automated archival processes.

## 5. History & Audit Trail

**Description:**
Track changes to Apps Script deployments, sheet data, and configuration. This ensures all script edits, deployments, and automation runs are auditable and reversible if needed.

**How it works:**
- Maintain a log of Apps Script version history, deployments, and who made changes.
- Allow users to view change history for scripts, sheet data, and settings.
- Provide options to revert to previous Apps Script versions or sheet states.

## 6. Notifications

**Description:**
Keep users informed about the status of Apps Script deployments, automation runs, and errors through in-app and system notifications.

**How it works:**
- Notify users of successful or failed Apps Script deployments.
- Alert users to automation completion, errors, or required actions.
- Provide logs and feedback for troubleshooting.

---

## Implementation Notes
- Prioritize modular and extensible code structure for Apps Script and Sheets integration.
- Centralize configuration and settings in the `config/` directory.
- Ensure robust error handling and user feedback throughout the app.
- Add comprehensive docstrings, comments, and unit tests for maintainability.

---

*This roadmap will evolve as user needs and technical requirements become clearer. Please provide feedback or clarifications to guide development priorities.*
