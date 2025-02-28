from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import sys
import requests
import json
import base64
from PIL import Image
import io
import logging
from PIL import ImageDraw, ImageFont
import shutil
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.trifold_layout import TrifoldBrochureLayout

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("generated_images", exist_ok=True)
os.makedirs("generated_brochures", exist_ok=True)

# Mount static directories with custom configuration
app.mount("/images", StaticFiles(directory="generated_images", check_dir=True), name="images")
app.mount("/brochures", StaticFiles(directory="generated_brochures", check_dir=True), name="brochures")

# Add response headers middleware for static files
@app.middleware("http")
async def add_static_files_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/images/", "/brochures/")):
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/images/{filename}")
async def get_image(filename: str):
    """Serve image files with proper headers"""
    file_path = os.path.join("generated_images", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(
        file_path,
        headers={
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/brochures/{filename}")
async def get_brochure(filename: str):
    """Serve PDF files with proper headers"""
    file_path = os.path.join("generated_brochures", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Brochure not found")
    return FileResponse(
        file_path,
        headers={
            "Content-Type": "application/pdf",
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*"
        }
    )

class TrifoldRequest(BaseModel):
    hotel_name: str
    location: str
    amenities: Optional[List[Dict[str, str]]] = None
    experience_text: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None

def generate_image(prompt, negative_prompt="", width=1024, height=768):
    """Generate an image using Stable Diffusion API"""
    url = "http://127.0.0.1:7861/sdapi/v1/txt2img"
    
    payload = {
        "prompt": f"professional high quality photograph, {prompt}, 8k, ultra detailed",
        "negative_prompt": f"low quality, blurry, distorted, ugly, deformed {negative_prompt}",
        "steps": 30,
        "width": width,
        "height": height,
        "sampler_name": "DPM++ 2M Karras",
        "cfg_scale": 7.5,
        "seed": -1
    }
    
    try:
        logger.info(f"Sending request to Stable Diffusion API at {url}")
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

def generate_hotel_images(hotel_name: str, location: str, images_dir: str) -> Dict[str, str]:
    """Generate all required images for the hotel brochure"""
    try:
        # First try to generate images with Stable Diffusion
        try:
            logger.info("Attempting to generate images with Stable Diffusion...")
            image_paths = {}
            hotel_prefix = hotel_name.replace(" ", "_")
            
            # Generate and save exterior image
            exterior_prompt = f"exterior view of luxury hotel {hotel_name} in {location}, architectural photography, professional real estate photo"
            exterior_image = generate_image(exterior_prompt, width=1024, height=1024)
            ext_path = os.path.join(images_dir, f"{hotel_prefix}_exterior.png")
            exterior_image.save(ext_path)
            image_paths["exterior"] = ext_path
            
            # Generate and save room image
            room_prompt = f"luxurious hotel room interior at {hotel_name} in {location}, ultra wide angle, dramatic lighting"
            room_image = generate_image(room_prompt, width=1024, height=768)
            room_path = os.path.join(images_dir, f"{hotel_prefix}_room.png")
            room_image.save(room_path)
            image_paths["room"] = room_path
            
            # Generate and save restaurant image
            restaurant_prompt = f"elegant restaurant interior at {hotel_name} in {location}, fine dining atmosphere"
            restaurant_image = generate_image(restaurant_prompt, width=1024, height=768)
            restaurant_path = os.path.join(images_dir, f"{hotel_prefix}_restaurant.png")
            restaurant_image.save(restaurant_path)
            image_paths["restaurant"] = restaurant_path
            
            # Use exterior image for front as well
            image_paths["front"] = ext_path
            
            return image_paths
            
        except Exception as sd_error:
            logger.warning(f"Stable Diffusion not available: {str(sd_error)}. Using fallback images...")
            
            # Use fallback stock images
            fallback_images_dir = os.path.join("static", "fallback_images")
            if not os.path.exists(fallback_images_dir):
                os.makedirs(fallback_images_dir, exist_ok=True)
                
                # Create some basic placeholder images if they don't exist
                for img_type in ["exterior", "room", "restaurant"]:
                    img_path = os.path.join(fallback_images_dir, f"{img_type}.png")
                    if not os.path.exists(img_path):
                        # Create a simple gradient image as placeholder
                        width = 1024
                        height = 1024 if img_type == "exterior" else 768
                        img = Image.new('RGB', (width, height))
                        draw = ImageDraw.Draw(img)
                        
                        # Create gradient background
                        for y in range(height):
                            r = int(255 * (1 - y/height))
                            g = int(200 * (1 - y/height))
                            b = int(155 * (1 - y/height))
                            draw.line([(0, y), (width, y)], fill=(r, g, b))
                            
                        # Add text
                        font_size = 40
                        try:
                            font = ImageFont.truetype("arial.ttf", font_size)
                        except:
                            font = ImageFont.load_default()
                            
                        text = f"Sample {img_type.title()} Image"
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        x = (width - text_width) // 2
                        y = (height - text_height) // 2
                        draw.text((x, y), text, fill='white', font=font)
                        
                        img.save(img_path)
            
            # Use the fallback images
            hotel_prefix = hotel_name.replace(" ", "_")
            image_paths = {}
            
            # Copy and rename fallback images for this hotel
            for img_type in ["exterior", "room", "restaurant"]:
                src_path = os.path.join(fallback_images_dir, f"{img_type}.png")
                dst_path = os.path.join(images_dir, f"{hotel_prefix}_{img_type}.png")
                shutil.copy2(src_path, dst_path)
                image_paths[img_type] = dst_path
            
            # Use exterior image for front as well
            image_paths["front"] = image_paths["exterior"]
            
            return image_paths
            
    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}")
        raise

async def generate_amenities_with_t5(hotel_name: str, location: str) -> List[tuple]:
    """Generate amenities using T5 model"""
    url = "http://127.0.0.1:8005/generate"
    prompt = f"Generate exactly 3 luxury amenities for {hotel_name} in {location}. Include: 1) A spa/wellness amenity, 2) A dining amenity, 3) An accommodation amenity. Format each as 'Title: Description'. Make each description unique and detailed."
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"prompt": prompt}) as response:
                if response.status == 200:
                    data = await response.json()
                    generated_text = data.get("generated_text", "")
                    
                    # Parse the generated text into amenities
                    amenities = []
                    lines = [line.strip() for line in generated_text.strip().split('\n') if ':' in line]
                    
                    for line in lines:
                        if ':' in line:
                            title, description = line.split(':', 1)
                            # Clean and format the title and description
                            title = title.strip().title()
                            description = description.strip()
                            if title and description and (title, description) not in amenities:
                                amenities.append((title, description))
                    
                    # Ensure we have exactly 3 unique amenities
                    defaults = _get_default_amenities(hotel_name, location)
                    while len(amenities) < 3:
                        for default in defaults:
                            if len(amenities) >= 3:
                                break
                            if default not in amenities:
                                amenities.append(default)
                    
                    return amenities[:3]  # Return exactly 3 amenities
                    
                else:
                    logger.error(f"T5 API returned status code {response.status}")
                    return _get_default_amenities(hotel_name, location)
    except Exception as e:
        logger.error(f"Error generating amenities with T5: {str(e)}")
        return _get_default_amenities(hotel_name, location)

def _get_default_amenities(hotel_name: str, location: str) -> List[tuple]:
    """Get default amenities if T5 generation fails"""
    return [
        ("Luxury Spa & Wellness", f"Immerse yourself in tranquility at our world-class spa featuring traditional and modern treatments with panoramic views of {location}."),
        ("Gourmet Dining Experience", f"Savor exquisite cuisine at our signature restaurants, featuring local and international dishes prepared by renowned chefs with locally-sourced ingredients."),
        ("Premium Suite Accommodations", f"Experience unparalleled comfort in our meticulously designed suites, each offering stunning views of {location} and premium amenities.")
    ]

async def generate_experience_text_with_t5(hotel_name: str, location: str) -> str:
    """Generate experience text using T5 model"""
    try:
        prompt = f"Generate a short luxury experience description for {hotel_name} in {location}. Focus on the unique features and ambiance."
        url = "http://127.0.0.1:8005/generate"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"prompt": prompt}) as response:
                if response.status == 200:
                    data = await response.json()
                    experience_text = data.get("generated_text", "").strip()
                else:
                    experience_text = f"Experience luxury and comfort at {hotel_name}"
    except Exception as e:
        logger.error(f"Error generating experience text: {str(e)}")
        experience_text = f"Experience luxury and comfort at {hotel_name}"
    
    return experience_text

@app.post("/generate-trifold")
async def generate_trifold_brochure(request: TrifoldRequest):
    """Generate a trifold brochure based on the request"""
    try:
        # Create directories if they don't exist
        os.makedirs("generated_images", exist_ok=True)
        os.makedirs("generated_brochures", exist_ok=True)
        
        # Generate images for the brochure
        images = generate_hotel_images(request.hotel_name, request.location, "generated_images")
        
        # Generate amenities using T5
        amenities = await generate_amenities_with_t5(request.hotel_name, request.location)
        
        # Format hotel name for email
        email_domain = request.hotel_name.lower().replace(" ", "")
        
        # Ensure contact_info is not None and create default if needed
        contact_info = request.contact_info if request.contact_info else {}
        
        # Create contact information with defaults
        formatted_contact = {
            "phone": contact_info.get("phone", "+1 (555) 123-4567"),
            "email": contact_info.get("email", f"reservations@{email_domain}.com"),
            "website": contact_info.get("website", f"www.{email_domain}.com")
        }
        
        # Generate experience text using T5
        experience_text = await generate_experience_text_with_t5(request.hotel_name, request.location)
        
        # Create the brochure layout
        brochure = TrifoldBrochureLayout(
            hotel_name=request.hotel_name,
            location=request.location,
            images_dir="generated_images",
            output_dir="generated_brochures"
        )
        
        # Create the layout with all required parameters
        brochure_image = brochure.create_trifold_layout(
            amenities=amenities,
            experience_text=experience_text,
            contact_info=formatted_contact,
            images=images
        )
        
        # Save the brochure as PNG and PDF
        filename = f"{request.hotel_name.replace(' ', '_')}_brochure"
        png_path, pdf_path = brochure.save_brochure(brochure_image, filename)
        
        # Get relative paths for response
        rel_pdf_path = os.path.basename(pdf_path)
        rel_png_path = os.path.basename(png_path)
        
        return {
            "status": "success",
            "message": "Brochure generated successfully",
            "files": {
                "pdf": rel_pdf_path,
                "png": rel_png_path
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating brochure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent-brochures")
async def get_recent_brochures(limit: int = 10):
    """Get list of recently generated brochures"""
    try:
        brochures_dir = "generated_brochures"
        images_dir = "generated_images"
        
        # Ensure directories exist
        os.makedirs(brochures_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        
        logger.info(f"Looking for brochures in: {brochures_dir}")
        logger.info(f"Looking for images in: {images_dir}")
        
        # Get list of PDF files in brochures directory
        brochures = []
        for filename in os.listdir(brochures_dir):
            if not filename.endswith(".pdf"):
                continue
                
            file_path = os.path.join(brochures_dir, filename)
            created_at = os.path.getctime(file_path)
            
            # Clean up filename to extract hotel name
            base_name = filename.replace(".pdf", "")
            base_name = base_name.replace("_full_bleed_brochure", "")
            base_name = base_name.replace("_brochure", "")
            
            # Split by underscore and get hotel name
            name_parts = base_name.split("_")
            hotel_name = " ".join(name_parts)  # Join all parts with spaces
            
            logger.info(f"Processing file: {filename}")
            logger.info(f"Extracted hotel name: {hotel_name}")
            
            # Find matching exterior image
            exterior_image = None
            possible_image_names = [
                f"{base_name}_exterior.png",
                f"{hotel_name}_exterior.png",
                f"{hotel_name.replace(' ', '_')}_exterior.png",
                f"{base_name.lower()}_exterior.png",
                f"{hotel_name.lower()}_exterior.png",
                f"{hotel_name.replace(' ', '_').lower()}_exterior.png"
            ]
            
            logger.info(f"Looking for images with names: {possible_image_names}")
            
            for img_name in possible_image_names:
                img_path = os.path.join(images_dir, img_name)
                logger.info(f"Checking path: {img_path}")
                if os.path.exists(img_path):
                    exterior_image = img_name
                    logger.info(f"Found matching image: {img_name}")
                    break
            
            if not exterior_image:
                logger.warning(f"No matching image found for hotel: {hotel_name}")
            
            brochures.append({
                "id": str(len(brochures) + 1),
                "hotelName": hotel_name,
                "location": "Not specified",  # Since we don't have reliable location data
                "createdAt": created_at * 1000,  # Convert to milliseconds for JavaScript
                "filePath": filename,
                "exteriorImage": exterior_image
            })
        
        # Sort by creation time (newest first) and limit
        brochures.sort(key=lambda x: x["createdAt"], reverse=True)
        return brochures[:limit]
        
    except Exception as e:
        logger.error(f"Error getting recent brochures: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
