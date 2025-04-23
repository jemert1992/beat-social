import os
import logging
import random
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("content_creation.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("content_creation.base_creator")

class ContentCreator:
    """
    Base class for creating content for social media platforms.
    """
    def __init__(self, niche, output_dir):
        """
        Initialize the content creator.
        
        Args:
            niche (str): The content niche (e.g., weddings, fitness, travel)
            output_dir (str): Directory to store created content
        """
        self.niche = niche
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.join(output_dir, niche), exist_ok=True)
        
        # Font settings
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        self.font_size = 36
        
        logger.info(f"Initialized ContentCreator for niche: {niche}")
    
    def create_content(self, content_type, theme, text=None):
        """
        Create content based on specified type and theme.
        To be implemented by platform-specific subclasses.
        
        Args:
            content_type (str): Type of content to create
            theme (str): Theme of the content
            text (str, optional): Text to include in the content
            
        Returns:
            str: Path to the created content
        """
        raise NotImplementedError("Subclasses must implement create_content method")
    
    def get_stock_image(self, query):
        """
        Get a stock image related to the query.
        
        Args:
            query (str): Search query for the image
            
        Returns:
            PIL.Image: Image object
        """
        # In a production environment, this would use Unsplash/Pexels API
        # For now, we'll use a placeholder image service
        
        # Construct a query with niche and theme
        search_term = f"{self.niche} {query}".replace(" ", "+")
        
        # Use placeholder image service
        width = 1080
        height = 1080
        url = f"https://picsum.photos/{width}/{height}?random={random.randint(1, 1000)}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                logger.info(f"Retrieved stock image for query: {query}")
                return image
            else:
                logger.error(f"Failed to retrieve stock image: {response.status_code}")
                # Return a blank image as fallback
                return self._create_blank_image(width, height)
        except Exception as e:
            logger.error(f"Error retrieving stock image: {str(e)}")
            # Return a blank image as fallback
            return self._create_blank_image(width, height)
    
    def _create_blank_image(self, width, height, color=(240, 240, 240)):
        """
        Create a blank image with the specified dimensions.
        
        Args:
            width (int): Image width
            height (int): Image height
            color (tuple): RGB color tuple
            
        Returns:
            PIL.Image: Blank image
        """
        return Image.new('RGB', (width, height), color)
    
    def add_text_overlay(self, image, text, position='center', text_color=(255, 255, 255), 
                         shadow_color=(0, 0, 0), font_size=None):
        """
        Add text overlay to an image.
        
        Args:
            image (PIL.Image): Image to add text to
            text (str): Text to add
            position (str): Position of text ('center', 'top', 'bottom')
            text_color (tuple): RGB color tuple for text
            shadow_color (tuple): RGB color tuple for text shadow
            font_size (int, optional): Font size, defaults to self.font_size
            
        Returns:
            PIL.Image: Image with text overlay
        """
        if font_size is None:
            font_size = self.font_size
        
        # Create a copy of the image to avoid modifying the original
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except IOError:
            logger.warning(f"Font file not found: {self.font_path}, using default font")
            font = ImageFont.load_default()
        
        # Wrap text to fit image width
        width, height = img.size
        max_width = width * 0.8  # Use 80% of image width for text
        wrapped_text = self._wrap_text(text, font, max_width)
        
        # Calculate text size
        text_width, text_height = draw.multiline_textbbox((0, 0), wrapped_text, font=font)[2:]
        
        # Calculate position
        if position == 'center':
            x = (width - text_width) / 2
            y = (height - text_height) / 2
        elif position == 'top':
            x = (width - text_width) / 2
            y = height * 0.1  # 10% from top
        elif position == 'bottom':
            x = (width - text_width) / 2
            y = height * 0.8 - text_height  # 20% from bottom
        else:
            x = (width - text_width) / 2
            y = (height - text_height) / 2
        
        # Add shadow (offset by 2 pixels)
        draw.multiline_text((x+2, y+2), wrapped_text, font=font, fill=shadow_color, align='center')
        
        # Add main text
        draw.multiline_text((x, y), wrapped_text, font=font, fill=text_color, align='center')
        
        return img
    
    def _wrap_text(self, text, font, max_width):
        """
        Wrap text to fit within a specified width.
        
        Args:
            text (str): Text to wrap
            font (PIL.ImageFont): Font to use for text
            max_width (int): Maximum width in pixels
            
        Returns:
            str: Wrapped text with newlines
        """
        words = text.split()
        wrapped_lines = []
        current_line = []
        
        for word in words:
            # Add word to current line
            current_line.append(word)
            
            # Check if current line exceeds max width
            line = ' '.join(current_line)
            line_width = font.getlength(line)
            
            if line_width > max_width:
                # Remove last word and add line to wrapped lines
                if len(current_line) > 1:
                    current_line.pop()
                    wrapped_lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # If a single word is too long, keep it and move to next line
                    wrapped_lines.append(line)
                    current_line = []
        
        # Add the last line
        if current_line:
            wrapped_lines.append(' '.join(current_line))
        
        return '\n'.join(wrapped_lines)
    
    def save_image(self, image, filename_prefix, content_type):
        """
        Save an image to the output directory.
        
        Args:
            image (PIL.Image): Image to save
            filename_prefix (str): Prefix for the filename
            content_type (str): Type of content
            
        Returns:
            str: Path to the saved image
        """
        # Create a sanitized filename
        sanitized_prefix = filename_prefix.replace(' ', '_').lower()
        timestamp = random.randint(10000, 99999)  # Use random number instead of timestamp for testing
        filename = f"{sanitized_prefix}_{content_type}_{timestamp}.jpg"
        
        # Create full path
        output_path = os.path.join(self.output_dir, self.niche, filename)
        
        # Save the image
        image.save(output_path, "JPEG", quality=95)
        logger.info(f"Saved image to {output_path}")
        
        return output_path
    
    def apply_branding(self, image, brand_text=None):
        """
        Apply branding to an image.
        
        Args:
            image (PIL.Image): Image to brand
            brand_text (str, optional): Branding text
            
        Returns:
            PIL.Image: Branded image
        """
        if brand_text is None:
            brand_text = f"#{self.niche.capitalize()}"
        
        # Create a copy of the image
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Get image dimensions
        width, height = img.size
        
        try:
            font = ImageFont.truetype(self.font_path, int(self.font_size * 0.6))
        except IOError:
            logger.warning(f"Font file not found: {self.font_path}, using default font")
            font = ImageFont.load_default()
        
        # Calculate text size
        text_width, text_height = draw.textbbox((0, 0), brand_text, font=font)[2:]
        
        # Position at bottom right with padding
        x = width - text_width - 20
        y = height - text_height - 20
        
        # Add semi-transparent background
        padding = 10
        draw.rectangle(
            [(x - padding, y - padding), (x + text_width + padding, y + text_height + padding)],
            fill=(0, 0, 0, 128)
        )
        
        # Add text
        draw.text((x, y), brand_text, font=font, fill=(255, 255, 255))
        
        return img
