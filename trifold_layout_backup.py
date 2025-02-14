from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import os
import math
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
import requests

class TrifoldBrochureLayout:
    def __init__(self, hotel_name, location, images_dir="generated_images", output_dir="generated_brochures"):
        """Initialize the trifold brochure layout with hotel details and directories"""
        self.hotel_name = hotel_name.strip()
        self.location = location
        self.images_dir = images_dir
        self.output_dir = output_dir
        
        # Create directories if they don't exist
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up dimensions and layout parameters
        self.page_width = 2100  # A4 width (297mm) at 180 DPI
        self.page_height = 2970  # A4 height (420mm) at 180 DPI
        self.panel_width = self.page_width // 3
        self.margin = 50
        
        # Initialize fonts
        self.system_fonts = {
            'title': 'arial.ttf',  # Replace with your system font path
            'text': 'arial.ttf',
            'decorative': 'arial.ttf'
        }
        
        # Initialize fonts with different sizes
        self.font_title = ImageFont.truetype(self.system_fonts['title'], 60)
        self.font_subtitle = ImageFont.truetype(self.system_fonts['text'], 40)
        self.font_text = ImageFont.truetype(self.system_fonts['text'], 30)
        self.font_decorative = ImageFont.truetype(self.system_fonts['decorative'], 32)
        self.font_small = ImageFont.truetype(self.system_fonts['text'], 24)

    def create_trifold_layout(self, amenities, experience_text, contact_info, images):
        """Create the trifold brochure layout"""
        # Create a new image with white background
        brochure = Image.new('RGB', (self.page_width, self.page_height), 'white')
        draw = ImageDraw.Draw(brochure)
        
        # Panel positions (left to right)
        panels = [
            (0, self.panel_width),                    # Left panel
            (self.panel_width, self.panel_width * 2), # Middle panel
            (self.panel_width * 2, self.page_width)   # Right panel
        ]
        
        # Draw panel separators (light gray lines)
        for x in [self.panel_width, self.panel_width * 2]:
            draw.line([(x, 0), (x, self.page_height)], fill='#CCCCCC', width=2)
        
        # Front Panel (Right)
        self._draw_front_panel(draw, panels[2], images.get('front', None))
        
        # Inside Panels
        self._draw_inside_left_panel(draw, panels[0], amenities[:2], images.get('amenity1', None))
        self._draw_inside_middle_panel(draw, panels[1], amenities[2:], experience_text, images.get('amenity2', None))
        self._draw_inside_right_panel(draw, panels[2], contact_info, images.get('contact', None))
        
        return brochure

    def _draw_front_panel(self, draw, panel, image):
        """Draw the front panel of the brochure"""
        x_start, x_end = panel
        panel_center = (x_start + x_end) // 2
        
        # Add the main image if provided
        if image:
            try:
                img = Image.open(image)
                # Resize to fit panel width while maintaining aspect ratio
                img.thumbnail((self.panel_width - 2*self.margin, self.page_height//2))
                # Center the image horizontally and place it in the upper third
                img_x = panel_center - img.width//2
                img_y = self.page_height//4 - img.height//2
                draw.rectangle([img_x-2, img_y-2, img_x+img.width+2, img_y+img.height+2], 
                             outline='#666666', width=1)
                brochure.paste(img, (img_x, img_y))
            except Exception as e:
                print(f"Error adding front image: {str(e)}")
        
        # Add hotel name
        text_y = self.page_height * 2 // 3
        self._draw_centered_text(draw, self.hotel_name, panel_center, text_y, 
                               self.font_title, max_width=self.panel_width-2*self.margin)
        
        # Add location
        text_y += 100
        self._draw_centered_text(draw, self.location, panel_center, text_y, 
                               self.font_subtitle, max_width=self.panel_width-2*self.margin)

    def _draw_inside_left_panel(self, draw, panel, amenities, image):
        """Draw the inside left panel with amenities"""
        x_start, x_end = panel
        current_y = self.margin
        panel_center = (x_start + x_end) // 2
        
        # Add image if provided
        if image:
            try:
                img = Image.open(image)
                img.thumbnail((self.panel_width - 2*self.margin, self.page_height//3))
                img_x = panel_center - img.width//2
                brochure.paste(img, (img_x, current_y))
                current_y += img.height + self.margin
            except Exception as e:
                print(f"Error adding amenity image: {str(e)}")
        
        # Add amenities
        for title, description in amenities:
            # Draw title
            title_bbox = draw.textbbox((0, 0), title, font=self.font_subtitle)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text((x_start + self.margin, current_y), title, 
                     font=self.font_subtitle, fill='black')
            current_y += 60
            
            # Draw description with word wrap
            wrapped_text = textwrap.fill(description, width=30)
            draw.text((x_start + self.margin, current_y), wrapped_text, 
                     font=self.font_text, fill='black')
            current_y += 150

    def _draw_inside_middle_panel(self, draw, panel, amenities, experience_text, image):
        """Draw the inside middle panel with experience text and remaining amenities"""
        x_start, x_end = panel
        current_y = self.margin
        panel_center = (x_start + x_end) // 2
        
        # Add image if provided
        if image:
            try:
                img = Image.open(image)
                img.thumbnail((self.panel_width - 2*self.margin, self.page_height//3))
                img_x = panel_center - img.width//2
                brochure.paste(img, (img_x, current_y))
                current_y += img.height + self.margin
            except Exception as e:
                print(f"Error adding experience image: {str(e)}")
        
        # Add experience text
        wrapped_text = textwrap.fill(experience_text, width=35)
        draw.text((x_start + self.margin, current_y), wrapped_text, 
                 font=self.font_text, fill='black')
        current_y += 200
        
        # Add remaining amenities
        for title, description in amenities:
            # Draw title
            draw.text((x_start + self.margin, current_y), title, 
                     font=self.font_subtitle, fill='black')
            current_y += 60
            
            # Draw description
            wrapped_text = textwrap.fill(description, width=30)
            draw.text((x_start + self.margin, current_y), wrapped_text, 
                     font=self.font_text, fill='black')
            current_y += 150

    def _draw_inside_right_panel(self, draw, panel, contact_info, image):
        """Draw the inside right panel with contact information"""
        x_start, x_end = panel
        current_y = self.margin
        panel_center = (x_start + x_end) // 2
        
        # Add contact image if provided
        if image:
            try:
                img = Image.open(image)
                img.thumbnail((self.panel_width - 2*self.margin, self.page_height//3))
                img_x = panel_center - img.width//2
                brochure.paste(img, (img_x, current_y))
                current_y += img.height + self.margin
            except Exception as e:
                print(f"Error adding contact image: {str(e)}")
        
        # Add "Contact Us" header
        self._draw_centered_text(draw, "Contact Us", panel_center, current_y, 
                               self.font_subtitle)
        current_y += 80
        
        # Add contact information
        for info in contact_info:
            wrapped_text = textwrap.fill(info, width=35)
            text_bbox = draw.textbbox((0, 0), wrapped_text, font=self.font_text)
            text_width = text_bbox[2] - text_bbox[0]
            x_pos = panel_center - text_width//2
            draw.text((x_pos, current_y), wrapped_text, 
                     font=self.font_text, fill='black')
            current_y += 60

    def _draw_centered_text(self, draw, text, center_x, y, font, max_width=None):
        """Helper function to draw centered text"""
        if max_width:
            text = textwrap.fill(text, width=max_width//20)  # Approximate character width
        
        lines = text.split('\n')
        current_y = y
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = center_x - text_width//2
            draw.text((x, current_y), line, font=font, fill='black')
            current_y += bbox[3] - bbox[1] + 10  # Add some line spacing

    def save_brochure(self, brochure, filename):
        """Save the brochure as both PNG and PDF"""
        # Save as PNG
        png_path = os.path.join(self.output_dir, f"{filename}.png")
        brochure.save(png_path, "PNG", quality=95)
        
        # Convert to PDF
        pdf_path = os.path.join(self.output_dir, f"{filename}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.drawImage(ImageReader(brochure), 0, 0, A4[0], A4[1])
        c.save()
        
        return png_path, pdf_path

def create_trifold_brochure(hotel_name, location, amenities, experience_text, contact_info, images):
    """Helper function to create a trifold brochure"""
    generator = TrifoldBrochureLayout(hotel_name, location)
    brochure = generator.create_trifold_layout(amenities, experience_text, contact_info, images)
    return generator.save_brochure(brochure, f"{hotel_name.replace(' ', '_')}_brochure")
