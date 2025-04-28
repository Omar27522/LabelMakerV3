# Sheets Manager Refactor Plan

## Overview
This document outlines a proposed plan to refactor the Sheets Manager application for maximum modularity, maintainability, and scalability. The plan is inspired by the structure of the main `src` directory in the root project.

---

## 1. Directory Structure Inspiration from `src`

The root `src` directory uses clear separation of concerns:
- `ui/`: All UI windows, dialogs, and frames.
- `utils/`: Utility functions, logic, and helpers.
- `config/`: Configuration management.
- `product_data/`: Data-specific logic and helpers.

This modular approach allows for easy maintenance and future expansion.

---

## 2. Proposed Refactored Structure for Sheets Manager

```
Sheet Manager/
│
├── main.pyw
├── modules/                 # Main modules for each page/section
│   ├── __init__.py
│   ├── welcome.py           # Welcome/landing module
│   ├── connection.py        # Google Sheets connection module
│   └── ...                  # Future modules (e.g., DataView, Settings, etc.)
│
├── ui/                      # UI components, dialogs, frames
│   ├── __init__.py
│   └── ...                  # Reusable UI widgets/dialogs
│
├── utils/                   # Utilities and helpers
│   ├── __init__.py
│   └── ...                  # E.g., sheets_utils.py, config_utils.py
│
├── config/                  # Configuration management
│   ├── __init__.py
│   └── config_manager.py
│
├── assets/                  # Icons, images, etc.
│
└── README.md
```

---

## 3. Modularization Plan

### a. Modules Directory
- Each logical “page” or “step” is a module (Python class with a frame).
- Modules communicate via callbacks (e.g., pressing “Get Started” in Welcome calls a function to swap to Connection).
- Easy to add new modules: just drop in a new Python file and wire it up in the main window.

### b. UI Directory
- Place reusable dialogs, widgets, and frames here.
- Example: If multiple modules need a custom entry dialog, it lives here.

### c. Utils Directory
- Place helpers for Google Sheets, config parsing, file operations, etc.
- Example: `sheets_utils.py` for all Google Sheets API logic.

### d. Config Directory
- Centralizes configuration logic (e.g., loading/saving user preferences, credentials).

### e. Assets Directory
- Store icons, images, etc., for easy access and maintainability.

---

## 4. Refactor Steps

1. Move all module classes (Welcome, Connection, etc.) to `modules/`.
2. Extract reusable dialogs/widgets to `ui/`.
3. Move all logic not directly related to UI (e.g., Google Sheets API, file ops) to `utils/`.
4. Centralize configuration handling in `config/`.
5. Update `main.pyw` to only handle app bootstrapping, window setup, and navigation between modules.
6. Use clear, consistent naming conventions for all files and classes.
7. Document each module and utility with docstrings for maintainability.

---

## 5. Future-Proofing

- **Adding a new feature/page:** Create a new module in `modules/`, add any needed UI in `ui/`, use helpers from `utils/`.
- **Testing:** Each module and utility can be tested in isolation.
- **Scaling:** As the app grows, subdirectories (e.g., `ui/dialogs/`, `utils/sheets/`) can be added.

---

## 6. Example: Adding a New Module

1. Create `modules/dataview.py` with a `DataViewModule` class.
2. Add navigation logic in `main.pyw` to swap to this module.
3. If needed, create new dialogs in `ui/` and helpers in `utils/`.

---

## 7. Next Steps

- Review this plan and adjust directory/module names as needed.
- Decide on immediate priorities (e.g., extract UI components, centralize config, etc.).
- Begin incremental refactoring, testing after each stage.
