import os
import logging
import random
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import moviepy.editor as mp
from .base_creator import ContentCreator

logger = logging.getLogger("content_creation.tiktok_creator")

class TikTokContentCreator(ContentCreator):
    """
    Class for creating content specifically for TikTok.
    """
    def __init__(self, niche, output_dir):
        """
        Initialize the TikTok content creator.
        
        Args:
            niche (str): The content niche (e.g., weddings, fitness, travel)
            output_dir (str): Directory to store created content
        """
        super().__init__(niche, output_dir)
        
        # TikTok-specific dimensions
        self.video_width = 1080
        self.video_height = 1920
        self.video_duration = 15  # seconds
        
        logger.info(f"Initialized TikTokContentCreator for niche: {niche}")
    
    def create_content(self, content_type, theme, text=None, trending_data=None):
        """
        Create TikTok content based on specified type and theme.
        
        Args:
            content_type (str): Type of content to create (e.g., tutorial, tips, showcase)
            theme (str): Theme of the content
            text (str, optional): Text to include in the content
            trending_data (dict, optional): Trending data to inform content creation
            
        Returns:
            str: Path to the created content
        """
        logger.info(f"Creating TikTok {content_type} content with theme: {theme}")
        
        if text is None:
            text = self._generate_text_for_theme(theme, content_type)
        
        if content_type in ["tutorial", "tips", "transformation"]:
            return self.create_text_based_video(text, theme)
        elif content_type in ["showcase", "review"]:
            return self.create_image_slideshow(theme, text)
        else:
            # Default to a simple image with text overlay
            return self.create_simple_image_post(theme, text)
    
    def create_text_based_video(self, text, theme):
        """
        Create a text-based video for TikTok.
        
        Args:
            text (str): Text to include in the video
            theme (str): Theme of the content
            
        Returns:
            str: Path to the created video
        """
        logger.info(f"Creating text-based video for theme: {theme}")
        
        # Get a background image related to the theme
        background = self.get_stock_image(theme)
        background = background.resize((self.video_width, self.video_height))
        
        # Add text overlay
        text_parts = self._split_text_for_video(text)
        
        # Create a temporary directory for frames
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        # Create frames with different text parts
        frames = []
        for i, part in enumerate(text_parts):
            frame = background.copy()
            frame = self.add_text_overlay(frame, part, position='center', 
                                         text_color=(255, 255, 255), 
                                         shadow_color=(0, 0, 0),
                                         font_size=48)
            frame = self.apply_branding(frame)
            
            frame_path = os.path.join(temp_dir, f"frame_{i:03d}.jpg")
            frame.save(frame_path, "JPEG", quality=95)
            frames.append(frame_path)
        
        # Create video from frames
        clip_duration = self.video_duration / len(frames)
        clips = [mp.ImageClip(frame).set_duration(clip_duration) for frame in frames]
        
        final_clip = mp.concatenate_videoclips(clips, method="compose")
        
        # Add simple fade transitions
        final_clip = final_clip.fadein(0.5).fadeout(0.5)
        
        # Save the video
        sanitized_theme = theme.replace(' ', '_').lower()
        timestamp = random.randint(10000, 99999)
        output_path = os.path.join(self.output_dir, self.niche, f"tiktok_text_{sanitized_theme}_{timestamp}.mp4")
        
        final_clip.write_videofile(output_path, codec='libx264', audio=False, fps=24)
        
        # Clean up temporary files
        for frame in frames:
            os.remove(frame)
        os.rmdir(temp_dir)
        
        logger.info(f"Created text-based video at {output_path}")
        return output_path
    
    def create_image_slideshow(self, theme, text, num_images=5):
        """
        Create an image slideshow for TikTok.
        
        Args:
            theme (str): Theme of the content
            text (str): Text to include in the slideshow
            num_images (int): Number of images in the slideshow
            
        Returns:
            str: Path to the created slideshow
        """
        logger.info(f"Creating image slideshow for theme: {theme} with {num_images} images")
        
        # Create a temporary directory for frames
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        # Get images related to the theme
        frames = []
        for i in range(num_images):
            # Get a different image for each frame
            image = self.get_stock_image(f"{theme} {i}")
            image = image.resize((self.video_width, self.video_height))
            
            # Add text overlay (different part of text for each image)
            text_parts = self._split_text_for_slideshow(text, num_images)
            current_text = text_parts[i % len(text_parts)]
            
            image = self.add_text_overlay(image, current_text, position='bottom', 
                                         text_color=(255, 255, 255), 
                                         shadow_color=(0, 0, 0),
                                         font_size=42)
            
            image = self.apply_branding(image)
            
            frame_path = os.path.join(temp_dir, f"slide_{i:03d}.jpg")
            image.save(frame_path, "JPEG", quality=95)
            frames.append(frame_path)
        
        # Create video from frames
        clip_duration = self.video_duration / len(frames)
        clips = [mp.ImageClip(frame).set_duration(clip_duration) for frame in frames]
        
        final_clip = mp.concatenate_videoclips(clips, method="compose")
        
        # Add transitions
        final_clip = final_clip.fadein(0.5).fadeout(0.5)
        
        # Save the video
        sanitized_theme = theme.replace(' ', '_').lower()
        timestamp = random.randint(10000, 99999)
        output_path = os.path.join(self.output_dir, self.niche, f"tiktok_slideshow_{sanitized_theme}_{timestamp}.mp4")
        
        final_clip.write_videofile(output_path, codec='libx264', audio=False, fps=24)
        
        # Clean up temporary files
        for frame in frames:
            os.remove(frame)
        os.rmdir(temp_dir)
        
        logger.info(f"Created image slideshow at {output_path}")
        return output_path
    
    def create_simple_image_post(self, theme, text):
        """
        Create a simple image post for TikTok.
        
        Args:
            theme (str): Theme of the content
            text (str): Text to include in the image
            
        Returns:
            str: Path to the created image
        """
        logger.info(f"Creating simple image post for theme: {theme}")
        
        # Get a background image related to the theme
        image = self.get_stock_image(theme)
        image = image.resize((self.video_width, self.video_height))
        
        # Add text overlay
        image = self.add_text_overlay(image, text, position='center', 
                                     text_color=(255, 255, 255), 
                                     shadow_color=(0, 0, 0),
                                     font_size=48)
        
        # Add branding
        image = self.apply_branding(image)
        
        # Save the image
        sanitized_theme = theme.replace(' ', '_').lower()
        return self.save_image(image, f"tiktok_{sanitized_theme}", "image")
    
    def _generate_text_for_theme(self, theme, content_type):
        """
        Generate text based on theme and content type.
        
        Args:
            theme (str): Theme of the content
            content_type (str): Type of content
            
        Returns:
            str: Generated text
        """
        # This is a simplified text generator
        # In a production system, this would be more sophisticated
        
        if content_type == "tutorial":
            return f"How to create the perfect {theme} look in 3 easy steps!"
        elif content_type == "tips":
            return f"5 essential {theme} tips you need to know!"
        elif content_type == "transformation":
            return f"Watch this amazing {theme} transformation!"
        elif content_type == "showcase":
            return f"Check out these stunning {theme} ideas!"
        elif content_type == "review":
            return f"My honest review of the latest {theme} trends!"
        else:
            return f"Exploring the world of {theme}!"
    
    def _split_text_for_video(self, text, max_parts=5):
        """
        Split text into parts for a video.
        
        Args:
            text (str): Text to split
            max_parts (int): Maximum number of parts
            
        Returns:
            list: List of text parts
        """
        # Simple splitting by sentences
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Group sentences into parts
        parts = []
        current_part = ""
        
        for sentence in sentences:
            if len(current_part) + len(sentence) < 100:  # Character limit per frame
                current_part += " " + sentence if current_part else sentence
            else:
                parts.append(current_part)
                current_part = sentence
        
        # Add the last part
        if current_part:
            parts.append(current_part)
        
        # Limit to max_parts
        if len(parts) > max_parts:
            # Combine excess parts
            combined = " ".join(parts[max_parts-1:])
            parts = parts[:max_parts-1] + [combined]
        
        return parts
    
    def _split_text_for_slideshow(self, text, num_slides):
        """
        Split text into parts for a slideshow.
        
        Args:
            text (str): Text to split
            num_slides (int): Number of slides
            
        Returns:
            list: List of text parts
        """
        # Simple splitting by sentences
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # If fewer sentences than slides, repeat sentences
        if len(sentences) < num_slides:
            sentences = sentences * (num_slides // len(sentences) + 1)
        
        # Group sentences into parts based on number of slides
        parts = []
        sentences_per_part = max(1, len(sentences) // num_slides)
        
        for i in range(0, len(sentences), sentences_per_part):
            part = " ".join(sentences[i:i+sentences_per_part])
            parts.append(part)
            
            if len(parts) >= num_slides:
                break
        
        return parts
