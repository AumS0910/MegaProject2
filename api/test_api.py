import requests
import time
import os

def test_brochure_generation():
    # API endpoint
    base_url = "http://127.0.0.1:8006"
    
    # Test data
    test_data = {
        "hotel_name": "Taj Mahal Palace Hotel",
        "location": "Mumbai",
        "layout": "full_bleed"
    }
    
    try:
        # Check if API is healthy
        health_response = requests.get(f"{base_url}/health")
        print(f"Health check response: {health_response.json()}")
        
        # Submit brochure generation request
        print("\nSubmitting brochure generation request...")
        response = requests.post(f"{base_url}/generate-brochure", json=test_data)
        response_data = response.json()
        
        if response.status_code == 200:
            task_id = response_data.get("task_id")
            print(f"Task ID: {task_id}")
            
            # Poll for task status
            while True:
                status_response = requests.get(f"{base_url}/task-status/{task_id}")
                
                if status_response.headers.get("content-type") == "image/png":
                    # Save the brochure
                    with open("test_brochure.png", "wb") as f:
                        f.write(status_response.content)
                    print("\nBrochure generated successfully!")
                    print(f"Saved as: {os.path.abspath('test_brochure.png')}")
                    break
                
                status_data = status_response.json()
                print(f"\nTask status: {status_data['status']}")
                print(f"Message: {status_data['message']}")
                
                if status_data["status"] == "failed":
                    print("Brochure generation failed!")
                    break
                
                time.sleep(5)  # Wait 5 seconds before next poll
                
        else:
            print(f"Error: {response_data}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_brochure_generation()
