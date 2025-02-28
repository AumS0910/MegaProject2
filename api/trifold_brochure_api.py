from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os
import requests
import logging
from PIL import Image, ImageDraw, ImageFont
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
import io
import base64
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs("generated_images", exist_ok=True)
os.makedirs("generated_brochures", exist_ok=True)

# Mount static directories
app.mount("/images", StaticFiles(directory="generated_images"), name="images")
app.mount("/brochures", StaticFiles(directory="generated_brochures"), name="brochures")

class TrifoldBrochureRequest(BaseModel):
    hotel_name: str
    location: str
    amenities: Optional[list] = None
    images: Optional[Dict[str, str]] = None

def generate_image(prompt, negative_prompt="", width=1024, height=768):
    """Generate an image using Stable Diffusion API"""
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    
    payload = {
        "prompt": f"professional high quality photograph, {prompt}",
        "negative_prompt": f"low quality, blurry, distorted, ugly {negative_prompt}",
        "steps": 30,
        "width": width,
        "height": height,
        "sampler_name": "DPM++ 2M Karras",
        "cfg_scale": 7.5,
        "seed": -1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        if response.status_code == 200:
            image_data = response.json()["images"][0]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            return image
        else:
            raise Exception(f"Stable Diffusion API returned status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise

class TrifoldBrochureGenerator:
    def __init__(self, hotel_name: str, location: str):
        self.hotel_name = hotel_name
        self.location = location
        # A4 dimensions in landscape orientation
        self.width = int(A4[1])  # Height becomes width in landscape
        self.height = int(A4[0])  # Width becomes height in landscape
        self.margin = 50
        self.panel_width = self.width // 3  # Divide into three equal panels
        
        # Initialize fonts
        font_path = os.path.join("fonts", "Montserrat-Regular.ttf")
        font_bold_path = os.path.join("fonts", "Montserrat-Bold.ttf")
        
        self.font_title = ImageFont.truetype(font_path, 140)
        self.font_section_title = ImageFont.truetype(font_bold_path, 60)
        self.font_subtitle = ImageFont.truetype(font_bold_path, 44)
        self.font_text = ImageFont.truetype(font_path, 32)
        self.font_small = ImageFont.truetype(font_path, 28)

    def generate_images(self):
        """Generate all required images using Stable Diffusion"""
        try:
            # Generate exterior image for circular display
            exterior_prompt = f"exterior view of luxury hotel {self.hotel_name} in {self.location}, architectural photography, professional real estate photo"
            exterior_image = generate_image(exterior_prompt, width=1024, height=1024)
            
            # Generate main image for middle panel
            main_prompt = f"stunning interior lobby of luxury hotel {self.hotel_name} in {self.location}, ultra wide angle, dramatic lighting"
            main_image = generate_image(main_prompt, width=1024, height=768)
            
            # Generate cover image
            cover_prompt = f"breathtaking view of {self.hotel_name} in {self.location}, golden hour, cinematic, award winning photography"
            cover_image = generate_image(cover_prompt, width=1024, height=768)
            
            # Save images to temporary files
            temp_dir = "generated_images"
            os.makedirs(temp_dir, exist_ok=True)
            
            image_paths = {}
            
            # Save exterior image
            ext_path = os.path.join(temp_dir, f"exterior_{self.hotel_name.replace(' ', '_')}.png")
            exterior_image.save(ext_path)
            image_paths["exterior"] = ext_path
            
            # Save main image
            main_path = os.path.join(temp_dir, f"main_{self.hotel_name.replace(' ', '_')}.png")
            main_image.save(main_path)
            image_paths["main"] = main_path
            
            # Save cover image
            cover_path = os.path.join(temp_dir, f"cover_{self.hotel_name.replace(' ', '_')}.png")
            cover_image.save(cover_path)
            image_paths["cover"] = cover_path
            
            return image_paths
            
        except Exception as e:
            logger.error(f"Error generating images: {str(e)}")
            raise

    def generate_brochure(self, amenities=None, images=None):
        # If no images provided, generate them
        if not images:
            try:
                images = self.generate_images()
            except Exception as e:
                logger.error(f"Failed to generate images: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to generate images: {str(e)}")
        
        # Create a new image with white background
        brochure = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(brochure)

        # Define panel boundaries (left to right)
        left_panel = (0, self.panel_width)
        middle_panel = (self.panel_width, self.panel_width * 2)
        right_panel = (self.panel_width * 2, self.width)

        # Draw panels
        self._draw_amenities_panel(draw, brochure, left_panel, amenities)
        self._draw_main_panel(draw, brochure, middle_panel, images)
        self._draw_cover_panel(draw, brochure, right_panel, images)

        # Generate both PNG and PDF
        png_path = os.path.join("generated_brochures", f"{self.hotel_name.replace(' ', '_')}_trifold_brochure.png")
        pdf_path = os.path.join("generated_brochures", f"{self.hotel_name.replace(' ', '_')}_trifold_brochure.pdf")

        # Save PNG
        brochure.save(png_path, "PNG")

        # Create PDF in landscape orientation
        self._create_pdf(pdf_path, brochure)

        return {
            "png_path": png_path,
            "pdf_path": pdf_path
        }

    def _create_pdf(self, pdf_path: str, brochure_image: Image):
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        brochure_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Create PDF in landscape orientation
        c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
        c.drawImage(ImageReader(io.BytesIO(img_byte_arr)), 0, 0, width=self.width, height=self.height)
        c.save()

    def _draw_amenities_panel(self, draw, brochure, panel, amenities):
        x_start, x_end = panel
        current_y = self.margin + 50
        panel_width = x_end - x_start
        panel_center = x_start + panel_width // 2

        # Add title
        header_text = "Amenities\n& Services"
        bbox = draw.textbbox((0, 0), header_text, font=self.font_section_title)
        header_width = bbox[2] - bbox[0]
        header_x = panel_center - header_width // 2
        draw.text((header_x, current_y), header_text, font=self.font_section_title, fill='black')
        current_y += 150

        if not amenities:
            amenities = [
                ("Luxury Suites", "Experience unparalleled comfort in our luxury suites."),
                ("Fine Dining", "Savor exquisite cuisine at our restaurants."),
                ("Spa & Wellness", "Rejuvenate your body and soul at our spa.")
            ]

        for title, description in amenities:
            # Draw title
            bbox = draw.textbbox((0, 0), title, font=self.font_subtitle)
            title_width = bbox[2] - bbox[0]
            title_x = panel_center - title_width // 2
            draw.text((title_x, current_y), title, font=self.font_subtitle, fill='black')
            current_y += 40

            # Draw description
            wrapped_desc = textwrap.fill(description, width=25)
            for line in wrapped_desc.split('\n'):
                bbox = draw.textbbox((0, 0), line, font=self.font_text)
                text_width = bbox[2] - bbox[0]
                text_x = panel_center - text_width // 2
                draw.text((text_x, current_y), line, font=self.font_text, fill='black')
                current_y += 35
            current_y += 40

    def _draw_main_panel(self, draw, brochure, panel, images):
        x_start, x_end = panel
        panel_width = x_end - x_start
        panel_center = x_start + panel_width // 2

        # Add main image if available
        if images and 'main' in images:
            try:
                main_img = Image.open(images['main'])
                # Resize maintaining aspect ratio
                main_img.thumbnail((panel_width - self.margin * 2, self.height // 2))
                # Center the image
                img_x = x_start + (panel_width - main_img.width) // 2
                img_y = self.margin
                brochure.paste(main_img, (img_x, img_y))
            except Exception as e:
                print(f"Error adding main image: {str(e)}")

        # Add contact information
        contact_y = self.height - 300
        email_domain = self.hotel_name.lower().replace(" ", "")
        contact_info = [
            "Contact Information",
            "",
            f"For reservations and inquiries,",
            f"please reach out to us at {self.hotel_name}:",
            "",
            "(555) 123-4567",
            f"reservations@{email_domain}.com",
            f"www.{email_domain}.com"
        ]

        for line in contact_info:
            bbox = draw.textbbox((0, 0), line, font=self.font_text)
            text_width = bbox[2] - bbox[0]
            text_x = panel_center - text_width // 2
            draw.text((text_x, contact_y), line, font=self.font_text, fill='black')
            contact_y += 35

    def _draw_cover_panel(self, draw, brochure, panel, images):
        x_start, x_end = panel
        panel_width = x_end - x_start
        panel_center = x_start + panel_width // 2

        # Add background image if available
        if images and 'cover' in images:
            try:
                cover_img = Image.open(images['cover'])
                # Resize to fill panel
                cover_img = cover_img.resize((panel_width, self.height))
                brochure.paste(cover_img, (x_start, 0))
            except Exception as e:
                print(f"Error adding cover image: {str(e)}")

        # Add hotel name with shadow effect
        hotel_name_y = self.height // 2
        shadow_offset = 3
        
        # Draw shadow first
        draw.text(
            (panel_center - shadow_offset, hotel_name_y - shadow_offset), 
            self.hotel_name,
            font=self.font_title,
            fill='rgba(0, 0, 0, 0.5)',
            anchor='mm'
        )
        
        # Draw main text
        draw.text(
            (panel_center, hotel_name_y),
            self.hotel_name,
            font=self.font_title,
            fill='white',
            anchor='mm'
        )

@app.post("/generate-trifold-brochure")
async def generate_trifold_brochure(request: TrifoldBrochureRequest):
    try:
        generator = TrifoldBrochureGenerator(request.hotel_name, request.location)
        result = generator.generate_brochure(request.amenities, request.images)
        
        return {
            "status": "success",
            "file_paths": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
