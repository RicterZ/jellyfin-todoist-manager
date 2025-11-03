import os
import time
import uuid
import requests

from dotenv import load_dotenv

from config import TODOIST_API_KEY, TODOIST_PROJECT_ID
from todoist import TodoistClient


def delete_section(api_token: str, section_id: str) -> bool:
    """Delete a section via Todoist REST API (cleanup helper for tests)."""
    url = f"https://api.todoist.com/rest/v2/sections/{section_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
    }
    try:
        resp = requests.delete(url, headers=headers)
        # 204 No Content is expected on successful delete
        return resp.status_code == 204
    except requests.RequestException:
        return False


def print_sections(client: TodoistClient, project_id: str, title: str):
    sections = client.get_sections(project_id)
    sections_sorted = sorted(sections, key=lambda s: s.get("order", 0))
    print(f"\n== {title} ==")
    for s in sections_sorted:
        print(f"order={s.get('order')}, id={s.get('id')}, name={s.get('name')}")


def main():
    load_dotenv()

    api_key = TODOIST_API_KEY
    project_id = TODOIST_PROJECT_ID
    assert api_key and project_id, "TODOIST_API_KEY / TODOIST_PROJECT_ID is required"

    client = TodoistClient(api_key)

    # Create 3 temporary sections
    suffix = uuid.uuid4().hex[:6]
    sec_a_name = f"TEST_JTM_A_{suffix}"
    sec_b_name = f"TEST_JTM_B_{suffix}"
    sec_c_name = f"TEST_JTM_C_{suffix}"

    sec_a = client.create_section(project_id, sec_a_name)
    sec_b = client.create_section(project_id, sec_b_name)
    sec_c = client.create_section(project_id, sec_c_name)
    if not (sec_a and sec_b and sec_c):
        raise RuntimeError("Failed to create test sections")

    sec_a_id = sec_a.get("id")
    sec_b_id = sec_b.get("id")
    sec_c_id = sec_c.get("id")

    try:
        print_sections(client, project_id, "Before creating tasks")

        # Create tasks to set created_at ordering: A(1 task), B(2 tasks), C(empty)
        client.add_task(content=f"A-task-1-{suffix}", project_id=project_id, section_id=sec_a_id, due_string="today")
        time.sleep(1)
        client.add_task(content=f"B-task-1-{suffix}", project_id=project_id, section_id=sec_b_id, due_string="today")
        time.sleep(1)
        client.add_task(content=f"B-task-2-{suffix}", project_id=project_id, section_id=sec_b_id, due_string="today")

        # Reorder with B at front (as if B just received a new task)
        client.reorder_sections(project_id, front_section_id=sec_b_id)
        print_sections(client, project_id, "After reorder with front=B (expect: B first, C last)")

        # Make A empty by completing its only task, then reorder again
        tasks = client.get_tasks(project_id=project_id)
        a_tasks = [t for t in tasks if t.get("section_id") == sec_a_id]
        for t in a_tasks:
            client.complete_task(t.get("id"))

        client.reorder_sections(project_id)
        print_sections(client, project_id, "After completing A tasks and reorder (expect: A last)")

        print("\nTest finished. Manually verify the orders printed above in Todoist if desired.")
    finally:
        # Cleanup created sections (best-effort). Sections must be empty to delete.
        # Try to close remaining tasks under our test sections first
        tasks = client.get_tasks(project_id=project_id)
        for t in tasks:
            if t.get("section_id") in {sec_a_id, sec_b_id, sec_c_id}:
                try:
                    client.complete_task(t.get("id"))
                except Exception:
                    pass
        # Attempt to delete sections
        for sid in [sec_a_id, sec_b_id, sec_c_id]:
            try:
                delete_section(api_key, sid)
            except Exception:
                pass


if __name__ == "__main__":
    main()


