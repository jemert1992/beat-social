# Social Media Content Automation System - User Guide

## Overview

The Social Media Content Automation System is a comprehensive solution designed to automate content creation, scheduling, and performance tracking for TikTok and Instagram. This system analyzes trending content in your specified niche, generates engaging posts, and optimizes your social media strategy based on performance data.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [System Configuration](#system-configuration)
5. [Content Generation](#content-generation)
6. [Scheduling and Posting](#scheduling-and-posting)
7. [Performance Tracking](#performance-tracking)
8. [Weekly Reports](#weekly-reports)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## System Requirements

- Python 3.10 or higher
- Internet connection for trend analysis and posting
- TikTok and Instagram accounts with API access
- Sufficient storage space for generated content

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/social-media-automation.git
   cd social-media-automation
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up API credentials:
   Create a `.env` file in the root directory with the following variables:
   ```
   TIKTOK_API_KEY=your_tiktok_api_key
   TIKTOK_API_SECRET=your_tiktok_api_secret
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   ```

## Getting Started

To start using the system, follow these steps:

1. Configure the system with your niche and posting preferences
2. Generate a content plan
3. Execute the content plan to create and schedule posts
4. Review weekly performance reports

## System Configuration

The system can be configured through the command line or by directly editing the configuration file.

### Command Line Configuration

```python
from src.system import SocialMediaAutomationSystem

# Initialize the system
system = SocialMediaAutomationSystem("/path/to/base/directory")

# Configure the system
system.configure(
    niche="travel",                   # Your content niche
    tiktok_frequency=2,               # Posts per day on TikTok
    instagram_frequency=1,            # Posts per day on Instagram
    content_preferences={             # Optional content preferences
        "preferred_content_types": ["tutorial", "showcase"],
        "preferred_themes": ["adventure", "budget"]
    }
)
```

### Configuration Options

- **niche**: The content niche (e.g., weddings, fitness, travel)
- **tiktok_frequency**: Number of TikTok posts per day (1-3 recommended)
- **instagram_frequency**: Number of Instagram posts per day (1-2 recommended)
- **content_preferences**: Optional dictionary with preferences for content types and themes

## Content Generation

The system analyzes trending content in your niche and generates original content based on the trends.

### Content Plan Generation

```python
# Generate a content plan for 7 days
content_plan = system.generate_content_plan(days=7)
```

The content plan includes:
- Post frequency for each platform
- Recommended content types based on trend analysis
- Recommended themes based on trend analysis
- Detailed plan for each post

### Content Types

#### TikTok Content Types
- **tutorial**: Step-by-step instructional videos
- **tips**: Quick advice and helpful information
- **transformation**: Before and after showcases
- **showcase**: Highlighting products, places, or ideas
- **review**: Opinions and evaluations

#### Instagram Content Types
- **single_image**: Standard Instagram post with one image
- **carousel**: Multiple images in a swipeable format
- **reel**: Short vertical videos similar to TikTok
- **igtv**: Longer-form vertical videos

## Scheduling and Posting

The system automatically schedules and posts content at optimal times.

### Executing a Content Plan

```python
# Execute the generated content plan
execution_results = system.execute_content_plan(content_plan)
```

This process:
1. Creates content for each planned post
2. Generates captions and hashtags
3. Schedules posts at optimal times
4. Tracks post IDs for performance monitoring

### Optimal Posting Times

The system uses the following optimal posting times by default:

#### TikTok
- 7:00 PM
- 9:00 PM
- 11:00 PM
- 8:00 AM
- 12:00 PM

#### Instagram
- 12:00 PM
- 3:00 PM
- 6:00 PM
- 9:00 PM
- 9:00 AM

## Performance Tracking

The system tracks engagement metrics for all posts and uses this data to optimize future content.

### Tracked Metrics

#### TikTok Metrics
- Views
- Likes
- Comments
- Shares
- Engagement rate

#### Instagram Metrics
- Likes
- Comments
- Saves
- Followers
- Engagement rate

## Weekly Reports

The system generates comprehensive weekly reports to help you understand your social media performance.

### Generating a Report

```python
# Generate a weekly performance report
report_path = system.generate_weekly_report()
```

### Report Contents

- Summary of posting activity
- Top-performing posts
- Content type performance analysis
- Platform performance comparison
- Insights based on data analysis
- Recommendations for future content

## Troubleshooting

### Common Issues

#### Content Generation Failures
- **Issue**: Content generation fails with an error
- **Solution**: Check that the system has access to the internet and that the required libraries are installed

#### Scheduling Errors
- **Issue**: Posts fail to schedule
- **Solution**: Verify API credentials and check internet connectivity

#### API Rate Limiting
- **Issue**: API requests are being rate limited
- **Solution**: Reduce posting frequency or implement longer delays between posts

## FAQ

### How many posts can I schedule per day?
We recommend 1-3 posts per day for TikTok and 1-2 posts per day for Instagram to maintain quality and avoid overwhelming your audience.

### Can I customize the content templates?
Yes, you can add custom templates by modifying the content creation modules in the source code.

### Does the system require constant internet connection?
Yes, the system needs internet access to analyze trends, generate content, and post to social media platforms.

### How can I add more social media platforms?
The system is designed to be extensible. You can add new platforms by creating platform-specific creator classes and integrating them into the main system.

### Is my social media account information secure?
Yes, all credentials are stored locally in the .env file and are not transmitted except when making API calls to the respective platforms.
