import os
import logging
import random
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import moviepy.editor as mp
from .base_creator import ContentCreator

logger = logging.getLogger("content_creation.instagram_creator")

class InstagramContentCreator(ContentCreator):
    """
    Class for creating content specifically for Instagram.
    """
    def __init__(self, niche, output_dir):
        """
        Initialize the Instagram content creator.
        
        Args:
            niche (str): The content niche (e.g., weddings, fitness, travel)
            output_dir (str): Directory to store created content
        """
        super().__init__(niche, output_dir)
        
        # Instagram-specific dimensions
        self.post_width = 1080
        self.post_height = 1350  # 4:5 aspect ratio for posts
        self.reel_width = 1080
        self.reel_height = 1920  # 9:16 aspect ratio for reels
        self.carousel_count = 5  # Default number of images in carousel
        
        logger.info(f"Initialized InstagramContentCreator for niche: {niche}")
    
    def create_content(self, content_type, theme, text=None, trending_data=None):
        """
        Create Instagram content based on specified type and theme.
        
        Args:
            content_type (str): Type of content to create (e.g., single_image, carousel, reel)
            theme (str): Theme of the content
            text (str, optional): Text to include in the content
            trending_data (dict, optional): Trending data to inform content creation
            
        Returns:
            str or list: Path(s) to the created content
        """
        logger.info(f"Creating Instagram {content_type} content with theme: {theme}")
        
        if text is None:
            text = self._generate_text_for_theme(theme, content_type)
        
        if content_type == "single_image":
            return self.create_single_image(theme, text)
        elif content_type == "carousel":
            return self.create_carousel(theme, text)
        elif content_type == "reel":
            return self.create_reel(theme, text)
        elif content_type == "igtv":
            return self.create_igtv(theme, text)
        else:
            # Default to a single image post
            return self.create_single_image(theme, text)
    
    def create_single_image(self, theme, text):
        """
        Create a single image post for Instagram.
        
        Args:
            theme (str): Theme of the content
            text (str): Text to include in the image
            
        Returns:
            str: Path to the created image
        """
        logger.info(f"Creating single image post for theme: {theme}")
        
        # Get a background image related to the theme
        image = self.get_stock_image(theme)
        image = image.resize((self.post_width, self.post_height))
        
        # Add text overlay
        image = self.add_text_overlay(image, text, position='center', 
                                     text_color=(255, 255, 255), 
                                     shadow_color=(0, 0, 0),
                                     font_size=42)
        
        # Add branding
        image = self.apply_branding(image)
        
        # Save the image
        sanitized_theme = theme.replace(' ', '_').lower()
        return self.save_image(image, f"instagram_{sanitized_theme}", "single")
    
    def create_carousel(self, theme, text, num_images=None):
        """
        Create a carousel post for Instagram.
        
        Args:
            theme (str): Theme of the content
            text (str): Text to include in the images
            num_images (int, optional): Number of images in the carousel
            
        Returns:
            list: Paths to the created images
        """
        if num_images is None:
            num_images = self.carousel_count
            
        logger.info(f"Creating carousel with {num_images} images for theme: {theme}")
        
        # Split text into parts for each carousel slide
        text_parts = self._split_text_for_carousel(text, num_images)
        
        # Create images for carousel
        carousel_images = []
        for i in range(num_images):
            # Get a different image for each slide
            image = self.get_stock_image(f"{theme} {i}")
            image = image.resize((self.post_width, self.post_height))
            
            # Add slide number
            slide_text = f"{i+1}/{num_images}"
            image = self._add_slide_number(image, slide_text)
            
            # Add text overlay
            current_text = text_parts[i % len(text_parts)]
            image = self.add_text_overlay(image, current_text, position='center', 
                                         text_color=(255, 255, 255), 
                                         shadow_color=(0, 0, 0),
                                         font_size=42)
            
            # Add branding
            image = self.apply_branding(image)
            
            # Save the image
            sanitized_theme = theme.replace(' ', '_').lower()
            image_path = self.save_image(image, f"instagram_{sanitized_theme}_carousel_{i+1}", "carousel")
            carousel_images.append(image_path)
        
        logger.info(f"Created {len(carousel_images)} carousel images")
        return carousel_images
    
    def create_reel(self, theme, text):
        """
        Create a reel for Instagram.
        
        Args:
            theme (str): Theme of the content
            text (str): Text to include in the reel
            
        Returns:
            str: Path to the created reel
        """
        logger.info(f"Creating reel for theme: {theme}")
        
        # Get a background image related to the theme
        background = self.get_stock_image(theme)
        background = background.resize((self.reel_width, self.reel_height))
        
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
        clip_duration = 15 / len(frames)  # 15 seconds total
        clips = [mp.ImageClip(frame).set_duration(clip_duration) for frame in frames]
        
        final_clip = mp.concatenate_videoclips(clips, method="compose")
        
        # Add simple fade transitions
        final_clip = final_clip.fadein(0.5).fadeout(0.5)
        
        # Save the video
        sanitized_theme = theme.replace(' ', '_').lower()
        timestamp = random.randint(10000, 99999)
        output_path = os.path.join(self.output_dir, self.niche, f"instagram_reel_{sanitized_theme}_{timestamp}.mp4")
        
        final_clip.write_videofile(output_path, codec='libx264', audio=False, fps=24)
        
        # Clean up temporary files
        for frame in frames:
            os.remove(frame)
        os.rmdir(temp_dir)
        
        logger.info(f"Created reel at {output_path}")
        return output_path
    
    def create_igtv(self, theme, text):
        """
        Create an IGTV video for Instagram.
        
        Args:
            theme (str): Theme of the content
            text (str): Text to include in the video
            
        Returns:
            str: Path to the created video
        """
        logger.info(f"Creating IGTV video for theme: {theme}")
        
        # IGTV is similar to reels but longer
        # Get multiple background images related to the theme
        backgrounds = [self.get_stock_image(f"{theme} {i}") for i in range(5)]
        backgrounds = [bg.resize((self.reel_width, self.reel_height)) for bg in backgrounds]
        
        # Add text overlay
        text_parts = self._split_text_for_video(text, max_parts=10)  # More parts for longer video
        
        # Create a temporary directory for frames
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        # Create frames with different text parts and backgrounds
        frames = []
        for i, part in enumerate(text_parts):
            # Cycle through backgrounds
            frame = backgrounds[i % len(backgrounds)].copy()
            frame = self.add_text_overlay(frame, part, position='center', 
                                         text_color=(255, 255, 255), 
                                         shadow_color=(0, 0, 0),
                                         font_size=48)
            frame = self.apply_branding(frame)
            
            frame_path = os.path.join(temp_dir, f"frame_{i:03d}.jpg")
            frame.save(frame_path, "JPEG", quality=95)
            frames.append(frame_path)
        
        # Create video from frames
        clip_duration = 30 / len(frames)  # 30 seconds total for IGTV
        clips = [mp.ImageClip(frame).set_duration(clip_duration) for frame in frames]
        
        final_clip = mp.concatenate_videoclips(clips, method="compose")
        
        # Add transitions
        final_clip = final_clip.fadein(0.5).fadeout(0.5)
        
        # Save the video
        sanitized_theme = theme.replace(' ', '_').lower()
        timestamp = random.randint(10000, 99999)
        output_path = os.path.join(self.output_dir, self.niche, f"instagram_igtv_{sanitized_theme}_{timestamp}.mp4")
        
        final_clip.write_videofile(output_path, codec='libx264', audio=False, fps=24)
        
        # Clean up temporary files
        for frame in frames:
            os.remove(frame)
        os.rmdir(temp_dir)
        
        logger.info(f"Created IGTV video at {output_path}")
        return output_path
    
    def _add_slide_number(self, image, text, position='top-right'):
        """
        Add slide number to an image.
        
        Args:
            image (PIL.Image): Image to add slide number to
            text (str): Slide number text (e.g., "1/5")
            position (str): Position of the slide number
            
        Returns:
            PIL.Image: Image with slide number
        """
        # Create a copy of the image
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Get image dimensions
        width, height = img.size
        
        try:
            font = ImageFont.truetype(self.font_path, int(self.font_size * 0.8))
        except IOError:
            logger.warning(f"Font file not found: {self.font_path}, using default font")
            font = ImageFont.load_default()
        
        # Calculate text size
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        
        # Position based on parameter
        if position == 'top-right':
            x = width - text_width - 20
            y = 20
        elif position == 'top-left':
            x = 20
            y = 20
        else:  # Default to top-right
            x = width - text_width - 20
            y = 20
        
        # Add semi-transparent background
        padding = 10
        draw.rectangle(
            [(x - padding, y - padding), (x + text_width + padding, y + text_height + padding)],
            fill=(0, 0, 0, 128)
        )
        
        # Add text
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        return img
    
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
        
        if content_type == "single_image":
            return f"Exploring the beauty of {theme}. What's your favorite part about it?"
        elif content_type == "carousel":
            return f"Swipe to see our top {self.carousel_count} {theme} inspirations!"
        elif content_type == "reel":
            return f"Quick tips for mastering {theme}! Save this for later!"
        elif content_type == "igtv":
            return f"A deep dive into everything you need to know about {theme}. Watch till the end for a special tip!"
        else:
            return f"Sharing our love for {theme}! Double tap if you agree!"
    
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
    
    def _split_text_for_carousel(self, text, num_slides):
        """
        Split text into parts for a carousel.
        
        Args:
            text (str): Text to split
            num_slides (int): Number of slides
            
        Returns:
            list: List of text parts
        """
        # For carousels, we want each slide to have a complete thought
        # Simple splitting by sentences
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # If fewer sentences than slides, add generic sentences
        if len(sentences) < num_slides:
            generic_sentences = [
                f"Discover the beauty of {self.niche}.",
                f"Explore new {self.niche} ideas.",
                f"Get inspired by these {self.niche} concepts.",
                f"Transform your approach to {self.niche}.",
                f"Share your {self.niche} journey with us!"
            ]
            sentences.extend(generic_sentences[:num_slides - len(sentences)])
        
        # Group sentences into parts based on number of slides
        parts = []
        sentences_per_part = max(1, len(sentences) // num_slides)
        
        for i in range(0, len(sentences), sentences_per_part):
            part = " ".join(sentences[i:i+sentences_per_part])
            parts.append(part)
            
            if len(parts) >= num_slides:
                break
        
        return parts
