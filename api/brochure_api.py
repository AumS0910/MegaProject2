from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
import os
import re
import logging
from pathlib import Path
import time
from typing import Optional
import json
from pydantic import BaseModel

# Add the parent directory to sys.path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from models.generate_single_page_brochure import SinglePageBrochureGenerator
from api.models import BrochureRequest, BrochureResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Brochure Generation API",
    description="API for generating hotel brochures using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories if they don't exist
os.makedirs("generated_images", exist_ok=True)
os.makedirs("generated_brochures", exist_ok=True)

# Mount directories for static files
app.mount("/images", StaticFiles(directory="generated_images"), name="images")
app.mount("/brochures", StaticFiles(directory="generated_brochures", html=True), name="brochures")

# Add response headers middleware for PDF files
@app.middleware("http")
async def add_pdf_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/brochures") and request.url.path.endswith(".pdf"):
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "inline"
    return response

# Store background tasks status
tasks_status = {}

class PromptRequest(BaseModel):
    prompt: str

def extract_hotel_info(prompt: str) -> dict:
    """Extract hotel name and location from the prompt using simple pattern matching."""
    logger.info(f"\nExtracting hotel info from prompt: {prompt}")
    try:
        # Common patterns in prompts
        patterns = [
            r"(?i)generate.*?(?:brochure|flyer).*?for\s+(.*?)\s+in\s+(.*?)(?:\.|$|\s)",
            r"(?i)create.*?(?:brochure|flyer).*?for\s+(.*?)\s+in\s+(.*?)(?:\.|$|\s)",
            r"(?i)make.*?(?:brochure|flyer).*?for\s+(.*?)\s+in\s+(.*?)(?:\.|$|\s)",
        ]
        
        logger.info(f"Trying {len(patterns)} patterns...")
        for i, pattern in enumerate(patterns):
            logger.info(f"Trying pattern {i+1}: {pattern}")
            match = re.search(pattern, prompt)
            if match:
                hotel_name = match.group(1).strip()
                location = match.group(2).strip()
                logger.info(f"Match found! Hotel: {hotel_name}, Location: {location}")
                return {
                    "hotel_name": hotel_name,
                    "location": location,
                    "layout": "full_bleed"  # Default layout as requested
                }
        
        logger.info("No pattern matched, trying fallback method...")
        # Fallback: Try to find any capitalized words for hotel name
        words = prompt.split()
        logger.info(f"Split words: {words}")
        capitalized_words = []
        location_words = []
        found_in = False
        
        for i, word in enumerate(words):
            logger.info(f"Processing word {i}: {word}")
            if word.lower() == "in" and i < len(words) - 1:
                logger.info(f"Found 'in' at position {i}")
                found_in = True
                continue
            if found_in:
                location_words.append(word)
            elif word[0].isupper():
                capitalized_words.append(word)
        
        logger.info(f"Capitalized words: {capitalized_words}")
        logger.info(f"Location words: {location_words}")
        
        if capitalized_words and location_words:
            result = {
                "hotel_name": " ".join(capitalized_words),
                "location": " ".join(location_words),
                "layout": "full_bleed"
            }
            logger.info(f"Fallback method succeeded: {result}")
            return result
        
        logger.info("Could not extract hotel information")
        raise ValueError("Could not extract hotel information from prompt")
        
    except Exception as e:
        logger.error(f"Error in extract_hotel_info: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise ValueError("Could not understand the prompt. Please try rephrasing it.")

def generate_brochure_task(task_id: str, request: BrochureRequest):
    try:
        logger.info(f"Starting brochure generation task {task_id} for {request.hotel_name}")
        tasks_status[task_id] = {"status": "processing", "message": "Generating brochure..."}
        
        # Initialize the brochure generator
        generator = SinglePageBrochureGenerator(
            hotel_name=request.hotel_name,
            location=request.location,
            layout=request.layout
        )
        
        # Generate the brochure
        generator.generate_brochure()
        
        # Update task status
        brochure_filename = f"{request.hotel_name}_full_bleed_brochure.png"
        brochure_path = os.path.join("generated_brochures", brochure_filename)
        
        if os.path.exists(brochure_path):
            tasks_status[task_id] = {
                "status": "completed",
                "message": "Brochure generated successfully",
                "file_path": brochure_path
            }
        else:
            tasks_status[task_id] = {
                "status": "failed",
                "message": "Failed to generate brochure"
            }
            
    except Exception as e:
        logger.error(f"Error in task {task_id}: {str(e)}")
        tasks_status[task_id] = {
            "status": "failed",
            "message": str(e)
        }

@app.post("/generate-brochure")
async def generate_brochure(request: BrochureRequest):
    try:
        # Create response object for streaming updates
        response = {
            "status": "generating",
            "message": "Starting brochure generation process",
            "progress": 0
        }
        
        # Update progress: Starting image generation
        response.update({
            "message": "Generating AI images for your hotel...",
            "progress": 20
        })
        
        # Initialize brochure generator
        generator = SinglePageBrochureGenerator(
            hotel_name=request.hotel_name,
            location=request.location,
            layout=request.layout
        )
        
        # Update progress: Images generated
        response.update({
            "message": "AI images generated successfully. Creating brochure layout...",
            "progress": 60
        })
        
        # Generate brochure
        brochure = generator.generate_brochure()
        
        if brochure:
            # Get the file path
            file_path = f"generated_brochures/{request.hotel_name}_{request.layout}_brochure.pdf"
            
            # Update progress: Brochure completed
            response.update({
                "status": "completed",
                "message": "Brochure generated successfully!",
                "progress": 100,
                "file_path": file_path
            })
            
            return response
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate brochure"
            )
            
    except Exception as e:
        logger.error(f"Error generating brochure: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating brochure: {str(e)}"
        )

@app.post("/generate-brochure-from-prompt")
async def generate_brochure_from_prompt(request: PromptRequest):
    print("\n=== Generate Brochure From Prompt ===")
    print(f"Raw request data: {request}")
    print(f"Request type: {type(request)}")
    print(f"Request dict: {request.dict()}")
    print(f"Prompt: {request.prompt}")
    print(f"Prompt type: {type(request.prompt)}")
    
    logger.info(f"\nReceived prompt request: {request.prompt}")
    try:
        # Extract hotel information from prompt
        print("\nExtracting hotel info...")
        hotel_info = extract_hotel_info(request.prompt)
        print(f"Extracted hotel info: {hotel_info}")
        
        # Initialize brochure generator
        print(f"\nInitializing brochure generator...")
        print(f"Hotel name: {hotel_info['hotel_name']}")
        print(f"Location: {hotel_info['location']}")
        generator = SinglePageBrochureGenerator(
            hotel_name=hotel_info['hotel_name'],
            location=hotel_info['location']
        )
        
        # Generate images first
        print("\nStarting image generation...")
        try:
            generator.generate_images()
            print("Image generation completed successfully")
        except Exception as img_error:
            logger.error(f"Error during image generation: {str(img_error)}")
            logger.error(f"Error type: {type(img_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate images: {str(img_error)}"
            )
        
        # Generate brochure
        print("\nStarting brochure generation...")
        try:
            brochure = generator.generate_brochure()
            print("Brochure generation completed successfully")
        except Exception as brochure_error:
            logger.error(f"Error during brochure generation: {str(brochure_error)}")
            logger.error(f"Error type: {type(brochure_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate brochure: {str(brochure_error)}"
            )
        
        if brochure:
            # Get safe filenames
            safe_hotel_name = hotel_info['hotel_name'].replace(' ', '_')
            brochure_filename = f"{safe_hotel_name}_full_bleed_brochure.pdf"
            
            # Log file paths
            print(f"\nFile paths:")
            print(f"Brochure path: generated_brochures/{brochure_filename}")
            print(f"Checking if file exists: {os.path.exists(os.path.join('generated_brochures', brochure_filename))}")
            
            # Get image paths for frontend
            image_paths = {
                "exterior": f"{safe_hotel_name}_exterior.png",
                "room": f"{safe_hotel_name}_room.png",
                "restaurant": f"{safe_hotel_name}_restaurant.png"
            }
            print(f"Image paths: {image_paths}")
            
            response_data = {
                "status": "completed",
                "message": "Brochure generated successfully",
                "progress": 100,
                "file_path": brochure_filename,  # Changed this to just the filename
                "images": image_paths
            }
            print(f"Response data: {response_data}")
            return response_data
        else:
            print("Brochure generation failed - no brochure returned")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate brochure"
            )
            
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        logger.error(f"Error type: {type(ve)}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating brochure: {str(e)}"
        )

@app.get("/brochures/{filename}")
async def get_brochure(filename: str):
    try:
        brochure_path = os.path.join("generated_brochures", filename)
        if not os.path.exists(brochure_path):
            raise HTTPException(status_code=404, detail="Brochure not found")
        
        return FileResponse(
            brochure_path,
            media_type="application/pdf",
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error serving brochure {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images/{filename}")
async def get_image(filename: str):
    try:
        image_path = os.path.join("generated_images", filename)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(
            image_path,
            media_type="image/png",
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(tasks_status[task_id])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8006)
