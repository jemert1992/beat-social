import os
import logging
import json
import time
from datetime import datetime
import random

# Import modules from other components
from src.content_analysis.analysis_manager import ContentAnalysisManager
from src.content_creation.tiktok_creator import TikTokContentCreator
from src.content_creation.instagram_creator import InstagramContentCreator
from src.caption_hashtag.generator import CaptionHashtagGenerator
from src.scheduling.scheduler import PostScheduler
from src.performance_tracking.tracker import PerformanceTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("social_media_automation.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("social_media_automation.system")

class SocialMediaAutomationSystem:
    """
    Main class that integrates all components of the social media automation system.
    """
    def __init__(self, base_dir):
        """
        Initialize the social media automation system.
        
        Args:
            base_dir (str): Base directory for the system
        """
        self.base_dir = base_dir
        
        # Create directory structure
        self.data_dir = os.path.join(base_dir, "data")
        self.content_dir = os.path.join(base_dir, "content")
        self.config_dir = os.path.join(base_dir, "config")
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.content_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Configuration file
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config = self._load_config()
        
        # Initialize components
        self._init_components()
        
        logger.info(f"Initialized SocialMediaAutomationSystem in {base_dir}")
    
    def _init_components(self):
        """
        Initialize all system components.
        """
        # Get current niche from config
        niche = self.config.get("niche", "general")
        
        # Initialize content analysis
        self.content_analyzer = ContentAnalysisManager(niche, self.data_dir)
        
        # Initialize content creators
        self.tiktok_creator = TikTokContentCreator(niche, self.content_dir)
        self.instagram_creator = InstagramContentCreator(niche, self.content_dir)
        
        # Initialize caption and hashtag generator
        self.caption_generator = CaptionHashtagGenerator(niche)
        
        # Initialize scheduler
        self.scheduler = PostScheduler(self.data_dir)
        
        # Initialize performance tracker
        self.performance_tracker = PerformanceTracker(self.data_dir)
        
        logger.info(f"Initialized all components for niche: {niche}")
    
    def configure(self, niche, tiktok_frequency=1, instagram_frequency=1, content_preferences=None):
        """
        Configure the system with user preferences.
        
        Args:
            niche (str): Content niche (e.g., weddings, fitness, travel)
            tiktok_frequency (int): Number of TikTok posts per day
            instagram_frequency (int): Number of Instagram posts per day
            content_preferences (dict, optional): Content preferences
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Configuring system for niche: {niche}")
        
        # Update configuration
        self.config["niche"] = niche
        self.config["tiktok_frequency"] = tiktok_frequency
        self.config["instagram_frequency"] = instagram_frequency
        self.config["content_preferences"] = content_preferences or {}
        self.config["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save configuration
        self._save_config()
        
        # Reinitialize components with new niche
        self._init_components()
        
        logger.info(f"System configured for niche: {niche}")
        return True
    
    def generate_content_plan(self, days=7):
        """
        Generate a content plan for the specified number of days.
        
        Args:
            days (int): Number of days to plan for
            
        Returns:
            dict: Content plan
        """
        logger.info(f"Generating content plan for {days} days")
        
        niche = self.config["niche"]
        tiktok_frequency = self.config["tiktok_frequency"]
        instagram_frequency = self.config["instagram_frequency"]
        
        # Analyze trends
        trend_analysis = self.content_analyzer.analyze_all_platforms()
        
        # Calculate total posts needed
        total_tiktok_posts = tiktok_frequency * days
        total_instagram_posts = instagram_frequency * days
        
        # Get recommendations from trend analysis
        tiktok_recommendations = trend_analysis["cross_platform_insights"]["recommendations"]["tiktok"]
        instagram_recommendations = trend_analysis["cross_platform_insights"]["recommendations"]["instagram"]
        
        # Generate content plan
        content_plan = {
            "niche": niche,
            "period": f"{datetime.now().strftime('%Y-%m-%d')} to {(datetime.now() + datetime.timedelta(days=days)).strftime('%Y-%m-%d')}",
            "tiktok": {
                "posts_per_day": tiktok_frequency,
                "total_posts": total_tiktok_posts,
                "content_types": tiktok_recommendations["content_types"],
                "themes": tiktok_recommendations["themes"],
                "hashtags": tiktok_recommendations["hashtags"],
                "posts": []
            },
            "instagram": {
                "posts_per_day": instagram_frequency,
                "total_posts": total_instagram_posts,
                "content_types": instagram_recommendations["content_types"],
                "themes": instagram_recommendations["themes"],
                "hashtags": instagram_recommendations["hashtags"],
                "posts": []
            }
        }
        
        # Generate TikTok post plans
        for i in range(total_tiktok_posts):
            content_type = random.choice(tiktok_recommendations["content_types"])
            theme = random.choice(tiktok_recommendations["themes"])
            
            post_plan = {
                "id": f"tiktok_{i+1}",
                "content_type": content_type,
                "theme": theme,
                "day": (i // tiktok_frequency) + 1,
                "status": "planned"
            }
            
            content_plan["tiktok"]["posts"].append(post_plan)
        
        # Generate Instagram post plans
        for i in range(total_instagram_posts):
            content_type = random.choice(instagram_recommendations["content_types"])
            theme = random.choice(instagram_recommendations["themes"])
            
            post_plan = {
                "id": f"instagram_{i+1}",
                "content_type": content_type,
                "theme": theme,
                "day": (i // instagram_frequency) + 1,
                "status": "planned"
            }
            
            content_plan["instagram"]["posts"].append(post_plan)
        
        # Save content plan
        plan_file = os.path.join(self.data_dir, f"content_plan_{datetime.now().strftime('%Y%m%d')}.json")
        with open(plan_file, 'w') as f:
            json.dump(content_plan, f, indent=4)
        
        logger.info(f"Generated content plan with {total_tiktok_posts} TikTok posts and {total_instagram_posts} Instagram posts")
        return content_plan
    
    def execute_content_plan(self, content_plan=None):
        """
        Execute a content plan by generating and scheduling posts.
        
        Args:
            content_plan (dict, optional): Content plan to execute, or generate a new one if None
            
        Returns:
            dict: Execution results
        """
        if content_plan is None:
            content_plan = self.generate_content_plan()
        
        logger.info(f"Executing content plan for niche: {content_plan['niche']}")
        
        # Start the scheduler
        self.scheduler.start_scheduler()
        
        # Track execution results
        execution_results = {
            "tiktok": {
                "generated": [],
                "scheduled": []
            },
            "instagram": {
                "generated": [],
                "scheduled": []
            }
        }
        
        # Execute TikTok posts
        for post_plan in content_plan["tiktok"]["posts"]:
            try:
                # Generate content
                content_path = self.tiktok_creator.create_content(
                    post_plan["content_type"],
                    post_plan["theme"]
                )
                
                # Generate caption and hashtags
                caption = self.caption_generator.generate_caption(
                    "tiktok",
                    post_plan["content_type"],
                    post_plan["theme"]
                )
                
                hashtags = self.caption_generator.generate_hashtags(
                    "tiktok",
                    post_plan["content_type"],
                    post_plan["theme"]
                )
                
                # Schedule post
                post_id = self.scheduler.schedule_post(
                    "tiktok",
                    content_path,
                    caption,
                    hashtags
                )
                
                # Track results
                execution_results["tiktok"]["generated"].append({
                    "plan_id": post_plan["id"],
                    "content_path": content_path,
                    "caption": caption,
                    "hashtags": hashtags
                })
                
                execution_results["tiktok"]["scheduled"].append({
                    "plan_id": post_plan["id"],
                    "post_id": post_id
                })
                
                logger.info(f"Generated and scheduled TikTok post: {post_id}")
                
                # Simulate post metrics for demonstration
                self._simulate_post_metrics("tiktok", post_id, post_plan["content_type"], post_plan["theme"])
                
            except Exception as e:
                logger.error(f"Error executing TikTok post plan {post_plan['id']}: {str(e)}")
        
        # Execute Instagram posts
        for post_plan in content_plan["instagram"]["posts"]:
            try:
                # Generate content
                content_path = self.instagram_creator.create_content(
                    post_plan["content_type"],
                    post_plan["theme"]
                )
                
                # Generate caption and hashtags
                caption = self.caption_generator.generate_caption(
                    "instagram",
                    post_plan["content_type"],
                    post_plan["theme"]
                )
                
                hashtags = self.caption_generator.generate_hashtags(
                    "instagram",
                    post_plan["content_type"],
                    post_plan["theme"]
                )
                
                # Schedule post
                post_id = self.scheduler.schedule_post(
                    "instagram",
                    content_path,
                    caption,
                    hashtags
                )
                
                # Track results
                execution_results["instagram"]["generated"].append({
                    "plan_id": post_plan["id"],
                    "content_path": content_path,
                    "caption": caption,
                    "hashtags": hashtags
                })
                
                execution_results["instagram"]["scheduled"].append({
                    "plan_id": post_plan["id"],
                    "post_id": post_id
                })
                
                logger.info(f"Generated and scheduled Instagram post: {post_id}")
                
                # Simulate post metrics for demonstration
                self._simulate_post_metrics("instagram", post_id, post_plan["content_type"], post_plan["theme"])
                
            except Exception as e:
                logger.error(f"Error executing Instagram post plan {post_plan['id']}: {str(e)}")
        
        # Save execution results
        results_file = os.path.join(self.data_dir, f"execution_results_{datetime.now().strftime('%Y%m%d')}.json")
        with open(results_file, 'w') as f:
            json.dump(execution_results, f, indent=4)
        
        logger.info(f"Completed content plan execution")
        return execution_results
    
    def generate_weekly_report(self):
        """
        Generate a weekly performance report.
        
        Returns:
            str: Path to the generated report
        """
        logger.info(f"Generating weekly report for niche: {self.config['niche']}")
        
        # Generate report using performance tracker
        report_path = self.performance_tracker.generate_weekly_report(
            self.config["niche"],
            platforms=["tiktok", "instagram"],
            output_format="html"
        )
        
        # Generate performance charts
        chart_paths = self.performance_tracker.generate_performance_charts()
        
        logger.info(f"Generated weekly report: {report_path}")
        return report_path
    
    def _simulate_post_metrics(self, platform, post_id, content_type, theme):
        """
        Simulate post metrics for demonstration purposes.
        
        Args:
            platform (str): Social media platform
            post_id (str): Post ID
            content_type (str): Content type
            theme (str): Content theme
        """
        # Generate random metrics based on platform
        if platform.lower() == "tiktok":
            metrics = {
                "views": random.randint(1000, 100000),
                "likes": random.randint(100, 10000),
                "comments": random.randint(10, 1000),
                "shares": random.randint(5, 500)
            }
        else:  # Instagram
            metrics = {
                "likes": random.randint(50, 5000),
                "comments": random.randint(5, 500),
                "saves": random.randint(10, 1000),
                "followers": random.randint(1000, 10000)
            }
        
        # Track metrics
        self.performance_tracker.track_post(
            post_id,
            platform,
            content_type,
            theme,
            metrics
        )
        
        logger.info(f"Simulated metrics for {platform} post: {post_id}")
    
    def _load_config(self):
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration
        """
        if not os.path.exists(self.config_file):
            # Default configuration
            default_config = {
                "niche": "general",
                "tiktok_frequency": 1,
                "instagram_frequency": 1,
                "content_preferences": {},
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save default configuration
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return {
                "niche": "general",
                "tiktok_frequency": 1,
                "instagram_frequency": 1,
      
(Content truncated due to size limit. Use line ranges to read in chunks)