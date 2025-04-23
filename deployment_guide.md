# Deployment Guide for Social Media Automation System

This guide will walk you through deploying the Social Media Automation System to Render.

## Prerequisites

- A Render account (https://render.com)
- A GitHub repository with your Social Media Automation System code
- TikTok API credentials (Content Posting API)
- Instagram API credentials (Graph API)

## Deployment Files

The following files have been prepared for deployment:

1. **Procfile**: Defines the web and worker processes
2. **runtime.txt**: Specifies the Python version
3. **app.py**: Flask application with API endpoints
4. **worker.py**: Background worker for scheduling and analysis

## Deployment Steps

### 1. Push Code to GitHub

First, ensure all the deployment files are pushed to your GitHub repository:

```bash
git add Procfile runtime.txt app.py worker.py
git commit -m "Add deployment files"
git push origin main
```

### 2. Create a New Web Service on Render

1. Log in to your Render account
2. Click on "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service with the following settings:
   - **Name**: social-media-automation (or your preferred name)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Choose an appropriate plan (Start with the free plan for testing)

### 3. Set Up Environment Variables

In the Render dashboard, add the following environment variables:

- `TIKTOK_API_KEY`: Your TikTok API key
- `TIKTOK_API_SECRET`: Your TikTok API secret
- `INSTAGRAM_USERNAME`: Your Instagram username
- `INSTAGRAM_PASSWORD`: Your Instagram password
- `FLASK_ENV`: production
- `FLASK_SECRET_KEY`: A random secret key for Flask

### 4. Create a Background Worker

1. In the Render dashboard, click on "New" and select "Background Worker"
2. Connect to the same GitHub repository
3. Configure the worker with the following settings:
   - **Name**: social-media-automation-worker
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python worker.py`
   - **Plan**: Choose an appropriate plan

### 5. Set Up Persistent Disk

1. In the Render dashboard, go to your web service
2. Click on "Disks" in the left sidebar
3. Click "Create Disk"
4. Configure the disk with the following settings:
   - **Name**: social-media-data
   - **Size**: 1 GB (increase as needed)
   - **Mount Path**: `/data`

### 6. Update Configuration for Persistent Storage

Update your application to use the persistent disk for data storage:

```python
# In your application code
DATA_DIR = os.environ.get('DATA_DIR', '/data')
```

Add this environment variable to both the web service and worker:
- `DATA_DIR`: `/data`

## Monitoring and Maintenance

### Logs

- Monitor application logs in the Render dashboard
- Check for any errors or issues in the logs

### Scaling

- If needed, upgrade your plan to handle increased load
- Adjust worker frequency based on your posting schedule

### Backups

- Regularly back up your data from the persistent disk
- Consider setting up automated backups

## Troubleshooting

### Common Issues

1. **API Rate Limiting**: If you encounter rate limiting issues, adjust your posting frequency
2. **Worker Timeouts**: If worker processes timeout, consider breaking tasks into smaller chunks
3. **Disk Space**: Monitor disk usage and increase size if needed

### Support

If you encounter any issues with the deployment, refer to:
- Render documentation: https://render.com/docs
- Open an issue in the GitHub repository

## Next Steps

After deployment, you can:

1. Access your application at the URL provided by Render
2. Configure your social media automation settings
3. Generate and execute content plans
4. Monitor performance through weekly reports
