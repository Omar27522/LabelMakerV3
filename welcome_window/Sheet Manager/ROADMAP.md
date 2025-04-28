# Sheets Manager: Refactor Plan & Feature Roadmap

## Overview
This document provides a comprehensive plan for refactoring and expanding the Sheets Manager application. It covers modularization, maintainability, and a roadmap for future features and improvements.

---

## 1. Directory Structure Inspiration

Following best practices, the project should use clear separation of concerns:
- `ui/`: All UI windows, dialogs, and frames.
- `utils/`: Utility functions, logic, and helpers.
- `config/`: Configuration management and user preferences.
- `modules/`: Main modules for each app feature/page.
- `assets/`: Icons, images, and other static files.
- `tests/`: Unit and integration tests.

---

## 2. Proposed Directory Structure

```
Sheet Manager/
│
├── main.pyw
├── modules/                 # Main modules for each page/section
│   ├── welcome.py           # Welcome/landing module
│   ├── connection.py        # Google Sheets connection module
│   └── ...                  # Future modules (e.g., DataView, Settings, etc.)
│
├── ui/                      # UI components, dialogs, frames
│   ├── welcome_frame.py
│   ├── connection_frame.py
│   └── ...
│
├── utils/                   # Utilities and helpers
│   ├── logger.py
│   ├── single_instance.py
│   ├── error_handling.py
│   ├── cleanup.py
│   ├── dpi.py
│   └── ...                  # E.g., sheets_utils.py
│
├── config/                  # Configuration management
│   ├── config_manager.py
│   └── ...
│
├── assets/                  # Icons, images, etc.
├── tests/                   # Unit and integration tests
└── README.md
```

---

## 3. Refactor Steps

1. Move all module classes (Welcome, Connection, etc.) to `modules/`.
2. Extract reusable dialogs/widgets to `ui/`.
3. Move all logic not directly related to UI (e.g., Google Sheets API, file ops) to `utils/`.
4. Centralize configuration handling in `config/`.
5. Update `main.pyw` to only handle app bootstrapping, window setup, and navigation between modules.
6. Add docstrings and comments for maintainability.
7. Add unit tests for all utilities and modules.

---

## 4. Feature Roadmap & Ideas

### Core Features
- **Google Sheets Integration:**
  - Authenticate with Google (OAuth2 flow).
  - View, create, rename, and delete spreadsheets.
  - Read, write, and update sheet data.
  - Import/export CSV and Excel files.
- **Data Viewer/Editor:**
  - Spreadsheet-like grid for viewing and editing data.
  - Filtering, sorting, and searching within sheets.
  - Bulk update and undo/redo support.
- **Settings Module:**
  - Manage user preferences (theme, autosave, API keys, etc.).
  - Configure default sheet behaviors.
- **Connection Manager:**
  - Manage multiple Google accounts.
  - Connection status indicator.
- **History & Audit Trail:**
  - View changes and revert to previous versions.
- **Notifications:**
  - In-app and system notifications for sync status, errors, etc.

### Advanced & Optional Features
- **Collaboration:**
  - Real-time multi-user editing (if API allows).
- **Charting & Visualization:**
  - Built-in support for basic charts and graphs.
- **Custom Formulas & Scripting:**
  - Allow users to define custom calculations or scripts.
- **Template Management:**
  - Save and reuse sheet templates.
- **Data Validation:**
  - Enforce data types and validation rules on input.
- **Offline Mode:**
  - Local cache with sync on reconnect.
- **Export/Import Plugins:**
  - Support for additional data formats.
- **Accessibility:**
  - High-contrast themes, keyboard navigation, screen reader support.
- **Localization:**
  - Multi-language support.
- **Theming:**
  - Light/dark mode and custom color schemes.
- **Cloud Backup:**
  - Backup and restore user settings and data to the cloud.
- **Command Palette:**
  - Quick-access command/search bar for power users.
- **Drag-and-Drop:**
  - Reorder sheets, columns, and rows via drag-and-drop.
- **Plugin System:**
  - Allow third-party extensions.

---

## 5. Testing & Quality Assurance
- Add unit and integration tests for all modules and utilities.
- Use continuous integration (CI) for automated testing.
- Manual QA for UI/UX flows.

---

## 6. Documentation
- Keep this roadmap updated as features are added or changed.
- Add usage instructions and developer notes to `README.md`.
- Add docstrings to all modules and functions.

---

## 7. Next Steps
- Review and adjust this plan as needed.
- Prioritize features based on user needs.
- Begin incremental implementation, testing at each stage.
