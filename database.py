import sqlite3
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path("jellyfin_todoist.db")


def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database and create tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jellyfin_item_id TEXT NOT NULL UNIQUE,
            todoist_item_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def save_mapping(jellyfin_item_id: str, todoist_item_id: str) -> bool:
    """
    Save mapping between Jellyfin item ID and Todoist item ID
    
    Args:
        jellyfin_item_id: Jellyfin item ID
        todoist_item_id: Todoist item ID
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO item_mappings (jellyfin_item_id, todoist_item_id)
            VALUES (?, ?)
        """, (jellyfin_item_id, todoist_item_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved mapping: Jellyfin {jellyfin_item_id} -> Todoist {todoist_item_id}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error saving mapping: {e}")
        return False


def get_todoist_item_id(jellyfin_item_id: str) -> Optional[str]:
    """
    Get Todoist item ID by Jellyfin item ID
    
    Args:
        jellyfin_item_id: Jellyfin item ID
        
    Returns:
        Todoist item ID if found, None otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT todoist_item_id FROM item_mappings
            WHERE jellyfin_item_id = ?
        """, (jellyfin_item_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['todoist_item_id']
        return None
    except sqlite3.Error as e:
        logger.error(f"Error getting Todoist item ID: {e}")
        return None


def mark_completed(jellyfin_item_id: str) -> bool:
    """
    Mark mapping as completed
    
    Args:
        jellyfin_item_id: Jellyfin item ID
        
    Returns:
        True if updated successfully, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE item_mappings
            SET completed_at = CURRENT_TIMESTAMP
            WHERE jellyfin_item_id = ?
        """, (jellyfin_item_id,))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        if affected_rows > 0:
            logger.info(f"Marked as completed: Jellyfin {jellyfin_item_id}")
            return True
        return False
    except sqlite3.Error as e:
        logger.error(f"Error marking as completed: {e}")
        return False

