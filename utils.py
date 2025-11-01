from typing import Dict, Any, Optional


def parse_time_string(time_str: str) -> Optional[int]:
    """
    Parse time string in HH:MM:SS format to total seconds
    
    Args:
        time_str: Time string in format HH:MM:SS or MM:SS
        
    Returns:
        Total seconds, or None if parsing fails
    """
    if not time_str:
        return None
    
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return None
    except (ValueError, AttributeError):
        return None


def get_series_name(data: Dict[str, Any]) -> str:
    """
    Get series name from data
    
    Args:
        data: Webhook data dictionary containing item information
        
    Returns:
        Series name, or item name if not an episode
    """
    item_type = data.get('ItemType', '')
    
    if item_type == 'Episode':
        series_name = data.get('SeriesName', '')
        if series_name:
            return series_name
    
    # For non-episode items, return item name
    return data.get('ItemName', 'Unknown')


def format_task_title(data: Dict[str, Any]) -> str:
    """
    Format task title with episode number only (for Todoist tasks)
    Since the section already shows series name, task only needs episode info
    
    Args:
        data: Webhook data dictionary containing item information
        
    Returns:
        Formatted task title string (e.g., "S01E05")
    """
    item_type = data.get('ItemType', '')
    
    if item_type == 'Episode':
        season_number = data.get('SeasonNumber', '')
        episode_number = data.get('EpisodeNumber', '')
        
        if season_number and episode_number:
            # Convert to int if possible, otherwise use as string
            try:
                season_int = int(season_number)
                episode_int = int(episode_number)
                return f"S{season_int:02d}E{episode_int:02d}"
            except (ValueError, TypeError):
                # If conversion fails, use as string
                return f"S{season_number}E{episode_number}"
        elif episode_number:
            # Only episode number available
            try:
                episode_int = int(episode_number)
                return f"E{episode_int:02d}"
            except (ValueError, TypeError):
                return f"E{episode_number}"
    
    # For non-episode items, use item name
    return data.get('ItemName', 'Unknown')


def format_series_title(data: Dict[str, Any]) -> str:
    """
    Format full series title (for logging/display purposes)
    
    Args:
        data: Webhook data dictionary containing item information
        
    Returns:
        Formatted title string with series name and episode info
    """
    item_name = data.get('ItemName', 'N/A')
    item_type = data.get('ItemType', '')
    
    if item_type == 'Episode':
        series_name = data.get('SeriesName', '')
        if series_name:
            season_number = data.get('SeasonNumber', '')
            episode_number = data.get('EpisodeNumber', '')
            item_id = data.get('Id', '')
            
            if season_number and episode_number:
                # Convert to int if possible, otherwise use as string
                try:
                    season_int = int(season_number)
                    episode_int = int(episode_number)
                    title = f"{series_name} S{season_int:02d}E{episode_int:02d} - {item_id}"
                except (ValueError, TypeError):
                    # If conversion fails, use as string
                    title = f"{series_name} S{season_number}E{episode_number} - {item_id}"
            else:
                title = f"{series_name} - {item_name} - {item_id}"
        else:
            title = f"{item_name} - {item_id}" if data.get('Id') else item_name
    else:
        title = f"{item_name} - {data.get('Id', '')}" if data.get('Id') else item_name
    
    return title

