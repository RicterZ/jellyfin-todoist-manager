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


def format_series_title(data: Dict[str, Any]) -> str:
    """
    Format series title based on item type and data
    
    Args:
        data: Webhook data dictionary containing item information
        
    Returns:
        Formatted title string
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
                title = f"{series_name} S{season_number:02d}E{episode_number:02d} - {item_id}"
            else:
                title = f"{series_name} - {item_name} - {item_id}"
        else:
            title = f"{item_name} - {item_id}" if data.get('Id') else item_name
    else:
        title = f"{item_name} - {data.get('Id', '')}" if data.get('Id') else item_name
    
    return title

