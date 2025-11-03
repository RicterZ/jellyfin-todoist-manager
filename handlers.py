import logging
from typing import Dict, Any
import time

from config import TODOIST_API_KEY, TODOIST_PROJECT_ID
from database import save_mapping, get_todoist_item_id, mark_completed
from utils import format_task_title, format_series_title, parse_time_string, get_series_name
from todoist_api_python.api import TodoistAPI
from todoist_helpers import (
    get_or_create_section,
    get_archived_section_by_name,
    unarchive_section,
    archive_section,
    is_section_empty,
)

logger = logging.getLogger(__name__)

# Initialize Todoist SDK client
todoist_api = TodoistAPI(TODOIST_API_KEY)


async def handle_item_added(data: Dict[str, Any]):
    """Handle Item Added event - create Todoist section if needed, then create task"""
    # Get Jellyfin item ID - prioritize ItemId over Id
    # ItemId is the actual media item ID, while Id might be a session/event ID
    jellyfin_item_id = data.get('ItemId') or data.get('Id') or data.get('item_id') or data.get('id')
    
    if not jellyfin_item_id:
        logger.warning("No Jellyfin item ID found in ItemAdded event")
        return
    
    # Get series name for section
    series_name = get_series_name(data)
    
    # If a section with same name was archived, unarchive and reuse it; otherwise get/create
    archived_section = get_archived_section_by_name(TODOIST_API_KEY, TODOIST_PROJECT_ID, series_name)
    if archived_section:
        section_id = archived_section
        if not unarchive_section(TODOIST_API_KEY, section_id):
            logger.error(f"Failed to unarchive section for series: {series_name}")
            return
    else:
        # Get or create section based on series name in the configured project
        section_id = get_or_create_section(todoist_api, TODOIST_PROJECT_ID, series_name)
    
    if not section_id:
        logger.error(f"Failed to get or create section for series: {series_name}")
        return
    
    # Format title for Todoist task (only episode number, since section has series name)
    title = format_task_title(data)
    
    # Create Todoist task in the section (no description needed, due date is today)
    try:
        task = todoist_api.add_task(content=title, project_id=TODOIST_PROJECT_ID, section_id=section_id, due_string="today")
    except Exception as e:
        # Print detailed SDK error if available
        err_msg = getattr(e, 'message', str(e))
        status_code = getattr(e, 'status_code', None)
        response_body = getattr(e, 'response_body', None)
        logger.error(f"Failed to add task via SDK: {err_msg} (status={status_code}) body={response_body}")
        return
    
    if task and getattr(task, 'id', None):
        todoist_item_id = task.id
        # Save mapping to database
        if save_mapping(jellyfin_item_id, todoist_item_id):
            logger.info(f"Created Todoist task {todoist_item_id} in section '{series_name}' for Jellyfin item {jellyfin_item_id}")
        else:
            logger.error(f"Failed to save mapping for Jellyfin item {jellyfin_item_id}")
    else:
        logger.error(f"Failed to create Todoist task for Jellyfin item {jellyfin_item_id}")


async def handle_playback_stop(data: Dict[str, Any]):
    """Handle Playback Stop event, check if playback is completed and mark Todoist task as done"""
    
    # Get time values
    runtime_str = data.get('RunTime', '')
    playback_position_str = data.get('PlaybackPosition', '')
    
    # Parse time strings to seconds
    runtime_seconds = parse_time_string(runtime_str) if runtime_str else None
    playback_position_seconds = parse_time_string(playback_position_str) if playback_position_str else None
    
    # Check if we have valid time data
    if runtime_seconds is None or playback_position_seconds is None:
        return
    
    # Calculate difference
    time_diff = abs(runtime_seconds - playback_position_seconds)
    
    # Check if completed (difference <= 1 minute)
    is_completed = time_diff <= 60
    
    # Only process if completed
    if not is_completed:
        return
    
    # Get Jellyfin item ID - prioritize ItemId over Id
    # ItemId is the actual media item ID, while Id might be a session/event ID
    jellyfin_item_id = data.get('ItemId') or data.get('Id') or data.get('item_id') or data.get('id')
    
    if not jellyfin_item_id:
        logger.warning("No Jellyfin item ID found in playback stop data")
        return
    
    # Get Todoist item ID from database
    todoist_item_id = get_todoist_item_id(jellyfin_item_id)
    
    if not todoist_item_id:
        logger.warning(f"No Todoist task found for Jellyfin item {jellyfin_item_id}")
        return
    
    # Resolve section by series name (avoid get_task on completed tasks which may error)
    section_id = None
    series_name = get_series_name(data)
    try:
        sections = todoist_api.get_sections(project_id=TODOIST_PROJECT_ID)
        for s in sections:
            if s.name == series_name:
                section_id = s.id
                break
    except Exception as e:
        err_msg = getattr(e, 'message', str(e))
        status_code = getattr(e, 'status_code', None)
        response_body = getattr(e, 'response_body', None)
        logger.error(f"Failed to list sections via SDK: {err_msg} (status={status_code}) body={response_body}")
    
    # Mark Todoist task as completed
    closed_ok = False
    try:
        closed_ok = todoist_api.complete_task(task_id=todoist_item_id)
    except Exception as e:
        err_msg = getattr(e, 'message', str(e))
        status_code = getattr(e, 'status_code', None)
        response_body = getattr(e, 'response_body', None)
        logger.error(f"Failed to complete task via SDK: {err_msg} (status={status_code}) body={response_body}")
        closed_ok = False

    if closed_ok:
        # Update database to mark as completed
        mark_completed(jellyfin_item_id)
        title = format_series_title(data)
        logger.info(f"Marked Todoist task {todoist_item_id} as completed for: {title}")
        print(f"✅ Completed: {title}")
        
        # If section is empty after completion, archive it (with short retry for consistency)
        # section_id was already resolved above; no further fallback

        if section_id:
            empty = False
            for _ in range(5):  # retry up to ~2.5s
                if is_section_empty(todoist_api, TODOIST_PROJECT_ID, section_id):
                    empty = True
                    break
                time.sleep(0.5)
            if empty:
                if archive_section(TODOIST_API_KEY, section_id):
                    logger.info(f"Archived empty section: {section_id}")
                else:
                    logger.warning(f"Failed to archive empty section: {section_id}")
    else:
        logger.error(f"Failed to complete Todoist task {todoist_item_id}")

