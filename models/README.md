# AI Model Setup Instructions

## 1. Stable Diffusion WebUI with Kohya

1. Clone the Stable Diffusion WebUI repository:
```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui
```

2. Download the Kohya model:
   - Download `last.safetensors` (or your preferred model)
   - Place it in the `models/Stable-diffusion` directory

3. Start the WebUI:
```bash
# Windows
webui-user.bat
```

The server will start at `http://127.0.0.1:7860`

## 2. Flan-T5 Model Server

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install transformers torch fastapi uvicorn
```

3. Create the model server (save as `t5_server.py`):
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

app = FastAPI()

# Load model and tokenizer
model_name = "google/flan-t5-base"  # You can use larger versions if you have more GPU memory
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

if torch.cuda.is_available():
    model = model.to("cuda")

class GenerationRequest(BaseModel):
    prompt: str
    max_length: int = 500
    temperature: float = 0.7
    top_p: float = 0.9

@app.post("/generate")
async def generate_text(request: GenerationRequest):
    try:
        # Prepare input
        inputs = tokenizer(request.prompt, return_tensors="pt", max_length=512, truncation=True)
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")

        # Generate
        outputs = model.generate(
            **inputs,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            do_sample=True
        )

        # Decode
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"generated_text": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

4. Start the Flan-T5 server:
```bash
python t5_server.py
```

The server will start at `http://localhost:8002`

## Configuration

Make sure your `application.properties` has these settings:

```properties
# Stable Diffusion Configuration
stable-diffusion.api-url=http://127.0.0.1:7860
stable-diffusion.model-name=last.safetensors

# T5 Model Configuration
t5.model.endpoint=http://localhost:8002
```

## Testing the Models

1. Test Stable Diffusion:
```bash
curl -X POST http://127.0.0.1:7860/sdapi/v1/txt2img \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful beach resort", "steps": 30}'
```

2. Test Flan-T5:
```bash
curl -X POST http://localhost:8002/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a description for a luxury hotel:", "max_length": 500}'
```
