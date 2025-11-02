# Jellyfin Todoist Manager

Automatically manage your Todoist tasks based on Jellyfin media library events. When you add new episodes to Jellyfin, tasks are created in Todoist. When you finish watching an episode, the task is automatically marked as completed.

## Features

- Automatically creates Todoist tasks when new episodes are added to Jellyfin
- Marks tasks as completed when you finish watching an episode
- Organizes tasks by series in Todoist sections
- Moves empty sections to the end of the project

<img width="2094" height="1261" alt="image" src="https://github.com/user-attachments/assets/cebdb8b6-4416-4b0e-b736-202c52bc83b9" />


## Deployment

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd jellyfin-webhook
```

2. Create a `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your credentials:
```
TODOIST_API_KEY=your_todoist_api_key_here
TODOIST_PROJECT_ID=your_todoist_project_id_here
```

4. Start the service:
```bash
docker-compose up -d
```

The service will be available at `http://localhost:8000`

## Configuration

### Getting Todoist API Token

1. Go to [Todoist Settings](https://todoist.com/app/settings/integrations)
2. Scroll to "Developer" section
3. Copy your API token

### Getting Todoist Project ID

1. Open your Todoist project in a web browser
2. The project ID is in the URL: `https://todoist.com/app/project/{PROJECT_ID}/...`

### Setting up Jellyfin Webhook

1. In Jellyfin, go to **Dashboard → Webhooks**
2. Click **Add Webhook**
3. Configure the webhook:
   - **Webhook URL**: `http://your-server-ip:8000/webhook`
     - If running on the same machine as Jellyfin: `http://localhost:8000/webhook`
     - If running in Docker on the same machine: `http://host.docker.internal:8000/webhook`
   - **Enable the following notification types**:
     - ✅ Item Added
     - ✅ Playback Stop

<img width="1980" height="1187" alt="image" src="https://github.com/user-attachments/assets/effcf545-17e6-48a4-aed2-f36dc784a15e" />


4. Save the webhook configuration

## How It Works

1. **When a new episode is added**: A Todoist section is created (named after the series) if it doesn't exist, and a task is added with episode information (e.g., "S01E05")

2. **When you finish watching**: The task is automatically marked as completed in Todoist. If all tasks in a section are completed, the section is moved to the end of the project

## License

MIT License

