import os
import logging
import json
import time
import datetime
import schedule
import threading
import queue
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduling.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("scheduling.scheduler")

class PostScheduler:
    """
    Class for scheduling and managing social media posts.
    """
    def __init__(self, data_dir):
        """
        Initialize the post scheduler.
        
        Args:
            data_dir (str): Directory to store scheduling data
        """
        self.data_dir = data_dir
        self.schedule_file = os.path.join(data_dir, "schedule.json")
        self.scheduled_posts = self._load_schedule()
        self.post_queue = queue.Queue()
        self.running = False
        self.scheduler_thread = None
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info(f"Initialized PostScheduler with data directory: {data_dir}")
    
    def schedule_post(self, platform, content_path, caption, hashtags, post_time=None):
        """
        Schedule a post for publishing.
        
        Args:
            platform (str): Social media platform (e.g., tiktok, instagram)
            content_path (str or list): Path(s) to content file(s)
            caption (str): Post caption
            hashtags (list): Post hashtags
            post_time (datetime, optional): Time to post, defaults to optimal time if None
            
        Returns:
            str: Post ID
        """
        # Generate post ID
        post_id = f"post_{int(time.time())}_{platform}"
        
        # Determine post time if not provided
        if post_time is None:
            post_time = self._get_optimal_post_time(platform)
        
        # Format post time
        post_time_str = post_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create post data
        post_data = {
            "id": post_id,
            "platform": platform,
            "content_path": content_path,
            "caption": caption,
            "hashtags": hashtags,
            "scheduled_time": post_time_str,
            "status": "scheduled",
            "attempts": 0,
            "posted_time": None,
            "error": None
        }
        
        # Add to scheduled posts
        self.scheduled_posts[post_id] = post_data
        
        # Save schedule
        self._save_schedule()
        
        # Schedule the post
        schedule_time = post_time.strftime("%H:%M")
        schedule_day = post_time.strftime("%A").lower()
        
        # Schedule for specific day and time
        getattr(schedule.every(), schedule_day).at(schedule_time).do(
            self._queue_post, post_id=post_id
        ).tag(post_id)
        
        logger.info(f"Scheduled {platform} post {post_id} for {post_time_str}")
        return post_id
    
    def schedule_multiple_posts(self, platform, posts_per_day, content_paths, captions, hashtags_list):
        """
        Schedule multiple posts across multiple days.
        
        Args:
            platform (str): Social media platform
            posts_per_day (int): Number of posts per day
            content_paths (list): List of content paths
            captions (list): List of captions
            hashtags_list (list): List of hashtag lists
            
        Returns:
            list: List of post IDs
        """
        if len(content_paths) != len(captions) or len(captions) != len(hashtags_list):
            raise ValueError("Content paths, captions, and hashtags lists must be the same length")
        
        post_ids = []
        
        # Calculate how many days we need
        total_posts = len(content_paths)
        days_needed = (total_posts + posts_per_day - 1) // posts_per_day  # Ceiling division
        
        # Get optimal posting times for the platform
        optimal_times = self._get_platform_optimal_times(platform, posts_per_day)
        
        # Schedule posts across days
        current_date = datetime.datetime.now()
        post_index = 0
        
        for day in range(days_needed):
            # Move to next day (skip today for the first iteration)
            if day > 0:
                current_date += datetime.timedelta(days=1)
            
            # Schedule posts for this day
            for time_slot in range(min(posts_per_day, total_posts - post_index)):
                # Get optimal time for this slot
                hour, minute = optimal_times[time_slot]
                post_time = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Schedule the post
                post_id = self.schedule_post(
                    platform=platform,
                    content_path=content_paths[post_index],
                    caption=captions[post_index],
                    hashtags=hashtags_list[post_index],
                    post_time=post_time
                )
                
                post_ids.append(post_id)
                post_index += 1
                
                # Break if we've scheduled all posts
                if post_index >= total_posts:
                    break
        
        logger.info(f"Scheduled {len(post_ids)} posts for {platform} across {days_needed} days")
        return post_ids
    
    def cancel_post(self, post_id):
        """
        Cancel a scheduled post.
        
        Args:
            post_id (str): ID of the post to cancel
            
        Returns:
            bool: True if successful, False otherwise
        """
        if post_id not in self.scheduled_posts:
            logger.warning(f"Post {post_id} not found in scheduled posts")
            return False
        
        # Remove from schedule
        schedule.clear(post_id)
        
        # Update status
        self.scheduled_posts[post_id]["status"] = "cancelled"
        
        # Save schedule
        self._save_schedule()
        
        logger.info(f"Cancelled post {post_id}")
        return True
    
    def reschedule_post(self, post_id, new_post_time):
        """
        Reschedule a post to a new time.
        
        Args:
            post_id (str): ID of the post to reschedule
            new_post_time (datetime): New time to post
            
        Returns:
            bool: True if successful, False otherwise
        """
        if post_id not in self.scheduled_posts:
            logger.warning(f"Post {post_id} not found in scheduled posts")
            return False
        
        # Remove from schedule
        schedule.clear(post_id)
        
        # Update post time
        post_time_str = new_post_time.strftime("%Y-%m-%d %H:%M:%S")
        self.scheduled_posts[post_id]["scheduled_time"] = post_time_str
        self.scheduled_posts[post_id]["status"] = "scheduled"
        
        # Save schedule
        self._save_schedule()
        
        # Reschedule the post
        schedule_time = new_post_time.strftime("%H:%M")
        schedule_day = new_post_time.strftime("%A").lower()
        
        # Schedule for specific day and time
        getattr(schedule.every(), schedule_day).at(schedule_time).do(
            self._queue_post, post_id=post_id
        ).tag(post_id)
        
        logger.info(f"Rescheduled post {post_id} for {post_time_str}")
        return True
    
    def get_scheduled_posts(self, platform=None, status=None):
        """
        Get scheduled posts, optionally filtered by platform and status.
        
        Args:
            platform (str, optional): Filter by platform
            status (str, optional): Filter by status
            
        Returns:
            dict: Filtered scheduled posts
        """
        filtered_posts = {}
        
        for post_id, post_data in self.scheduled_posts.items():
            # Apply platform filter
            if platform and post_data["platform"] != platform:
                continue
            
            # Apply status filter
            if status and post_data["status"] != status:
                continue
            
            filtered_posts[post_id] = post_data
        
        return filtered_posts
    
    def start_scheduler(self):
        """
        Start the scheduler in a background thread.
        
        Returns:
            bool: True if started, False if already running
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return False
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("Started scheduler")
        return True
    
    def stop_scheduler(self):
        """
        Stop the scheduler.
        
        Returns:
            bool: True if stopped, False if not running
        """
        if not self.running:
            logger.warning("Scheduler is not running")
            return False
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            self.scheduler_thread = None
        
        logger.info("Stopped scheduler")
        return True
    
    def _scheduler_loop(self):
        """
        Main scheduler loop that runs in a background thread.
        """
        logger.info("Scheduler loop started")
        
        while self.running:
            # Run pending scheduled tasks
            schedule.run_pending()
            
            # Process any posts in the queue
            try:
                while not self.post_queue.empty():
                    post_id = self.post_queue.get_nowait()
                    self._process_post(post_id)
                    self.post_queue.task_done()
            except queue.Empty:
                pass
            
            # Sleep for a short time
            time.sleep(1)
        
        logger.info("Scheduler loop stopped")
    
    def _queue_post(self, post_id):
        """
        Queue a post for processing.
        
        Args:
            post_id (str): ID of the post to queue
        """
        logger.info(f"Queueing post {post_id} for processing")
        self.post_queue.put(post_id)
    
    def _process_post(self, post_id):
        """
        Process a post from the queue.
        
        Args:
            post_id (str): ID of the post to process
        """
        if post_id not in self.scheduled_posts:
            logger.warning(f"Post {post_id} not found in scheduled posts")
            return
        
        post_data = self.scheduled_posts[post_id]
        
        # Update status
        post_data["status"] = "processing"
        post_data["attempts"] += 1
        self._save_schedule()
        
        logger.info(f"Processing post {post_id} for {post_data['platform']}")
        
        try:
            # Get the appropriate poster for the platform
            if post_data["platform"].lower() == "tiktok":
                success = self._post_to_tiktok(post_data)
            elif post_data["platform"].lower() == "instagram":
                success = self._post_to_instagram(post_data)
            else:
                logger.error(f"Unsupported platform: {post_data['platform']}")
                success = False
                post_data["error"] = f"Unsupported platform: {post_data['platform']}"
            
            # Update status based on result
            if success:
                post_data["status"] = "posted"
                post_data["posted_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                post_data["error"] = None
                logger.info(f"Successfully posted {post_id} to {post_data['platform']}")
            else:
                # If we've tried too many times, mark as failed
                if post_data["attempts"] >= 3:
                    post_data["status"] = "failed"
                    logger.error(f"Post {post_id} failed after {post_data['attempts']} attempts")
                else:
                    # Reschedule for retry in 30 minutes
                    post_data["status"] = "scheduled"
                    retry_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
                    self.reschedule_post(post_id, retry_time)
                    logger.warning(f"Rescheduled post {post_id} for retry at {retry_time}")
        except Exception as e:
            logger.exception(f"Error processing post {post_id}: {str(e)}")
            post_data["status"] = "error"
            post_data["error"] = str(e)
        
        # Save updated schedule
        self._save_schedule()
    
    def _post_to_tiktok(self, post_data):
        """
        Post content to TikTok.
        
        Args:
            post_data (dict): Post data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # In a production environment, this would use the TikTok API
        # For now, we'll simulate posting
        
        logger.info(f"Simulating post to TikTok: {post_data['id']}")
        
        # Check if content exists
        content_path = post_data["content_path"]
        if isinstance(content_path, list):
            # TikTok only supports single videos
            content_path = content_path[0]
        
        if not os.path.exists(content_path):
            logger.error(f"Content file not found: {content_path}")
            post_data["error"] = f"Content file not found: {content_path}"
            return False
        
        # Format caption with hashtags
        caption_with_hashtags = post_data["caption"]
        if post_data["hashtags"]:
            caption_with_hashtags += " " + " ".join(post_data["hashtags"][:5])  # TikTok typically uses fewer hashtags
        
        # Simulate API call
        time.sleep(2)  # Simulate network delay
        
        # Simulate success (90% of the time)
        success = random.random() < 0.9
        
        if not success:
            post_data["error"] = "Simulated TikTok API error"
        
        return success
    
    def _post_to_instagram(self, post_data):
        """
        Post content to Instagram.
        
        Args:
            post_data (dict): Post data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # In a production environment, this would use the Instagram API
        # For now, we'll simulate posting
        
        logger.info(f"Simulating post to Instagram: {post_data['id']}")
        
        # Check if content exists
        content_path = post_data["content_path"]
        content_paths = content_path if isinstance(content_path, list) else [content_path]
        
        for path in content_paths:
            if not os.path.exists(path):
                logger.error(f"Content file not found: {path}")
                post_data["error"] = f"Content file not found: {path}"
                return False
        
        # Format caption with hashtags
        caption_with_hashtags = post_data["caption"]
        if post_data["hashtags"]:
            caption_with_hashtags += "\n\n" + " ".join(post_data["hashtags"])
        
        # Determine post type
        if len(content_paths) > 1:
            post_type = "carousel"
        elif content_paths[0].endswith((".mp4", ".mov")):
            post_type = "reel" if "reel" in content_paths[0] else "video"
        else:
            post_type = "image"
        
        logger.info(f"Instagram post type: {post_type}")
        
        # Simulate API call
        time.sleep(2)  # Simulate network delay
        
        # Simulate success (90% of the time)
        success = random.random() < 0.9
        
        if not success:
(Content truncated due to size limit. Use line ranges to read in chunks)