import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Todoist configuration
TODOIST_API_KEY = os.getenv('TODOIST_API_KEY')
TODOIST_PROJECT_ID = os.getenv('TODOIST_PROJECT_ID')

# Validate required environment variables
if not TODOIST_API_KEY:
    raise ValueError("TODOIST_API_KEY is not set in environment variables")
if not TODOIST_PROJECT_ID:
    raise ValueError("TODOIST_PROJECT_ID is not set in environment variables")

