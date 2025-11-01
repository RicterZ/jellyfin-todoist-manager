import logging
from typing import Dict, Any

from utils import parse_time_string, format_series_title

logger = logging.getLogger(__name__)


async def handle_item_added(data: Dict[str, Any]):
    """Handle Item Added event"""
    logger.info(f"Item Added: {data}")


async def handle_playback_stop(data: Dict[str, Any]):
    """Handle Playback Stop event, check if playback is completed based on RunTime and PlaybackPosition"""
    
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
    
    # Output result only when completed
    if is_completed:
        title = format_series_title(data)
        print(f"✅ Completed: {title}")
    else:
        return

