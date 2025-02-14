# AI Brochure Generation System

A microservices-based system for generating AI-powered hotel brochures using T5 for text generation and Stable Diffusion for image generation.

## Services

The system consists of three main services:

1. **T5 Text Generation Server (Port 8003)**
   - Generates dynamic descriptions for hotels
   - Uses flan-t5-base model
   - Rate limited to prevent overload

2. **Stable Diffusion API (Port 7860)**
   - Generates realistic hotel images
   - Customizable prompts
   - High-quality output

3. **Brochure Generation API (Port 8004)**
   - Coordinates the brochure generation process
   - Handles async tasks
   - Provides status tracking
   - CORS enabled for frontend integration

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start all services:
   ```bash
   start_services.bat
   ```

3. Test the API:
   ```bash
   python api/test_api.py
   ```

## API Endpoints

### Generate Brochure
```http
POST /generate-brochure
Content-Type: application/json

{
    "hotel_name": "Hotel Name",
    "location": "Location",
    "layout": "full_bleed"
}
```

### Check Task Status
```http
GET /task-status/{task_id}
```

### Health Check
```http
GET /health
```

## Integration with Frontend

Make HTTP requests to `http://localhost:8004/generate-brochure` with the required parameters. The API will return a task ID that can be used to track the generation progress.

## Directory Structure
```
AI-brochure-generation/
├── api/
│   ├── brochure_api.py
│   ├── models.py
│   └── test_api.py
├── models/
│   ├── generate_single_page_brochure.py
│   ├── t5_server.py
│   └── test_image_generation.py
├── requirements.txt
└── start_services.bat
```

## Error Handling

The API includes comprehensive error handling and logging:
- All errors are logged to `api.log`
- Failed tasks include detailed error messages
- Background task status tracking

## Notes

- The T5 model requires approximately 2GB of RAM
- Stable Diffusion requires a GPU for optimal performance
- Generated brochures are saved in the `generated_brochures` directory
- Generated images are saved in the `generated_images` directory
