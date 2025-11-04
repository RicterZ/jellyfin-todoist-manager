import json
import logging
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException

from database import init_database
from handlers import handle_item_added, handle_playback_stop
from config import TODOIST_API_KEY, TODOIST_PROJECT_ID
from todoist_api_python.api import TodoistAPI
from todoist_helpers import start_background_section_archiver

# Load environment variables
load_dotenv()

# Initialize database
init_database()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(title="Jellyfin Todoist Manager", version="1.0.0")
# Start background archiver thread
try:
    interval = int(os.getenv("SECTION_ARCHIVE_SCAN_INTERVAL", "120"))
except ValueError:
    interval = 120
_bg_api = TodoistAPI(TODOIST_API_KEY)
start_background_section_archiver(_bg_api, TODOIST_PROJECT_ID, TODOIST_API_KEY, interval)



@app.post("/webhook")
async def receive_webhook(request: Request):
    """Main endpoint for receiving Jellyfin webhook events"""
    try:
        body = await request.body()
        body_str = body.decode('utf-8')
        
        webhook_data = json.loads(body_str)
        notification_type = webhook_data.get('NotificationType', '')
        
        if notification_type == 'ItemAdded':
            await handle_item_added(webhook_data)
        elif notification_type == 'PlaybackStop':
            await handle_playback_stop(webhook_data)
        
        return {"status": "success", "message": "Webhook received and processed"}
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
