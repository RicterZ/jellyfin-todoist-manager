import json
import logging
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException

from database import init_database
from handlers import handle_item_added, handle_playback_stop

# Load environment variables
load_dotenv()

# Initialize database
init_database()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(title="Jellyfin Todoist Manager", version="1.0.0")


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Main endpoint for receiving Jellyfin webhook events"""
    try:
        body = await request.body()
        body_str = body.decode('utf-8')
        
        webhook_data = json.loads(body_str)
        notification_type = webhook_data.get('NotificationType', '')
        
        # Log webhook data structure for debugging ID extraction
        logger.debug(f"Webhook received - Type: {notification_type}")
        logger.debug(f"Webhook data keys: {list(webhook_data.keys())}")
        
        # Log all possible ID-related fields
        id_fields = ['Id', 'ItemId', 'item_id', 'id']
        for field in id_fields:
            if field in webhook_data:
                logger.debug(f"  {field}: {webhook_data[field]}")
        
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
