import requests
import json
import time
from collections import deque

# Rate limiting setup
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
MAX_REQUESTS_PER_WINDOW = 100
request_timestamps = deque()

def check_rate_limit():
    current_time = time.time()
    # Remove timestamps older than the window
    while request_timestamps and current_time - request_timestamps[0] > RATE_LIMIT_WINDOW:
        request_timestamps.popleft()
    
    if len(request_timestamps) >= MAX_REQUESTS_PER_WINDOW:
        time_until_next = request_timestamps[0] + RATE_LIMIT_WINDOW - current_time
        raise Exception(f"Rate limit exceeded. Please try again in {int(time_until_next)} seconds")
    
    request_timestamps.append(current_time)

def generate_hotel_description(hotel_name, section):
    url = "http://localhost:8003/generate"  # Updated port to 8003
    
    prompts = {
        "exterior": f"Generate a detailed luxury hotel exterior description highlighting architecture and surroundings: {hotel_name} welcomes guests with",
        "room": f"Generate a luxury hotel room description focusing on comfort and amenities: The rooms at {hotel_name} offer",
        "restaurant": f"Generate a fine dining restaurant description with cuisine and atmosphere: The signature restaurant at {hotel_name} presents"
    }
    
    if section not in prompts:
        return f"Welcome to {hotel_name}'s {section} area."
    
    try:
        check_rate_limit()
        data = {
            "prompt": prompts[section],
            "max_length": 150,
            "temperature": 0.7
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get("generated_text", f"Welcome to {hotel_name}'s {section} area.")
    except Exception as e:
        print(f"Error generating {section} description:", e)
        return f"Welcome to {hotel_name}'s {section} area."

def generate_amenities(hotel_name, location):
    url = "http://localhost:8003/generate"  # T5 server endpoint
    
    # Create a context-aware prompt based on location
    prompt = f"Generate 6 unique ultra-luxury amenities for {hotel_name} in {location}. Consider the location's features, climate, and culture. Each amenity should be extraordinary and specific to this location. Format as a numbered list."
    
    try:
        check_rate_limit()
        data = {
            "prompt": prompt,
            "max_length": 200,
            "temperature": 0.8  # Slightly higher temperature for more creative results
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        generated_text = result.get("generated_text", "")
        
        # Process the amenities
        amenities = []
        for amenity in generated_text.split("\n"):
            # Clean up the amenity text
            clean_amenity = amenity.strip()
            # Remove leading numbers and dots
            clean_amenity = ' '.join(clean_amenity.split()[1:]) if clean_amenity and clean_amenity[0].isdigit() else clean_amenity
            if clean_amenity:
                amenities.append(clean_amenity)
        
        # If we didn't get enough amenities, add some premium defaults
        default_amenities = [
            "24/7 Personal Butler Service",
            "World-Class Spa & Wellness Center",
            "Private Luxury Transportation",
            "Infinity Pool with Panoramic Views",
            "Michelin-Star Fine Dining",
            "Exclusive VIP Concierge"
        ]
        
        while len(amenities) < 6:
            amenities.append(default_amenities[len(amenities)])
        
        return amenities[:6]  # Return exactly 6 amenities
        
    except Exception as e:
        print(f"Error generating amenities:", e)
        # Return default luxury amenities if generation fails
        return [
            "24/7 Personal Butler Service",
            "World-Class Spa & Wellness Center",
            "Private Luxury Transportation",
            "Infinity Pool with Panoramic Views",
            "Michelin-Star Fine Dining",
            "Exclusive VIP Concierge"
        ]

# For testing
if __name__ == "__main__":
    test_hotels = [
        ("Taj Village Resort", "Goa"),
        ("Desert Rose Palace", "Dubai"),
        ("Alpine Luxury Lodge", "Switzerland")
    ]
    
    for hotel_name, location in test_hotels:
        print(f"\nGenerating amenities for {hotel_name} in {location}:")
        print("-" * 50)
        amenities = generate_amenities(hotel_name, location)
        for i, amenity in enumerate(amenities, 1):
            print(f"{i}. {amenity}")
        print()
