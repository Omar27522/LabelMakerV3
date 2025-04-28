"""
Google Apps Script API integration utilities for Sheets Manager.
Handles listing projects, files, editing, and deployments using the unified OAuth2 credentials.
"""

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# SCOPES required for Apps Script API
SCOPES = [
    'https://www.googleapis.com/auth/script.projects',
    'https://www.googleapis.com/auth/script.deployments',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.file',
]

def get_apps_script_service(creds: Credentials):
    """Get an authenticated Apps Script API service object."""
    return build('script', 'v1', credentials=creds)

# Example: List user's Apps Script projects (container-bound and standalone)
def list_projects(creds: Credentials):
    service = get_apps_script_service(creds)
    # Apps Script API does not provide a direct list, so use Drive API to find .gs/.json files
    drive_service = build('drive', 'v3', credentials=creds)
    results = drive_service.files().list(
        q="mimeType='application/vnd.google-apps.script'",
        fields="files(id, name)"
    ).execute()
    return results.get('files', [])

# Example: Get script files for a project
def get_project_content(creds: Credentials, project_id: str):
    service = get_apps_script_service(creds)
    return service.projects().getContent(scriptId=project_id).execute()

# Example: Update script files for a project
def update_project_content(creds: Credentials, project_id: str, files):
    service = get_apps_script_service(creds)
    body = {"files": files}
    return service.projects().updateContent(scriptId=project_id, body=body).execute()

# Example: Create a new deployment
def create_deployment(creds: Credentials, project_id: str, version_number: int, description: str = ""): 
    service = get_apps_script_service(creds)
    body = {
        "versionNumber": version_number,
        "manifestFileName": "appsscript",
        "description": description or "Deployment via Sheets Manager"
    }
    return service.projects().deployments().create(scriptId=project_id, body=body).execute()

# Example: List deployments
def list_deployments(creds: Credentials, project_id: str):
    service = get_apps_script_service(creds)
    return service.projects().deployments().list(scriptId=project_id).execute()
