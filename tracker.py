import os
import logging
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("performance_tracking.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("performance_tracking.tracker")

class PerformanceTracker:
    """
    Class for tracking and analyzing social media post performance.
    """
    def __init__(self, data_dir):
        """
        Initialize the performance tracker.
        
        Args:
            data_dir (str): Directory to store performance data
        """
        self.data_dir = data_dir
        self.metrics_file = os.path.join(data_dir, "performance_metrics.json")
        self.reports_dir = os.path.join(data_dir, "reports")
        self.metrics_data = self._load_metrics()
        
        # Create directories if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        logger.info(f"Initialized PerformanceTracker with data directory: {data_dir}")
    
    def track_post(self, post_id, platform, content_type, theme, metrics):
        """
        Track performance metrics for a post.
        
        Args:
            post_id (str): ID of the post
            platform (str): Social media platform
            content_type (str): Type of content
            theme (str): Theme of the content
            metrics (dict): Performance metrics (likes, comments, shares, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if post_id in self.metrics_data:
            # Update existing metrics
            self.metrics_data[post_id]["metrics"] = metrics
            self.metrics_data[post_id]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Add new post metrics
            self.metrics_data[post_id] = {
                "post_id": post_id,
                "platform": platform,
                "content_type": content_type,
                "theme": theme,
                "metrics": metrics,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Calculate engagement rate
        self._calculate_engagement_rate(post_id)
        
        # Save metrics
        self._save_metrics()
        
        logger.info(f"Tracked metrics for post {post_id} on {platform}")
        return True
    
    def update_metrics(self, post_id, new_metrics):
        """
        Update metrics for an existing post.
        
        Args:
            post_id (str): ID of the post
            new_metrics (dict): Updated performance metrics
            
        Returns:
            bool: True if successful, False otherwise
        """
        if post_id not in self.metrics_data:
            logger.warning(f"Post {post_id} not found in metrics data")
            return False
        
        # Update metrics
        current_metrics = self.metrics_data[post_id]["metrics"]
        for key, value in new_metrics.items():
            current_metrics[key] = value
        
        self.metrics_data[post_id]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Recalculate engagement rate
        self._calculate_engagement_rate(post_id)
        
        # Save metrics
        self._save_metrics()
        
        logger.info(f"Updated metrics for post {post_id}")
        return True
    
    def get_post_metrics(self, post_id):
        """
        Get metrics for a specific post.
        
        Args:
            post_id (str): ID of the post
            
        Returns:
            dict: Post metrics or None if not found
        """
        return self.metrics_data.get(post_id)
    
    def get_all_metrics(self, platform=None, content_type=None, theme=None, date_range=None):
        """
        Get all metrics, optionally filtered.
        
        Args:
            platform (str, optional): Filter by platform
            content_type (str, optional): Filter by content type
            theme (str, optional): Filter by theme
            date_range (tuple, optional): Filter by date range (start_date, end_date)
            
        Returns:
            dict: Filtered metrics data
        """
        filtered_data = {}
        
        for post_id, post_data in self.metrics_data.items():
            # Apply platform filter
            if platform and post_data["platform"] != platform:
                continue
            
            # Apply content type filter
            if content_type and post_data["content_type"] != content_type:
                continue
            
            # Apply theme filter
            if theme and post_data["theme"] != theme:
                continue
            
            # Apply date range filter
            if date_range:
                start_date, end_date = date_range
                post_date = datetime.strptime(post_data["created_at"], "%Y-%m-%d %H:%M:%S")
                
                if post_date < start_date or post_date > end_date:
                    continue
            
            filtered_data[post_id] = post_data
        
        return filtered_data
    
    def generate_weekly_report(self, niche, platforms=None, output_format="pdf"):
        """
        Generate a weekly performance report.
        
        Args:
            niche (str): Content niche
            platforms (list, optional): List of platforms to include
            output_format (str): Output format (pdf, html, json)
            
        Returns:
            str: Path to the generated report
        """
        logger.info(f"Generating weekly report for niche: {niche}")
        
        # Set date range for the past week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Filter metrics for the past week
        weekly_data = self.get_all_metrics(date_range=(start_date, end_date))
        
        # Further filter by platforms if specified
        if platforms:
            weekly_data = {k: v for k, v in weekly_data.items() if v["platform"] in platforms}
        
        # If no data, return early
        if not weekly_data:
            logger.warning(f"No data available for weekly report ({niche})")
            return None
        
        # Convert to DataFrame for analysis
        df = self._metrics_to_dataframe(weekly_data)
        
        # Generate report content
        report_content = self._generate_report_content(df, niche)
        
        # Create report file
        timestamp = datetime.now().strftime("%Y%m%d")
        report_filename = f"weekly_report_{niche}_{timestamp}"
        
        if output_format == "pdf":
            report_path = os.path.join(self.reports_dir, f"{report_filename}.pdf")
            self._generate_pdf_report(report_content, report_path)
        elif output_format == "html":
            report_path = os.path.join(self.reports_dir, f"{report_filename}.html")
            self._generate_html_report(report_content, report_path)
        else:  # Default to JSON
            report_path = os.path.join(self.reports_dir, f"{report_filename}.json")
            with open(report_path, 'w') as f:
                json.dump(report_content, f, indent=4)
        
        logger.info(f"Generated weekly report: {report_path}")
        return report_path
    
    def analyze_content_performance(self, platform=None, period=30):
        """
        Analyze content performance to identify trends.
        
        Args:
            platform (str, optional): Filter by platform
            period (int): Number of days to analyze
            
        Returns:
            dict: Performance analysis results
        """
        # Set date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        
        # Get metrics for the period
        period_data = self.get_all_metrics(platform=platform, date_range=(start_date, end_date))
        
        # If no data, return early
        if not period_data:
            logger.warning(f"No data available for performance analysis")
            return {
                "status": "no_data",
                "message": f"No data available for the past {period} days"
            }
        
        # Convert to DataFrame
        df = self._metrics_to_dataframe(period_data)
        
        # Analyze by content type
        content_type_performance = df.groupby('content_type')['engagement_rate'].mean().to_dict()
        best_content_type = max(content_type_performance.items(), key=lambda x: x[1])
        
        # Analyze by theme
        theme_performance = df.groupby('theme')['engagement_rate'].mean().to_dict()
        best_theme = max(theme_performance.items(), key=lambda x: x[1])
        
        # Analyze by platform (if not filtered)
        platform_performance = {}
        best_platform = None
        if not platform:
            platform_performance = df.groupby('platform')['engagement_rate'].mean().to_dict()
            best_platform = max(platform_performance.items(), key=lambda x: x[1])
        
        # Analyze time trends
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        time_trends = df.groupby('date')['engagement_rate'].mean().to_dict()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            content_type_performance,
            theme_performance,
            platform_performance
        )
        
        # Compile analysis results
        analysis = {
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "total_posts": len(period_data),
            "average_engagement_rate": df['engagement_rate'].mean(),
            "content_type_performance": content_type_performance,
            "best_content_type": {
                "type": best_content_type[0],
                "engagement_rate": best_content_type[1]
            },
            "theme_performance": theme_performance,
            "best_theme": {
                "theme": best_theme[0],
                "engagement_rate": best_theme[1]
            },
            "time_trends": time_trends,
            "recommendations": recommendations
        }
        
        # Add platform analysis if available
        if best_platform:
            analysis["platform_performance"] = platform_performance
            analysis["best_platform"] = {
                "platform": best_platform[0],
                "engagement_rate": best_platform[1]
            }
        
        logger.info(f"Completed performance analysis for the past {period} days")
        return analysis
    
    def generate_performance_charts(self, platform=None, period=30, output_dir=None):
        """
        Generate performance charts for visualization.
        
        Args:
            platform (str, optional): Filter by platform
            period (int): Number of days to analyze
            output_dir (str, optional): Directory to save charts
            
        Returns:
            list: Paths to generated chart images
        """
        if output_dir is None:
            output_dir = os.path.join(self.reports_dir, "charts")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Set date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        
        # Get metrics for the period
        period_data = self.get_all_metrics(platform=platform, date_range=(start_date, end_date))
        
        # If no data, return early
        if not period_data:
            logger.warning(f"No data available for performance charts")
            return []
        
        # Convert to DataFrame
        df = self._metrics_to_dataframe(period_data)
        
        # Generate charts
        chart_paths = []
        
        # 1. Engagement by content type
        content_type_chart = os.path.join(output_dir, f"engagement_by_content_type_{datetime.now().strftime('%Y%m%d')}.png")
        self._create_bar_chart(
            df, 'content_type', 'engagement_rate', 
            'Average Engagement Rate by Content Type',
            content_type_chart
        )
        chart_paths.append(content_type_chart)
        
        # 2. Engagement by theme
        theme_chart = os.path.join(output_dir, f"engagement_by_theme_{datetime.now().strftime('%Y%m%d')}.png")
        self._create_bar_chart(
            df, 'theme', 'engagement_rate', 
            'Average Engagement Rate by Theme',
            theme_chart
        )
        chart_paths.append(theme_chart)
        
        # 3. Engagement over time
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        time_chart = os.path.join(output_dir, f"engagement_over_time_{datetime.now().strftime('%Y%m%d')}.png")
        self._create_line_chart(
            df, 'date', 'engagement_rate', 
            'Engagement Rate Over Time',
            time_chart
        )
        chart_paths.append(time_chart)
        
        # 4. Platform comparison (if not filtered)
        if not platform and len(df['platform'].unique()) > 1:
            platform_chart = os.path.join(output_dir, f"engagement_by_platform_{datetime.now().strftime('%Y%m%d')}.png")
            self._create_bar_chart(
                df, 'platform', 'engagement_rate', 
                'Average Engagement Rate by Platform',
                platform_chart
            )
            chart_paths.append(platform_chart)
        
        logger.info(f"Generated {len(chart_paths)} performance charts")
        return chart_paths
    
    def _calculate_engagement_rate(self, post_id):
        """
        Calculate engagement rate for a post.
        
        Args:
            post_id (str): ID of the post
        """
        post_data = self.metrics_data[post_id]
        metrics = post_data["metrics"]
        platform = post_data["platform"].lower()
        
        # Different platforms have different engagement calculations
        if platform == "tiktok":
            # TikTok: (likes + comments + shares) / views * 100
            likes = metrics.get("likes", 0)
            comments = metrics.get("comments", 0)
            shares = metrics.get("shares", 0)
            views = metrics.get("views", 1)  # Avoid division by zero
            
            engagement_rate = (likes + comments + shares) / views * 100
        elif platform == "instagram":
            # Instagram: (likes + comments * 2 + saves * 3) / followers * 100
            likes = metrics.get("likes", 0)
            comments = metrics.get("comments", 0)
            saves = metrics.get("saves", 0)
            followers = metrics.get("followers", 100)  # Default to 100 if not provided
            
            engagement_rate = (likes + comments * 2 + saves * 3) / followers * 100
        else:
            # Generic calculation
            likes = metrics.get("likes", 0)
            comments = metrics.get("comments", 0)
            shares = metrics.get("shares", 0)
            views = metrics.get("views", 100)
            
            engagement_rate = (likes + comments + shares) / views * 100
        
        # Update engagement rate in metrics
        metrics["engagement_rate"] = round(engagement_rate, 2)
    
    def _metrics_to_dataframe(self, metrics_data):
        """
        Convert metrics data to a pandas DataFrame.
        
        Args:
            metrics_data (dict): Metrics data
            
        Returns:
            pandas.DataFrame: DataFrame of metrics
        """
        # Flatten the nested structure
        flattened_data = []
        
        for post_id, post_data in metrics_data.items():
            fl
(Content truncated due to size limit. Use line ranges to read in chunks)