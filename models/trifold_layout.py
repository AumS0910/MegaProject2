from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import os
import math
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
import requests
import logging

logger = logging.getLogger(__name__)

class TrifoldBrochureLayout:
    def __init__(self, hotel_name, location, images_dir="generated_images", output_dir="generated_brochures"):
        self.hotel_name = hotel_name
        self.location = location
        self.images_dir = images_dir
        self.output_dir = output_dir
        self.images = {}  # Will store image paths
        self.contact_info = {}  # Store contact information
        
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up dimensions for a landscape A4 brochure
        self.page_width = 2480  # A4 height (297mm) at 254 DPI
        self.page_height = 1754  # A4 width (210mm) at 254 DPI
        self.panel_width = self.page_width // 3
        self.margin = 80  # Increased margin for elegance
        
        # Initialize fonts
        self.system_fonts = {
            'title': 'arial.ttf',
            'text': 'arial.ttf'
        }
        
        # Initialize fonts with increased sizes
        self.font_title = ImageFont.truetype(self.system_fonts['title'], 120)  # Larger title
        self.font_section_title = ImageFont.truetype(self.system_fonts['title'], 70)  # Slightly larger section titles
        self.font_subtitle = ImageFont.truetype(self.system_fonts['text'], 45)  # Adjusted subtitle size
        self.font_text = ImageFont.truetype(self.system_fonts['text'], 35)  # Slightly smaller body text
        self.font_small = ImageFont.truetype(self.system_fonts['text'], 28)  # Increased from 20

    def create_trifold_layout(self, amenities, experience_text, contact_info, images):
        """Create the trifold brochure layout"""
        self.images = images  # Store images for use in other methods
        self.contact_info = contact_info  # Store contact information
        
        # Create base image with white background
        brochure = Image.new('RGB', (self.page_width, self.page_height), '#FFFFFF')
        draw = ImageDraw.Draw(brochure)
        
        # Panel positions (left to right)
        panels = [
            (0, self.panel_width),                    # Left panel (Amenities)
            (self.panel_width, 2*self.panel_width),   # Middle panel (Main image)
            (2*self.panel_width, self.page_width)     # Right panel (Cover)
        ]
        
        # Draw panels from back to front
        self._draw_cover_panel(draw, brochure, panels[2], self.images.get('exterior'))  # Draw cover first
        self._draw_middle_panel(draw, brochure, panels[1], self.images.get('room'), contact_info)
        self._draw_amenities_panel(draw, brochure, panels[0], amenities)
        
        return brochure

    def _draw_amenities_panel(self, draw, brochure, panel, amenities):
        """Draw the amenities panel (left panel)"""
        x_start, x_end = panel
        panel_width = x_end - x_start
        panel_center = x_start + panel_width // 2

        # Draw panel background with cream color
        background = Image.new('RGB', (panel_width, self.page_height), '#FFF8E7')  # Cream/beige color
        brochure.paste(background, (x_start, 0))

        # Draw "Amenities & Services" header
        header_text = "Amenities\n& Services"
        y = self.margin + 40
        bbox = draw.textbbox((0, 0), header_text, font=self.font_section_title)
        text_height = bbox[3] - bbox[1]
        self._draw_centered_text(draw, header_text, panel_center, y, self.font_section_title)
        
        # Calculate spacing for amenities
        circle_size = 520  # Size for the circular image
        content_height = self.page_height - (y + text_height + 60) - (circle_size + self.margin)
        
        # Ensure we have exactly 3 amenities for spacing calculation
        num_amenities = 3
        spacing = content_height / (num_amenities * 2)  # Distribute space evenly
        
        # Start amenities after header
        y += text_height + 60

        # Draw each amenity
        for title, description in amenities[:3]:  # Ensure we only draw 3 amenities
            # Draw amenity title
            bbox = draw.textbbox((0, 0), title, font=self.font_subtitle)
            title_height = bbox[3] - bbox[1]
            self._draw_centered_text(draw, title, panel_center, y, self.font_subtitle)
            y += title_height + 15  # Reduced space after title
            
            # Draw amenity description with proper width
            max_width = int(panel_width * 0.85)  # Slightly wider for better text flow
            bbox = draw.textbbox((0, 0), description, font=self.font_text)
            desc_height = bbox[3] - bbox[1]
            self._draw_centered_text(draw, description, panel_center, y, self.font_text, max_width=max_width)
            y += desc_height + spacing  # Space after description

        # Add circular image at the bottom
        if self.images.get("exterior"):
            try:
                img = Image.open(self.images["exterior"])
                
                # Create circular image
                min_size = max(img.width, img.height, circle_size)
                img = img.resize((min_size, min_size), Image.Resampling.LANCZOS)
                
                # Center crop to square
                left = (img.width - min_size) // 2
                top = (img.height - min_size) // 2
                img = img.crop((left, top, left + min_size, top + min_size))
                
                # Resize to final size
                img = img.resize((circle_size, circle_size), Image.Resampling.LANCZOS)
                
                # Create circular mask
                mask = Image.new('L', (circle_size, circle_size), 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0, circle_size, circle_size), fill=255)
                
                # Apply Gaussian blur for softer edges
                mask = mask.filter(ImageFilter.GaussianBlur(radius=2))
                
                # Create circular image
                output = Image.new('RGBA', (circle_size, circle_size), (0, 0, 0, 0))
                output.paste(img, (0, 0))
                output.putalpha(mask)
                
                # Position image at bottom with cream background behind it
                img_x = panel_center - circle_size // 2
                img_y = self.page_height - circle_size - self.margin
                
                # Add subtle shadow
                shadow = Image.new('RGBA', (circle_size, circle_size), (0, 0, 0, 30))  # Lighter shadow
                shadow.putalpha(mask)
                brochure.paste(shadow, (img_x + 4, img_y + 4), shadow)
                brochure.paste(output, (img_x, img_y), output)
                
            except Exception as e:
                logger.error(f"Error adding circular image: {str(e)}")

    def _draw_middle_panel(self, draw, brochure, panel, image_path, contact_info):
        """Draw the middle panel"""
        x_start, x_end = panel
        panel_width = x_end - x_start
        panel_center = x_start + panel_width // 2

        # Add main image at the top
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                # Resize image to fit panel width while maintaining aspect ratio
                aspect = img.height / img.width
                new_width = panel_width - self.margin * 2
                new_height = int(new_width * aspect)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Position image
                x = x_start + (panel_width - new_width) // 2
                y = self.margin
                brochure.paste(img, (x, y))
                
                # Update y position for next element
                y += new_height + self.margin * 2
            except Exception as e:
                print(f"Error adding main image: {str(e)}")
                y = self.margin * 2

        # Draw "Contact Information" header
        header_text = "Contact\nInformation"
        bbox = draw.textbbox((0, 0), header_text, font=self.font_section_title)
        text_height = bbox[3] - bbox[1]
        self._draw_centered_text(draw, header_text, panel_center, y, self.font_section_title)
        y += text_height + 40

        # Draw "Ready to plan your getaway" text
        ready_text = "Ready to plan your getaway at\n" + self.hotel_name + "?"
        bbox = draw.textbbox((0, 0), ready_text, font=self.font_subtitle)
        text_height = bbox[3] - bbox[1]
        self._draw_centered_text(draw, ready_text, panel_center, y, self.font_subtitle)
        y += text_height + 30

        # Draw contact information
        contact_text = "For reservations and inquiries,\nplease reach out to us:"
        bbox = draw.textbbox((0, 0), contact_text, font=self.font_text)
        text_height = bbox[3] - bbox[1]
        self._draw_centered_text(draw, contact_text, panel_center, y, self.font_text)
        y += text_height + 30

        # Format hotel name for email and website
        email_domain = self.hotel_name.lower().replace(" ", "")

        # Draw contact details with hotel-specific email and website
        if contact_info:
            contact_items = [
                contact_info.get("phone", "+1 (555) 123-4567"),
                contact_info.get("email", f"reservations@{email_domain}.com"),
                contact_info.get("website", f"www.{email_domain}.com")
            ]
            
            for item in contact_items:
                bbox = draw.textbbox((0, 0), item, font=self.font_text)
                text_height = bbox[3] - bbox[1]
                self._draw_centered_text(draw, item, panel_center, y, self.font_text)
                y += text_height + 15

    def _draw_cover_panel(self, draw, brochure, panel, background_image):
        """Draw the cover panel (right panel)"""
        x_start, x_end = panel
        panel_width = x_end - x_start
        panel_center = x_start + panel_width // 2
        
        try:
            # Open and process the background image
            if background_image and os.path.exists(background_image):
                img = Image.open(background_image)
                
                # Resize to cover the entire panel while maintaining aspect ratio
                aspect_ratio = img.height / img.width
                new_width = panel_width
                new_height = int(new_width * aspect_ratio)
                
                # If height is too short, scale by height instead
                if new_height < self.page_height:
                    new_height = self.page_height
                    new_width = int(new_height / aspect_ratio)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center crop if needed
                left = (new_width - panel_width) // 2
                top = (new_height - self.page_height) // 2
                img = img.crop((left, top, left + panel_width, top + self.page_height))
                
                # Create gradient overlay
                gradient = Image.new('RGBA', (panel_width, self.page_height), (0, 0, 0, 0))
                draw_gradient = ImageDraw.Draw(gradient)
                
                # Add subtle darkening gradient at the bottom for text readability
                for y in range(self.page_height - 400, self.page_height):
                    alpha = int(180 * (y - (self.page_height - 400)) / 400)  # Gradually increase opacity
                    draw_gradient.line([(0, y), (panel_width, y)], fill=(0, 0, 0, alpha))
                
                # Convert background to RGBA if it isn't already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Composite the gradient onto the background
                img = Image.alpha_composite(img, gradient)
                
                # Paste the final image
                brochure.paste(img, (x_start, 0))
            
            # Draw hotel name
            hotel_text = self.hotel_name.upper()
            resort_text = "HOTEL\nRESORT"  # Add 'HOTEL RESORT' text
            
            # Calculate position for hotel name (near bottom)
            font_size = 80  # Larger font size for hotel name
            font = ImageFont.truetype("arial.ttf", font_size)
            
            # Position text near bottom but above gradient
            y_position = self.page_height - 300
            
            # Draw hotel name
            bbox = draw.textbbox((0, 0), hotel_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = panel_center - text_width // 2
            draw.text((x, y_position), hotel_text, fill='white', font=font)
            
            # Draw 'HOTEL RESORT' below hotel name
            y_position += 100  # Space below hotel name
            bbox = draw.textbbox((0, 0), resort_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = panel_center - text_width // 2
            draw.text((x, y_position), resort_text, fill='white', font=font)
            
        except Exception as e:
            logger.error(f"Error creating cover panel: {str(e)}")
            # Create a simple gradient background as fallback
            gradient = Image.new('RGB', (panel_width, self.page_height), '#FFFFFF')
            draw_gradient = ImageDraw.Draw(gradient)
            
            for y in range(self.page_height):
                # Create a blue-gray gradient
                color = int(255 * (1 - y/self.page_height))
                draw_gradient.line([(0, y), (panel_width, y)], 
                                 fill=(color, color, int(color * 1.1)))
            
            brochure.paste(gradient, (x_start, 0))

    def _draw_centered_text(self, draw, text, center_x, y, font, color='black', max_width=None):
        """Helper function to draw centered text with line wrapping"""
        if not text:
            return y

        # Split text into lines if it contains newlines
        lines = text.split('\n')
        
        # Process each line
        for line in lines:
            words = line.split()
            current_line = []
            current_width = 0
            
            for word in words:
                word_bbox = draw.textbbox((0, 0), word, font=font)
                word_width = word_bbox[2] - word_bbox[0]
                space_width = draw.textbbox((0, 0), ' ', font=font)[2]
                
                # Check if adding this word would exceed max_width
                if max_width and current_width + word_width > max_width and current_line:
                    # Draw current line
                    text_to_draw = ' '.join(current_line)
                    bbox = draw.textbbox((0, 0), text_to_draw, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = center_x - text_width // 2
                    draw.text((x, y), text_to_draw, font=font, fill=color)
                    y += int(bbox[3] - bbox[1] + 10)  # Add small padding between lines
                    
                    # Start new line with current word
                    current_line = [word]
                    current_width = word_width
                else:
                    current_line.append(word)
                    current_width += word_width + space_width
            
            # Draw remaining text
            if current_line:
                text_to_draw = ' '.join(current_line)
                bbox = draw.textbbox((0, 0), text_to_draw, font=font)
                text_width = bbox[2] - bbox[0]
                x = center_x - text_width // 2
                draw.text((x, y), text_to_draw, font=font, fill=color)
                y += int(bbox[3] - bbox[1] + 15)  # Add padding after each paragraph
        
        return y

    def save_brochure(self, brochure, filename):
        """Save the brochure as both PNG and PDF"""
        # Save as PNG
        png_path = os.path.join(self.output_dir, f"{filename}.png")
        brochure.save(png_path, "PNG", quality=95)
        
        # Convert to PDF
        pdf_path = os.path.join(self.output_dir, f"{filename}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=(self.page_width, self.page_height))
        c.drawImage(ImageReader(brochure), 0, 0, self.page_width, self.page_height)
        c.save()
        
        return png_path, pdf_path

def create_trifold_brochure(hotel_name, location, amenities, experience_text, contact_info, images):
    """Helper function to create a trifold brochure"""
    generator = TrifoldBrochureLayout(hotel_name, location)
    brochure = generator.create_trifold_layout(amenities, experience_text, contact_info, images)
    return generator.save_brochure(brochure, f"{hotel_name.replace(' ', '_')}_brochure")
