from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import time
from typing import Optional
import logging
import requests
import base64
from PIL import Image
import io
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute in seconds
MAX_REQUESTS_PER_WINDOW = 10  # Allow 10 requests per minute
request_timestamps = []

class GenerationRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 100
    temperature: Optional[float] = 0.6
    top_p: Optional[float] = 0.8

def check_rate_limit():
    current_time = time.time()
    # Remove timestamps older than the window
    while request_timestamps and current_time - request_timestamps[0] > RATE_LIMIT_WINDOW:
        request_timestamps.pop(0)
    
    if len(request_timestamps) >= MAX_REQUESTS_PER_WINDOW:
        time_until_next = request_timestamps[0] + RATE_LIMIT_WINDOW - current_time
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Please try again in {int(time_until_next)} seconds"
        )
    
    request_timestamps.append(current_time)

def load_model():
    try:
        logger.info("Loading model and tokenizer...")
        model_path = "E:/MegaProject/Text/flan-t5-base"
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        logger.info("Model and tokenizer loaded successfully")
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

model, tokenizer = load_model()

def generate_image(prompt, negative_prompt="", width=512, height=512, steps=20):
    """Generate an image using Stable Diffusion API"""
    url = "http://127.0.0.1:7861/sdapi/v1/txt2img"
    
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "width": width,
        "height": height,
        "sampler_name": "Euler a",
        "cfg_scale": 7,
        "seed": -1
    }
    
    logger.info(f"Generating image with prompt: {prompt}")
    try:
        logger.info(f"Sending request to Stable Diffusion API at {url}")
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
        logger.info(f"Got response with status code: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"Stable Diffusion API returned status code {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        r = response.json()
        if 'images' not in r or not r['images']:
            error_msg = f"No images in response. Full response: {json.dumps(r, indent=2)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        image_data = base64.b64decode(r['images'][0])
        image = Image.open(io.BytesIO(image_data))
        logger.info("Successfully generated and decoded image")
        return image
        
    except requests.exceptions.ConnectionError as e:
        error_msg = "Could not connect to Stable Diffusion API. Make sure it's running on http://127.0.0.1:7861"
        logger.error(error_msg)
        raise Exception(error_msg) from e
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def create_pdf(text, image_path):
    # TO DO: implement PDF creation
    pass

@app.post("/generate")
async def generate_text(request: GenerationRequest):
    try:
        # Check rate limit
        check_rate_limit()
        
        # Process the prompt to handle bullet points
        processed_prompt = request.prompt.replace('\n', ' ').replace('- ', ', ').strip()
        
        # Tokenize and generate
        inputs = tokenizer(processed_prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=request.max_length,
                temperature=request.temperature,
                top_p=request.top_p,
                num_return_sequences=1,
                do_sample=True,  # Enable sampling
                no_repeat_ngram_size=3,  # Avoid repetition
                length_penalty=1.5  # Encourage longer responses
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-process the generated text
        generated_text = generated_text.replace(" .", ".").replace(" ,", ",")
        generated_text = " ".join(generated_text.split())  # Clean up whitespace
        
        return {"generated_text": generated_text}
    
    except HTTPException as he:
        # Re-raise HTTP exceptions (like rate limit)
        raise
    except Exception as e:
        logger.error(f"Error during text generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@app.post("/generate_brochure")
async def generate_brochure(content: str):
    try:
        logger.info(f"Starting brochure generation for content: {content}")
        
        # Generate text content using T5
        request = GenerationRequest(prompt=content)
        generated_text = (await generate_text(request))["generated_text"]
        logger.info("Successfully generated text content")
        
        # Generate image based on the content
        image_prompt = f"professional brochure image for: {content}, high quality, photorealistic"
        image = generate_image(
            prompt=image_prompt,
            negative_prompt="text, watermark, bad quality, blurry, cartoon, drawing",
            width=800,
            height=600,
            steps=30
        )
        
        if image:
            # Create static directory if it doesn't exist
            os.makedirs("static", exist_ok=True)
            
            # Save the image
            image_path = "static/generated_image.png"
            image.save(image_path)
            logger.info(f"Saved generated image to {image_path}")
            
            # Create PDF with both text and image
            create_pdf(generated_text, image_path)
            logger.info("Successfully created PDF")
            
            return {"status": "success", "message": "Brochure generated successfully"}
        else:
            error_msg = "Failed to generate image"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
            
    except Exception as e:
        logger.error(f"Error in generate_brochure: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)