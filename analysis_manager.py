import os
import logging
from .tiktok_analyzer import TikTokAnalyzer
from .instagram_analyzer import InstagramAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("content_analysis.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("content_analysis.manager")

class ContentAnalysisManager:
    """
    Manager class for coordinating content analysis across multiple platforms.
    """
    def __init__(self, niche, data_dir):
        """
        Initialize the content analysis manager.
        
        Args:
            niche (str): The content niche to analyze (e.g., weddings, fitness, travel)
            data_dir (str): Directory to store analysis results
        """
        self.niche = niche
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.join(data_dir, niche), exist_ok=True)
        
        # Initialize platform-specific analyzers
        self.tiktok_analyzer = TikTokAnalyzer(niche, data_dir)
        self.instagram_analyzer = InstagramAnalyzer(niche, data_dir)
        
        # Store combined analysis results
        self.combined_results = {}
        
        logger.info(f"Initialized ContentAnalysisManager for niche: {niche}")
    
    def analyze_all_platforms(self, limit=20):
        """
        Analyze trending content across all supported platforms.
        
        Args:
            limit (int): Maximum number of trending posts to analyze per platform
        
        Returns:
            dict: Combined analysis results
        """
        logger.info(f"Starting content analysis across all platforms for niche: {self.niche}")
        
        # Analyze TikTok trends
        tiktok_results = self.tiktok_analyzer.analyze_trends(limit)
        tiktok_file = self.tiktok_analyzer.save_trends_data()
        logger.info(f"TikTok analysis complete, saved to {tiktok_file}")
        
        # Analyze Instagram trends
        instagram_results = self.instagram_analyzer.analyze_trends(limit)
        instagram_file = self.instagram_analyzer.save_trends_data()
        logger.info(f"Instagram analysis complete, saved to {instagram_file}")
        
        # Combine results
        self.combined_results = self._combine_platform_results(tiktok_results, instagram_results)
        
        logger.info("Content analysis complete for all platforms")
        return self.combined_results
    
    def _combine_platform_results(self, tiktok_results, instagram_results):
        """
        Combine analysis results from multiple platforms.
        
        Args:
            tiktok_results (dict): TikTok analysis results
            instagram_results (dict): Instagram analysis results
        
        Returns:
            dict: Combined analysis results
        """
        # Create combined structure
        combined = {
            'niche': self.niche,
            'platforms': {
                'tiktok': tiktok_results,
                'instagram': instagram_results
            },
            'cross_platform_insights': {}
        }
        
        # Generate cross-platform insights
        combined['cross_platform_insights'] = self._generate_cross_platform_insights(tiktok_results, instagram_results)
        
        return combined
    
    def _generate_cross_platform_insights(self, tiktok_results, instagram_results):
        """
        Generate insights by comparing trends across platforms.
        
        Args:
            tiktok_results (dict): TikTok analysis results
            instagram_results (dict): Instagram analysis results
        
        Returns:
            dict: Cross-platform insights
        """
        insights = {
            'common_themes': self._find_common_themes(tiktok_results, instagram_results),
            'platform_specific_themes': self._find_platform_specific_themes(tiktok_results, instagram_results),
            'content_type_comparison': self._compare_content_types(tiktok_results, instagram_results),
            'hashtag_comparison': self._compare_hashtags(tiktok_results, instagram_results),
            'recommendations': self._generate_recommendations(tiktok_results, instagram_results)
        }
        
        return insights
    
    def _find_common_themes(self, tiktok_results, instagram_results):
        """
        Find themes that are common across both platforms.
        
        Returns:
            list: Common themes
        """
        tiktok_themes = set(tiktok_results.get('themes', {}).keys())
        instagram_themes = set(instagram_results.get('themes', {}).keys())
        
        common_themes = tiktok_themes.intersection(instagram_themes)
        return list(common_themes)
    
    def _find_platform_specific_themes(self, tiktok_results, instagram_results):
        """
        Find themes that are specific to each platform.
        
        Returns:
            dict: Platform-specific themes
        """
        tiktok_themes = set(tiktok_results.get('themes', {}).keys())
        instagram_themes = set(instagram_results.get('themes', {}).keys())
        
        tiktok_specific = tiktok_themes - instagram_themes
        instagram_specific = instagram_themes - tiktok_themes
        
        return {
            'tiktok': list(tiktok_specific),
            'instagram': list(instagram_specific)
        }
    
    def _compare_content_types(self, tiktok_results, instagram_results):
        """
        Compare popular content types across platforms.
        
        Returns:
            dict: Content type comparison
        """
        return {
            'tiktok': tiktok_results.get('content_types', {}),
            'instagram': instagram_results.get('content_types', {})
        }
    
    def _compare_hashtags(self, tiktok_results, instagram_results):
        """
        Compare popular hashtags across platforms.
        
        Returns:
            dict: Hashtag comparison
        """
        tiktok_hashtags = tiktok_results.get('trending_hashtags', [])
        instagram_hashtags = instagram_results.get('trending_hashtags', [])
        
        # Find common hashtags
        common_hashtags = set(tiktok_hashtags).intersection(set(instagram_hashtags))
        
        return {
            'tiktok_specific': [tag for tag in tiktok_hashtags if tag not in common_hashtags],
            'instagram_specific': [tag for tag in instagram_hashtags if tag not in common_hashtags],
            'common': list(common_hashtags)
        }
    
    def _generate_recommendations(self, tiktok_results, instagram_results):
        """
        Generate content recommendations based on cross-platform analysis.
        
        Returns:
            dict: Content recommendations
        """
        # This is a simplified recommendation engine
        # In a production system, this would be more sophisticated
        
        recommendations = {
            'tiktok': {
                'content_types': list(tiktok_results.get('content_types', {}).keys())[:3],
                'themes': list(tiktok_results.get('themes', {}).keys())[:3],
                'hashtags': tiktok_results.get('trending_hashtags', [])[:5]
            },
            'instagram': {
                'content_types': list(instagram_results.get('content_types', {}).keys())[:3],
                'themes': list(instagram_results.get('themes', {}).keys())[:3],
                'hashtags': instagram_results.get('trending_hashtags', [])[:5]
            }
        }
        
        return recommendations
    
    def save_combined_results(self):
        """
        Save the combined analysis results to a JSON file.
        
        Returns:
            str: Path to the saved file
        """
        import json
        from datetime import datetime
        
        if not self.combined_results:
            logger.error("No combined results available to save")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, self.niche, f"combined_analysis_{timestamp}.json")
        
        with open(filename, 'w') as f:
            json.dump(self.combined_results, f, indent=4)
        
        logger.info(f"Saved combined analysis results to {filename}")
        return filename
