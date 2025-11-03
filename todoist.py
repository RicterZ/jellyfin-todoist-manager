import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class TodoistClient:
    """Todoist API client utility class"""
    
    BASE_URL = "https://api.todoist.com/rest/v2"
    
    def __init__(self, api_token: str):
        """
        Initialize Todoist client
        
        Args:
            api_token: Todoist API token, can be obtained from https://todoist.com/app/settings/integrations
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def add_task(
        self,
        content: str,
        project_id: Optional[str] = None,
        section_id: Optional[str] = None,
        due_string: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: int = 1,
        description: Optional[str] = None,
        labels: Optional[list] = None,
        order: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Add a new task (todo)
        
        Args:
            content: Task content (required)
            project_id: Project ID, if not provided will be added to inbox
            section_id: Section ID, if provided task will be added to this section
            due_string: Due date string, e.g. "tomorrow", "next Monday", "2024-01-15"
            due_date: Due date in YYYY-MM-DD format
            priority: Priority level, 1-4 (1=normal, 2=important, 3=urgent, 4=very urgent)
            description: Task description
            labels: List of label IDs
            order: Task order
            
        Returns:
            Task object (contains task ID and other info) on success, None on failure
        """
        url = f"{self.BASE_URL}/tasks"
        
        payload: Dict[str, Any] = {
            "content": content,
            "priority": priority
        }
        
        if project_id:
            payload["project_id"] = project_id
        
        if section_id:
            payload["section_id"] = section_id
        
        if due_string:
            payload["due_string"] = due_string
        elif due_date:
            payload["due_date"] = due_date
        
        if description:
            payload["description"] = description
        
        if labels:
            payload["label_ids"] = labels
        
        if order is not None:
            payload["order"] = order
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            task = response.json()
            logger.info(f"Task added successfully: {content} (ID: {task.get('id')})")
            return task
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add task: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
    
    def complete_task(self, task_id: str) -> bool:
        """
        Mark a task as completed
        
        Args:
            task_id: Task ID
            
        Returns:
            True on success, False on failure
        """
        url = f"{self.BASE_URL}/tasks/{task_id}/close"
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Task completed successfully: {task_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to complete task: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task details
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object on success, None on failure
        """
        url = f"{self.BASE_URL}/tasks/{task_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get task: {e}")
            return None
    
    def get_tasks(
        self,
        project_id: Optional[str] = None,
        label_id: Optional[str] = None,
        filter: Optional[str] = None
    ) -> list:
        """
        Get list of tasks
        
        Args:
            project_id: Project ID, filter tasks by specific project
            label_id: Label ID, filter tasks by specific label
            filter: Filter string, e.g. "today", "completed"
            
        Returns:
            List of tasks
        """
        url = f"{self.BASE_URL}/tasks"
        params = {}
        
        if project_id:
            params["project_id"] = project_id
        if label_id:
            params["label_id"] = label_id
        if filter:
            params["filter"] = filter
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    def get_projects(self) -> list:
        """
        Get list of all projects
        
        Returns:
            List of projects
        """
        url = f"{self.BASE_URL}/projects"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get projects: {e}")
            return []
    
    def get_project_by_name(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Get project by name
        
        Args:
            project_name: Project name to search for
            
        Returns:
            Project object if found, None otherwise
        """
        projects = self.get_projects()
        
        for project in projects:
            if project.get('name') == project_name:
                return project
        
        return None
    
    def create_project(
        self,
        name: str,
        parent_id: Optional[str] = None,
        color: Optional[str] = None,
        is_favorite: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new project
        
        Args:
            name: Project name (required)
            parent_id: Parent project ID (for sub-projects)
            color: Project color (integer 30-49 or string name)
            is_favorite: Whether the project is favorite
            
        Returns:
            Project object on success, None on failure
        """
        url = f"{self.BASE_URL}/projects"
        
        payload: Dict[str, Any] = {
            "name": name,
            "is_favorite": is_favorite
        }
        
        if parent_id:
            payload["parent_id"] = parent_id
        if color:
            payload["color"] = color
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            project = response.json()
            logger.info(f"Created project: {name} (ID: {project.get('id')})")
            return project
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create project: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
    
    def get_or_create_project(self, project_name: str) -> Optional[str]:
        """
        Get existing project by name, or create a new one if it doesn't exist
        
        Args:
            project_name: Project name
            
        Returns:
            Project ID if successful, None on failure
        """
        existing_project = self.get_project_by_name(project_name)
        if existing_project:
            return existing_project.get('id')
        
        new_project = self.create_project(name=project_name)
        if new_project and new_project.get('id'):
            return new_project.get('id')
        
        return None
    
    def get_sections(self, project_id: str) -> list:
        """
        Get list of sections for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            List of sections
        """
        url = f"{self.BASE_URL}/sections"
        params = {"project_id": project_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get sections: {e}")
            return []
    
    def get_section_by_name(self, project_id: str, section_name: str) -> Optional[Dict[str, Any]]:
        """
        Get section by name in a project
        
        Args:
            project_id: Project ID
            section_name: Section name to search for
            
        Returns:
            Section object if found, None otherwise
        """
        sections = self.get_sections(project_id)
        
        for section in sections:
            if section.get('name') == section_name:
                return section
        
        return None
    
    def create_section(self, project_id: str, name: str, order: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new section in a project
        
        Args:
            project_id: Project ID
            name: Section name (required)
            order: Section order
            
        Returns:
            Section object on success, None on failure
        """
        url = f"{self.BASE_URL}/sections"
        
        payload: Dict[str, Any] = {
            "project_id": project_id,
            "name": name
        }
        
        if order is not None:
            payload["order"] = order
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            section = response.json()
            logger.info(f"Created section: {name} (ID: {section.get('id')}) in project {project_id}")
            return section
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create section: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
    
    def get_or_create_section(self, project_id: str, section_name: str) -> Optional[str]:
        """
        Get existing section by name in a project, or create a new one if it doesn't exist
        
        Args:
            project_id: Project ID
            section_name: Section name
            
        Returns:
            Section ID if successful, None on failure
        """
        existing_section = self.get_section_by_name(project_id, section_name)
        if existing_section:
            return existing_section.get('id')
        
        new_section = self.create_section(project_id=project_id, name=section_name)
        if new_section and new_section.get('id'):
            return new_section.get('id')
        
        return None
    
    def update_section(self, section_id: str, name: Optional[str] = None, order: Optional[int] = None) -> bool:
        """
        Update a section (name or order)
        
        Args:
            section_id: Section ID
            name: New section name (optional)
            order: New section order (optional)
            
        Returns:
            True on success, False on failure
        """
        url = f"{self.BASE_URL}/sections/{section_id}"
        
        payload: Dict[str, Any] = {}
        
        if name is not None:
            payload["name"] = name
        if order is not None:
            payload["order"] = order
        
        if not payload:
            return False
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Updated section {section_id} (name={name}, order={order})")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update section: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return False
    
    def is_section_empty(self, project_id: str, section_id: str) -> bool:
        """
        Check if a section has no active (uncompleted) tasks
        
        Args:
            project_id: Project ID
            section_id: Section ID
            
        Returns:
            True if section is empty (no active tasks), False otherwise
        """
        tasks = self.get_tasks(project_id=project_id)
        
        for task in tasks:
            if task.get('section_id') == section_id:
                if not task.get('is_completed', False):
                    return False
        
        return True
    
    def move_empty_section_to_end(self, project_id: str, section_id: str) -> bool:
        """
        Move an empty section to the end of the project
        
        Args:
            project_id: Project ID
            section_id: Section ID
            
        Returns:
            True on success, False on failure
        """
        sections = self.get_sections(project_id)
        
        if not sections:
            logger.warning(f"No sections found for project {project_id}")
            return False
        
        target_section = next((s for s in sections if s.get('id') == section_id), None)
        if not target_section:
            logger.warning(f"Section {section_id} not found in project {project_id}")
            return False
        
        current_order = target_section.get('order', 0)
        max_order = max((s.get('order', 0) for s in sections), default=0)
        
        if current_order >= max_order:
            return True
        
        new_order = max_order + 1
        return self.update_section(section_id, order=new_order)

    def _parse_created_at(self, created_at: Optional[str]) -> float:
        """
        Parse Todoist ISO8601 created_at to timestamp seconds.
        Returns 0.0 if parsing fails or value missing.
        """
        if not created_at or not isinstance(created_at, str):
            return 0.0
        try:
            # Todoist uses ISO8601, e.g. "2023-09-18T10:20:30.000000Z"
            value = created_at.replace("Z", "+00:00")
            return datetime.fromisoformat(value).timestamp()
        except Exception:
            return 0.0

    def reorder_sections(self, project_id: str, front_section_id: Optional[str] = None) -> bool:
        """
        Reorder sections for a project with rules:
        1) Empty sections go to the end
        2) The section that just received a new task goes to the front
        3) Other sections sorted by latest task created_at in descending order

        Args:
            project_id: Todoist project ID
            front_section_id: Section ID to force to the very front (optional)

        Returns:
            True if at least one section order was updated, False otherwise
        """
        sections = self.get_sections(project_id)
        if not sections:
            return False

        tasks = self.get_tasks(project_id=project_id)  # active (uncompleted) tasks

        # Build section -> latest_created_at and empty flag
        latest_by_section: Dict[str, float] = {}
        has_task_by_section: Dict[str, bool] = {}

        for task in tasks:
            sid = task.get("section_id")
            if not sid:
                continue
            has_task_by_section[sid] = True
            created_ts = self._parse_created_at(task.get("created_at"))
            prev = latest_by_section.get(sid, 0.0)
            if created_ts > prev:
                latest_by_section[sid] = created_ts

        # Compose sortable entries
        sortable: List[Tuple[int, float, str, Dict[str, Any]]] = []
        for s in sections:
            sid = s.get("id")
            is_empty = not has_task_by_section.get(sid, False)
            # Priority key: non-empty=0, empty=1 so empties go last
            empty_rank = 1 if is_empty else 0
            # Front boost: if equals front_section_id, use special rank -1 to force front
            front_rank = -1 if (front_section_id and sid == front_section_id) else 0
            # Latest timestamp for sorting (desc), default 0.0
            latest_ts = latest_by_section.get(sid, 0.0)

            # The overall priority tuple sorts by (front_rank, empty_rank, -latest_ts)
            # We can't sort by negative easily in tuple with float; store positive and invert later
            sortable.append((front_rank, empty_rank, latest_ts, sid, s))

        # Sort: front_rank asc (-1 first), then empty_rank asc (non-empty first), then latest_ts desc
        sortable.sort(key=lambda t: (t[0], t[1], -t[2]))

        # Assign new sequential orders starting from 1
        changed = False
        for index, (_, __, ___, sid, s) in enumerate(sortable, start=1):
            current_order = s.get("order")
            if current_order != index:
                ok = self.update_section(sid, order=index)
                if ok:
                    changed = True
        return changed

