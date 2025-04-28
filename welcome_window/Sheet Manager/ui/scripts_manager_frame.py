"""
Scripts Manager Frame - UI for Apps Script management.
"""

import tkinter as tk
from tkinter import ttk

class ScriptsManagerFrame(tk.Frame):
    def __init__(self, parent, on_back=None):
        super().__init__(parent, bg="white")
        self._project_id_map = {}
        self._on_back = on_back
        self._create_widgets()
        self._wire_up_logic()
        self._load_projects()

    def _create_widgets(self):
        # Project List Panel
        project_panel = tk.Frame(self, bg="#f1f1f1", width=180)
        project_panel.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(project_panel, text="Projects", bg="#f1f1f1", font=("Roboto", 10, "bold")).pack(anchor="nw", padx=10, pady=(10,0))
        self.project_listbox = tk.Listbox(project_panel)
        self.project_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Script File List Panel
        file_panel = tk.Frame(self, bg="#f9f9f9", width=180)
        file_panel.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(file_panel, text="Files", bg="#f9f9f9", font=("Roboto", 10, "bold")).pack(anchor="nw", padx=10, pady=(10,0))
        self.file_listbox = tk.Listbox(file_panel)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main Editor & Actions
        main_panel = tk.Frame(self, bg="white")
        main_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Actions Toolbar
        toolbar = tk.Frame(main_panel, bg="#eeeeee")
        toolbar.pack(fill=tk.X, padx=0, pady=(0,2))
        self.back_btn = tk.Button(toolbar, text="Back", bg="#ff0067", fg="white", font=("Roboto", 10, "bold"), command=self._on_back_click)
        self.back_btn.pack(side=tk.LEFT, padx=(10,5), pady=6)
        self.deploy_btn = tk.Button(toolbar, text="Deploy", bg="#388e3c", fg="white", font=("Roboto", 10, "bold"), command=self._on_deploy)
        self.deploy_btn.pack(side=tk.LEFT, padx=5, pady=6)
        self.rollback_btn = tk.Button(toolbar, text="Rollback", bg="#b71c1c", fg="white", font=("Roboto", 10), command=self._on_rollback)
        self.rollback_btn.pack(side=tk.LEFT, padx=5, pady=6)
        self.save_btn = tk.Button(toolbar, text="Save", bg="#1976d2", fg="white", font=("Roboto", 10), command=self._on_save)
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=6)
        self.revert_btn = tk.Button(toolbar, text="Revert", bg="#757575", fg="white", font=("Roboto", 10), command=self._on_revert)
        self.revert_btn.pack(side=tk.LEFT, padx=5, pady=6)

        # Code Editor Panel
        editor_panel = tk.Frame(main_panel, bg="white")
        editor_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,5))
        self.editor = tk.Text(editor_panel, wrap=tk.NONE, font=("Consolas", 11), undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True)

        # Deployment Log/Status Panel
        log_panel = tk.Frame(main_panel, bg="#f5f5f5", height=80)
        log_panel.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(log_panel, text="Deployment Log", bg="#f5f5f5", font=("Roboto", 9, "bold")).pack(anchor="nw", padx=10, pady=(5,0))
        self.log_text = tk.Text(log_panel, height=4, bg="#f5f5f5", fg="#333", font=("Consolas", 9), state=tk.DISABLED)
        self.log_text.pack(fill=tk.X, padx=10, pady=(0,5))

    def _wire_up_logic(self):
        self.project_listbox.bind('<<ListboxSelect>>', self._on_project_select)
        self.file_listbox.bind('<<ListboxSelect>>', self._on_file_select)

    def _load_projects(self):
        import threading
        self.project_listbox.delete(0, tk.END)
        self.project_listbox.insert(tk.END, "Loading projects...")
        threading.Thread(target=self._load_projects_thread, daemon=True).start()

    def _load_projects_thread(self):
        import os
        import json
        from google.oauth2.credentials import Credentials
        from google.auth.exceptions import GoogleAuthError
        from utils import apps_script_api
        import pathlib
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ClientSecret.json'))
        token_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../token.json'))
        if not os.path.exists(creds_path):
            self.after(0, lambda: self._show_project_error("No ClientSecret.json found. Please connect your Google account."))
            return
        creds = None
        try:
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, apps_script_api.SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, apps_script_api.SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            projects = apps_script_api.list_projects(creds)
            self.after(0, lambda: self._populate_projects(projects))
        except GoogleAuthError as e:
            self.after(0, lambda: self._show_project_error(f"Auth error: {str(e)}"))
        except Exception as e:
            err_msg = f"Failed to load projects: {str(e)}"
            self.after(0, lambda: self._show_project_error(err_msg))

    def _populate_projects(self, projects):
        self.project_listbox.delete(0, tk.END)
        self._project_id_map = {}
        if not projects:
            self.project_listbox.insert(tk.END, "No Apps Script projects found.")
            return
        for proj in projects:
            name = proj.get('name', proj.get('id', 'Unknown'))
            project_id = proj.get('id', name)
            self._project_id_map[name] = project_id
            self.project_listbox.insert(tk.END, name)

    def _show_project_error(self, message):
        self.project_listbox.delete(0, tk.END)
        self.project_listbox.insert(tk.END, f"Error: {message}")
        self._append_log(f"[ERROR] {message}")

    def _on_project_select(self, event):
        selection = self.project_listbox.curselection()
        if not selection:
            return
        project_name = self.project_listbox.get(selection[0])
        project_id = self._project_id_map.get(project_name)
        self._current_project_id = project_id  # Store current project
        if not project_id or project_name.startswith("Error") or project_name.startswith("No Apps Script"):
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, "No project selected or invalid selection.")
            return
        self.file_listbox.delete(0, tk.END)
        self.file_listbox.insert(tk.END, "Loading files...")
        import threading
        threading.Thread(target=self._load_files_thread, args=(project_id,), daemon=True).start()

    def _load_files_thread(self, project_id):
        import os
        import json
        from google.oauth2.credentials import Credentials
        from google.auth.exceptions import GoogleAuthError
        from utils import apps_script_api
        import pathlib
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ClientSecret.json'))
        token_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../token.json'))
        if not os.path.exists(creds_path):
            self.after(0, lambda: self._show_file_error("No ClientSecret.json found. Please connect your Google account."))
            return
        creds = None
        try:
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, apps_script_api.SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, apps_script_api.SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            content = apps_script_api.get_project_content(creds, project_id)
            files = content.get('files', [])
            self.after(0, lambda: self._populate_files(files))
        except GoogleAuthError as e:
            self.after(0, lambda: self._show_file_error(f"Auth error: {str(e)}"))
        except Exception as e:
            self.after(0, lambda: self._show_file_error(f"Failed to load files: {str(e)}"))

    def _populate_files(self, files):
        self.file_listbox.delete(0, tk.END)
        self._current_files = files  # Store for content lookup
        if not files:
            self.file_listbox.insert(tk.END, "No files found in this project.")
            return
        for f in files:
            name = f.get('name', '[Unnamed file]')
            self.file_listbox.insert(tk.END, name)

    def _show_file_error(self, message):
        self.file_listbox.delete(0, tk.END)
        self.file_listbox.insert(tk.END, f"Error: {message}")
        self._append_log(f"[ERROR] {message}")

    def _on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if not selection or not hasattr(self, '_current_files'):
            return
        filename = self.file_listbox.get(selection[0])
        # Find file object
        file_obj = next((f for f in self._current_files if f.get('name') == filename), None)
        if not file_obj:
            self.editor.delete('1.0', tk.END)
            self.editor.insert('1.0', f"// File '{filename}' not found in API response.")
            return
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', '// Loading file content...')
        # Load content in background
        import threading
        threading.Thread(target=self._load_file_content_thread, args=(file_obj,), daemon=True).start()

    def _load_file_content_thread(self, file_obj):
        try:
            content = file_obj.get('source', '')
            # Update editor in main thread
            self.after(0, lambda: self._update_editor_content(content, file_obj.get('name', 'Untitled')))
        except Exception as e:
            self.after(0, lambda: self._update_editor_content(f"// Error loading content: {e}", file_obj.get('name', 'Untitled')))

    def _update_editor_content(self, content, filename):
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', content if content else f"// No content in {filename}")

    def _on_deploy(self):
        self._append_log("[Deploy] Triggered deployment (placeholder)")

    def _on_rollback(self):
        self._append_log("[Rollback] Triggered rollback (placeholder)")

    def _on_save(self):
        # Save the current file's content back to the API
        if not hasattr(self, '_current_files') or not hasattr(self, '_current_project_id'):
            self._append_log('[Save] No project or file loaded.')
            return
        selection = self.file_listbox.curselection()
        if not selection:
            self._append_log('[Save] No file selected.')
            return
        filename = self.file_listbox.get(selection[0])
        file_obj = next((f for f in self._current_files if f.get('name') == filename), None)
        if not file_obj:
            self._append_log(f"[Save] File '{filename}' not found in memory.")
            return
        new_content = self.editor.get('1.0', 'end-1c')
        file_obj['source'] = new_content
        # Save in background
        import threading
        threading.Thread(target=self._save_file_content_thread, args=(self._current_project_id, self._current_files, filename), daemon=True).start()

    def _save_file_content_thread(self, project_id, files, filename):
        import os
        import json
        from google.oauth2.credentials import Credentials
        from google.auth.exceptions import GoogleAuthError
        from utils import apps_script_api
        import pathlib
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ClientSecret.json'))
        token_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../token.json'))
        creds = None
        try:
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, apps_script_api.SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, apps_script_api.SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            apps_script_api.update_project_content(creds, project_id, files)
            self.after(0, lambda: self._append_log(f"[Save] Saved '{filename}' to project."))
        except GoogleAuthError as e:
            self.after(0, lambda: self._append_log(f"[Save] Auth error: {str(e)}"))
        except Exception as e:
            self.after(0, lambda: self._append_log(f"[Save] Failed to save '{filename}': {str(e)}"))

    def _on_revert(self):
        self._append_log("[Revert] Reverted changes (placeholder)")

    def _on_back_click(self):
        if self._on_back:
            self._on_back()

    def _append_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
