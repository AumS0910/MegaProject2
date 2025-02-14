import requests
import json
import base64
from PIL import Image
import io

def test_sd_api():
    url = "http://127.0.0.1:7861/sdapi/v1/txt2img"  # Changed port from 7860 to 7861
    
    payload = {
        "prompt": "exterior of a modern restaurant, professional photo, high quality",
        "negative_prompt": "blurry, bad quality",
        "steps": 20,
        "width": 512,
        "height": 512,
        "sampler_name": "Euler a",
        "cfg_scale": 7,
        "seed": -1
    }
    
    print(f"Sending request to Stable Diffusion API at {url}")
    try:
        response = requests.post(url, json=payload)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return
            
        r = response.json()
        if 'images' not in r or not r['images']:
            print("No images in response")
            print(f"Full response: {json.dumps(r, indent=2)}")
            return
            
        image_data = base64.b64decode(r['images'][0])
        
        # Save the image
        image = Image.open(io.BytesIO(image_data))
        image.save("test_output.png")
        print("Image generated successfully and saved as 'test_output.png'")
        
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the Stable Diffusion API")
        print("Please make sure the API is running on http://127.0.0.1:7861")
        print("Check if the start_sd_api.bat script is running")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sd_api()
