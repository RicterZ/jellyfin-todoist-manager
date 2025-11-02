import logging
from typing import Optional, Dict, Any
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

