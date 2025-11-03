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

todoist_api = TodoistAPI(TODOIST_API_KEY)


async def handle_item_added(data: Dict[str, Any]):
    jellyfin_item_id = data.get('ItemId')
    
    if not jellyfin_item_id:
        logger.warning("No Jellyfin item ID found in ItemAdded event")
        return
    
    series_name = get_series_name(data)
    
    archived_section = get_archived_section_by_name(TODOIST_API_KEY, TODOIST_PROJECT_ID, series_name)
    if archived_section:
        section_id = archived_section
        if not unarchive_section(TODOIST_API_KEY, section_id):
            logger.error(f"Failed to unarchive section for series: {series_name}")
            return
    else:
        section_id = get_or_create_section(todoist_api, TODOIST_PROJECT_ID, series_name)
    
    if not section_id:
        logger.error(f"Failed to get or create section for series: {series_name}")
        return
    
    title = format_task_title(data)
    
    try:
        logger.info(
            f"Todoist add_task params: content='{title}', project_id={TODOIST_PROJECT_ID}, section_id={section_id}, due_string='today'"
        )
        task = todoist_api.add_task(content=title, project_id=TODOIST_PROJECT_ID, section_id=section_id, due_string="today")
    except Exception as e:
        err_msg = getattr(e, 'message', str(e))
        status_code = getattr(e, 'status_code', None)
        response_body = getattr(e, 'response_body', None)
        logger.error(f"Failed to add task via SDK: {err_msg} (status={status_code}) body={response_body}")
        return
    
    if task and getattr(task, 'id', None):
        todoist_item_id = task.id
        if save_mapping(jellyfin_item_id, todoist_item_id):
            logger.info(f"Created Todoist task {todoist_item_id} in section '{series_name}' for Jellyfin item {jellyfin_item_id}")
        else:
            logger.error(f"Failed to save mapping for Jellyfin item {jellyfin_item_id}")
    else:
        logger.error(f"Failed to create Todoist task for Jellyfin item {jellyfin_item_id}")


async def handle_playback_stop(data: Dict[str, Any]):
    
    runtime_str = data.get('RunTime', '')
    playback_position_str = data.get('PlaybackPosition', '')
    
    runtime_seconds = parse_time_string(runtime_str) if runtime_str else None
    playback_position_seconds = parse_time_string(playback_position_str) if playback_position_str else None
    
    if runtime_seconds is None or playback_position_seconds is None:
        return
    
    time_diff = abs(runtime_seconds - playback_position_seconds)
    
    is_completed = time_diff <= 60
    
    if not is_completed:
        return
    
    jellyfin_item_id = data.get('ItemId')
    
    if not jellyfin_item_id:
        logger.warning("No Jellyfin item ID found in playback stop data")
        return
    
    todoist_item_id = get_todoist_item_id(jellyfin_item_id)
    logger.info(f"Mapping lookup: Jellyfin {jellyfin_item_id} -> Todoist {todoist_item_id}")
    if not todoist_item_id:
        logger.warning(f"No Todoist task found for Jellyfin item {jellyfin_item_id}")
        return
    
    section_id = None
    
    closed_ok = False
    try:
        logger.info(f"Todoist complete_task params: task_id={todoist_item_id!r}")
        closed_ok = todoist_api.complete_task(task_id=todoist_item_id)
    except Exception as e:
        err_msg = getattr(e, 'message', str(e))
        status_code = getattr(e, 'status_code', None)
        response_body = getattr(e, 'response_body', None)
        if status_code == 400 or (isinstance(err_msg, str) and '400' in err_msg):
            logger.warning(f"Treating complete_task 400 as already completed for task {todoist_item_id}")
            closed_ok = True
        else:
            logger.error(f"Failed to complete task via SDK: {err_msg} (status={status_code}) body={response_body}")
            closed_ok = False

    if closed_ok:
        mark_completed(jellyfin_item_id)
        title = format_series_title(data)
        logger.info(f"Marked Todoist task {todoist_item_id} as completed for: {title}")
        print(f"✅ Completed: {title}")

        if section_id:
            empty = False
            for _ in range(5):
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

