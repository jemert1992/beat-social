import logging
import random
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("caption_hashtag.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("caption_hashtag.generator")

class CaptionHashtagGenerator:
    """
    Class for generating captions and hashtags for social media posts.
    """
    def __init__(self, niche):
        """
        Initialize the caption and hashtag generator.
        
        Args:
            niche (str): The content niche (e.g., weddings, fitness, travel)
        """
        self.niche = niche
        logger.info(f"Initialized CaptionHashtagGenerator for niche: {niche}")
        
        # Load templates and hashtag databases
        self.caption_templates = self._load_caption_templates()
        self.hashtag_database = self._load_hashtag_database()
        
    def generate_caption(self, platform, content_type, theme, trending_data=None):
        """
        Generate a caption for a social media post.
        
        Args:
            platform (str): Social media platform (e.g., tiktok, instagram)
            content_type (str): Type of content (e.g., tutorial, carousel)
            theme (str): Theme of the content
            trending_data (dict, optional): Trending data to inform caption generation
            
        Returns:
            str: Generated caption
        """
        logger.info(f"Generating caption for {platform} {content_type} with theme: {theme}")
        
        # Get platform-specific templates
        platform_templates = self.caption_templates.get(platform, self.caption_templates['general'])
        
        # Get content type specific templates, or use general templates
        content_templates = platform_templates.get(content_type, platform_templates['general'])
        
        # Select a random template
        template = random.choice(content_templates)
        
        # Fill in the template
        caption = self._fill_template(template, theme)
        
        # Add call to action
        caption = self._add_call_to_action(caption, platform)
        
        # Ensure caption is within platform limits
        caption = self._trim_caption(caption, platform)
        
        logger.info(f"Generated caption: {caption[:50]}...")
        return caption
    
    def generate_hashtags(self, platform, content_type, theme, count=10, trending_data=None):
        """
        Generate hashtags for a social media post.
        
        Args:
            platform (str): Social media platform (e.g., tiktok, instagram)
            content_type (str): Type of content (e.g., tutorial, carousel)
            theme (str): Theme of the content
            count (int): Number of hashtags to generate
            trending_data (dict, optional): Trending data to inform hashtag generation
            
        Returns:
            list: Generated hashtags
        """
        logger.info(f"Generating {count} hashtags for {platform} {content_type} with theme: {theme}")
        
        # Get platform-specific hashtags
        platform_hashtags = self.hashtag_database.get(platform, self.hashtag_database['general'])
        
        # Get niche-specific hashtags
        niche_hashtags = platform_hashtags.get(self.niche, platform_hashtags['general'])
        
        # Get theme-specific hashtags
        theme_hashtags = self._get_theme_hashtags(theme, platform)
        
        # Get trending hashtags if available
        trending_hashtags = []
        if trending_data and 'trending_hashtags' in trending_data:
            trending_hashtags = trending_data['trending_hashtags'][:5]  # Use top 5 trending hashtags
        
        # Combine hashtags with priority: trending > theme > niche > general
        all_hashtags = trending_hashtags + theme_hashtags + niche_hashtags
        
        # Remove duplicates while preserving order
        unique_hashtags = []
        for tag in all_hashtags:
            if tag not in unique_hashtags:
                unique_hashtags.append(tag)
        
        # Select hashtags based on count
        selected_hashtags = unique_hashtags[:count]
        
        # Ensure we have enough hashtags
        if len(selected_hashtags) < count:
            # Add general hashtags
            general_hashtags = platform_hashtags['general']
            for tag in general_hashtags:
                if tag not in selected_hashtags and len(selected_hashtags) < count:
                    selected_hashtags.append(tag)
        
        logger.info(f"Generated hashtags: {selected_hashtags}")
        return selected_hashtags
    
    def format_caption_with_hashtags(self, caption, hashtags, platform):
        """
        Format caption with hashtags according to platform best practices.
        
        Args:
            caption (str): Generated caption
            hashtags (list): Generated hashtags
            platform (str): Social media platform
            
        Returns:
            str: Formatted caption with hashtags
        """
        if platform.lower() == 'instagram':
            # Instagram: Hashtags typically at the end, separated from caption
            formatted = f"{caption}\n\n"
            formatted += " ".join(hashtags)
        elif platform.lower() == 'tiktok':
            # TikTok: Hashtags integrated into caption or at the end
            formatted = f"{caption} "
            formatted += " ".join(hashtags[:3])  # Add a few hashtags in the caption
            if len(hashtags) > 3:
                formatted += "\n\n" + " ".join(hashtags[3:])  # Rest of hashtags at the end
        else:
            # Default format
            formatted = f"{caption}\n\n"
            formatted += " ".join(hashtags)
        
        return formatted
    
    def _load_caption_templates(self):
        """
        Load caption templates for different platforms and content types.
        
        Returns:
            dict: Caption templates
        """
        # In a production system, these would be loaded from a database or file
        templates = {
            'general': {
                'general': [
                    "Exploring the world of {theme}! What's your favorite part?",
                    "Let's talk about {theme} today! Share your thoughts below.",
                    "{Theme} inspiration for your day! How do you incorporate this into your life?",
                    "The beauty of {theme} never ceases to amaze! Do you agree?",
                    "Sharing some {theme} magic with you today!"
                ]
            },
            'tiktok': {
                'general': [
                    "Check out this {theme} content! #fyp",
                    "{Theme} vibes only! Who else loves this?",
                    "POV: You're obsessed with {theme}",
                    "When {theme} is life... Can you relate?",
                    "This {theme} hack will change your life!"
                ],
                'tutorial': [
                    "How to master {theme} in 3 easy steps!",
                    "{Theme} tutorial you didn't know you needed!",
                    "Learn this {theme} trick in seconds!",
                    "The easiest way to level up your {theme} game!",
                    "POV: I'm teaching you about {theme}"
                ],
                'tips': [
                    "5 {theme} tips that actually work!",
                    "{Theme} secrets professionals don't want you to know!",
                    "Save this {theme} tip for later!",
                    "You've been doing {theme} wrong this whole time!",
                    "Game-changing {theme} tips!"
                ],
                'showcase': [
                    "Showing off my favorite {theme} finds!",
                    "{Theme} showcase that will inspire you!",
                    "The best {theme} I've ever seen!",
                    "This {theme} deserves to go viral!",
                    "Rate this {theme} 1-10!"
                ]
            },
            'instagram': {
                'general': [
                    "Embracing the beauty of {theme} today. What inspires you?",
                    "{Theme} moments that make life beautiful. Double tap if you agree!",
                    "Finding joy in {theme} every day. How do you incorporate this into your routine?",
                    "Sharing my {theme} journey with you all. What's been your experience?",
                    "The art of {theme} is all about perspective. What's yours?"
                ],
                'single_image': [
                    "Captured this {theme} moment and had to share! What do you think?",
                    "Today's {theme} inspiration. Saving this for later!",
                    "When {theme} speaks to your soul. Can you feel it?",
                    "This {theme} view never gets old. Where's your favorite spot?",
                    "Finding beauty in {theme} everywhere I look."
                ],
                'carousel': [
                    "Swipe to see my top {theme} picks! Which one is your favorite?",
                    "A collection of {theme} inspirations. Save this post for later!",
                    "Couldn't choose just one {theme} photo, so here's a series!",
                    "My {theme} journey in pictures. Swipe to see the transformation!",
                    "The many faces of {theme}. Which slide resonates with you most?"
                ],
                'reel': [
                    "Quick {theme} inspiration for your feed! Save for later!",
                    "When {theme} looks this good, you have to make a reel!",
                    "POV: You're obsessed with {theme} too!",
                    "This {theme} hack changed everything! Try it yourself!",
                    "The {theme} content you've been waiting for!"
                ]
            }
        }
        
        return templates
    
    def _load_hashtag_database(self):
        """
        Load hashtag database for different platforms and niches.
        
        Returns:
            dict: Hashtag database
        """
        # In a production system, these would be loaded from a database or file
        # and would be much more extensive
        database = {
            'general': {
                'general': ["#trending", "#viral", "#content", "#share", "#follow", "#like", "#comment", "#explore"]
            },
            'tiktok': {
                'general': ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending", "#tiktok", "#tiktokviral"],
                'weddings': ["#wedding", "#weddingday", "#bride", "#weddingplanning", "#weddingdress", "#weddingphotography", "#weddinginspo", "#bridetobe", "#weddingideas", "#weddinginspiration"],
                'fitness': ["#fitness", "#workout", "#gym", "#fitnessmotivation", "#fit", "#training", "#health", "#motivation", "#healthy", "#lifestyle", "#exercise", "#fitfam"],
                'travel': ["#travel", "#travelphotography", "#nature", "#photography", "#travelgram", "#adventure", "#wanderlust", "#explore", "#traveling", "#vacation", "#trip", "#instatravel"],
                'food': ["#food", "#foodie", "#foodporn", "#instafood", "#foodphotography", "#delicious", "#yummy", "#homemade", "#cooking", "#foodlover", "#foodblogger", "#tasty"],
                'beauty': ["#beauty", "#makeup", "#skincare", "#beautiful", "#fashion", "#style", "#hair", "#makeupartist", "#selfcare", "#natural", "#glam", "#mua"],
                'fashion': ["#fashion", "#style", "#ootd", "#fashionblogger", "#model", "#photography", "#instagood", "#beautiful", "#photooftheday", "#shopping", "#fashionstyle", "#fashionista"],
                'tech': ["#tech", "#technology", "#innovation", "#gadgets", "#smartphone", "#apple", "#iphone", "#android", "#samsung", "#computer", "#techie", "#geek"],
                'gaming': ["#gaming", "#gamer", "#videogames", "#ps5", "#xbox", "#pc", "#twitch", "#streamer", "#game", "#esports", "#gamingcommunity", "#gaminglife"],
                'education': ["#education", "#learning", "#student", "#study", "#school", "#college", "#knowledge", "#teacher", "#university", "#learn", "#students", "#teaching"],
                'business': ["#business", "#entrepreneur", "#success", "#motivation", "#entrepreneurship", "#marketing", "#smallbusiness", "#money", "#inspiration", "#startup", "#mindset", "#goals"]
            },
            'instagram': {
                'general': ["#instagood", "#photooftheday", "#love", "#instagram", "#beautiful", "#picoftheday", "#happy", "#follow", "#instadaily", "#style", "#reels", "#explorepage"],
                'weddings': ["#wedding", "#weddingday", "#bride", "#weddingphotography", "#weddingdress", "#weddingplanner", "#weddinginspiration", "#weddingphotographer", "#bridal", "#bridetobe", "#weddinginspo", "#weddings"],
                'fitness': ["#fitness", "#workout", "#gym", "#fitnessmotivation", "#fit", "#training", "#health", "#motivation", "#healthy", "#lifestyle", "#bodybuilding", "#fitfam", "#exercise"],
                'travel': ["#travel", "#travelphotography", "#nature", "#photography", "#travelgram", "#adventure", "#wanderlust", "#explore", "#traveling", "#vacation", "#trip", "#instatravel", "#naturephotography"],
                'food': ["#food", "#foodie", "#foodporn", "#instafood", "#foodphotography", "#delicious", "#yummy", "#homemade", "#cooking", "#foodlover", "#foodblogger", "#tasty", "#healthyfood"],
                'beauty': ["#beauty", "#makeup", "#skincare", "#beautiful", "#fashion", "#style", "#hair", "#makeupartist", "#selfcare", "#natural", "#glam", "#mua", "#makeuptutorial"],
                'fashion': ["#fashion", "#style", "#ootd", "#fashionblogger", "#model", "#photography", "#instagood", "#beautiful", "#photooftheday", "#shopping", "#fashionstyle", "#fashionista", "#instafashion"],
                'tech': ["#tech", "#technology", "#innovation", "#gadgets", "#smartphone", "#apple", "#iphone", "#android", "#samsung", "#computer", "#techie", "#geek", "#technews"],
                'gaming': ["#gaming", "#gamer", "#videogames", "#ps5", "#xbox", "#pc", "#twitch", "#streamer", "#game", "#esports", "#gamingcommunity", "#gaminglife", "#gamerlife"],
                'education': ["#education", "#learning", "#student", "#study", "#school", "#college", "#knowledge", "#teacher", "#university", "#learn", "#students", "#teaching", "#studygram"],
                'business': ["#business", "#entrepreneur", "#success", "#motivation", "#entrepreneurship", "#marketing", "#smallbusiness", "#money", "#inspiration", "#startup", "#mindset", "#goals", "#entrepreneurlife"]
            }
        }
        
        return database
    
    def _fill_template(self, template, theme):
        """
        Fill in a caption template with the theme.
        
        Args:
            template (str): Caption template
            theme (str): Theme of the content
            
        Returns:
            str: Filled caption
        """
        # Replace {theme} with lowercase theme
        caption = template.replace("{theme}", theme.lower())
        
        # Replace {Theme} with capitalized theme
        caption = caption.replace("{Theme}", theme.capitalize())
        
        return caption
    
    def _add_call_to_action(self, caption, platform):
        """
        Add a call to action to the caption.
        
        Args:
            caption (str): Caption
            platform (str): Social media platform
            
        Returns:
            str: Caption with call to action
        """
        # Check if caption already has a call to action
        cta_patterns = [
            r'\bfollow\b',
            r'\blike\b',
            r'\bcomment\b',
            r'\bshare\b',
            r'\bsave\b',
            r'\btag\b',
            r'\bswipe\b',
            r'\?$'  #
(Content truncated due to size limit. Use line ranges to read in chunks)