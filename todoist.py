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

