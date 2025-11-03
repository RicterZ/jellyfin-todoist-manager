import requests
import json
from datetime import datetime
from typing import Optional, List

from todoist_api_python.api import TodoistAPI


def get_or_create_section(api: TodoistAPI, project_id: str, name: str) -> Optional[str]:
    sections = api.get_sections(project_id=project_id)
    for s in sections:
        if s.name == name:
            return s.id
    created = api.add_section(project_id=project_id, name=name)
    return created.id if created else None


def get_tasks_in_project(api: TodoistAPI, project_id: str) -> List:
    # SDK paginates; iterator returns batches
    result = []
    tasks_iter = api.get_tasks(project_id=project_id)
    # SDK may return list directly; handle both
    if isinstance(tasks_iter, list):
        return tasks_iter
    for batch in tasks_iter:
        result.extend(batch)
    return result


def is_section_empty(api: TodoistAPI, project_id: str, section_id: str) -> bool:
    tasks = get_tasks_in_project(api, project_id)
    for t in tasks:
        if getattr(t, 'section_id', None) == section_id:
            return False
    return True


def _sync_command(api_token: str, commands: list) -> bool:
    url = "https://api.todoist.com/api/v1/sync"
    data = {
        "sync_token": "*",
        "resource_types": json.dumps(["sections"]),
        "commands": json.dumps(commands),
    }
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = requests.post(url, data=data, headers=headers)
    return resp.status_code == 200


def archive_section(api_token: str, section_id: str) -> bool:
    return _sync_command(api_token, [{
        "type": "section_archive",
        "uuid": f"archive-{datetime.utcnow().timestamp()}",
        "args": {"id": int(section_id) if section_id.isdigit() else section_id}
    }])


def unarchive_section(api_token: str, section_id: str) -> bool:
    return _sync_command(api_token, [{
        "type": "section_unarchive",
        "uuid": f"unarchive-{datetime.utcnow().timestamp()}",
        "args": {"id": int(section_id) if section_id.isdigit() else section_id}
    }])


def get_archived_section_by_name(api_token: str, project_id: str, name: str) -> Optional[str]:
    # Use sync to fetch sections and filter archived
    url = "https://api.todoist.com/api/v1/sync"
    data = {
        "sync_token": "*",
        "resource_types": json.dumps(["sections"]),
    }
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = requests.post(url, data=data, headers=headers)
    if resp.status_code != 200:
        return None
    payload = resp.json()
    sections = payload.get("sections", [])
    def _eq(a, b):
        try:
            return int(a) == int(b)
        except Exception:
            return a == b
    for s in sections:
        if _eq(s.get("project_id"), project_id) and s.get("name") == name and (s.get("is_archived") or s.get("archived") or s.get("is_archived_section")):
            return str(s.get("id"))
    return None


