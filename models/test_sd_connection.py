import requests
import json
import base64
from PIL import Image
import io

def test_stable_diffusion():
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    
    # Simple test payload
    payload = {
        "prompt": "a beautiful sunset on a beach",
        "negative_prompt": "low quality, blurry",
        "steps": 20,
        "width": 512,
        "height": 512,
        "cfg_scale": 7.0,
        "sampler_name": "Euler a"
    }
    
    print("Testing Stable Diffusion connection...")
    print(f"Sending request to: {url}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Image generated.")
            r = response.json()
            
            # Save the test image
            image_data = base64.b64decode(r['images'][0])
            image = Image.open(io.BytesIO(image_data))
            image.save("test_image.png")
            print("Test image saved as 'test_image.png'")
        else:
            print("Error response content:", response.text)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_stable_diffusion()
