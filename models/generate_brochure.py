import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_t5_server import generate_hotel_description, generate_amenities
from test_image_generation import test_image_generation

class BrochureGenerator:
    def __init__(self, hotel_name, location):
        self.hotel_name = hotel_name
        self.location = location
        self.font_title = ImageFont.truetype("arial.ttf", 60)
        self.font_heading = ImageFont.truetype("arial.ttf", 40)
        self.font_text = ImageFont.truetype("arial.ttf", 30)
        
    def add_text_to_image(self, image, text, position, font, color=(255, 255, 255), max_width=30):
        draw = ImageDraw.Draw(image)
        
        # Add semi-transparent black rectangle behind text for readability
        text_lines = textwrap.wrap(text, width=max_width)
        line_height = font.getbbox('hg')[3] + 10  # Using getbbox instead of deprecated getsize
        text_height = len(text_lines) * line_height
        rect_padding = 20
        
        # Draw background rectangle
        rect_coords = [
            position[0] - rect_padding,
            position[1] - rect_padding,
            position[0] + 800,  # Adjust width as needed
            position[1] + text_height + rect_padding
        ]
        draw.rectangle(rect_coords, fill=(0, 0, 0, 128))
        
        # Draw text
        y = position[1]
        for line in text_lines:
            draw.text((position[0], y), line, font=font, fill=color)
            y += line_height
            
    def create_page(self, image_path, title, description):
        # Open and resize image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Resize maintaining aspect ratio
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            
            # Add title
            self.add_text_to_image(img, title, (50, 50), self.font_heading)
            
            # Add description
            self.add_text_to_image(img, description, (50, 150), self.font_text)
            
            return img
            
    def generate_brochure(self):
        print("Generating text content...")
        # Generate text descriptions using the local function
        descriptions = {
            'exterior': generate_hotel_description(self.hotel_name, "exterior"),
            'room': generate_hotel_description(self.hotel_name, "room"),
            'restaurant': generate_hotel_description(self.hotel_name, "restaurant")
        }
        
        # Generate amenities
        amenities = generate_amenities(self.hotel_name, self.location)
        
        print("\nGenerating images...")
        # Generate images
        test_image_generation(self.hotel_name, self.location)
        
        print("\nCreating brochure pages...")
        pages = []
        image_types = ['exterior', 'room', 'restaurant']
        
        # Create output directory if it doesn't exist
        output_dir = "generated_brochures"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create each page
        for img_type in image_types:
            image_path = f"generated_images/{self.hotel_name}_{img_type}.png"
            if os.path.exists(image_path):
                title = f"{img_type.title()} View"
                description = descriptions[img_type] if img_type in descriptions else f"Welcome to {self.hotel_name}'s {img_type} area."
                page = self.create_page(image_path, title, description)
                pages.append(page)
        
        # Create amenities page
        amenities_page = Image.new('RGB', (1920, 1080), color='black')
        self.add_text_to_image(amenities_page, "LUXURY AMENITIES", (50, 50), self.font_heading)
        
        # Add each amenity with bullet points
        y_position = 150
        for amenity in amenities:
            self.add_text_to_image(amenities_page, f"• {amenity}", (50, y_position), self.font_text)
            y_position += 100
        
        pages.append(amenities_page)
        
        # Save individual pages and combined PDF
        for i, page in enumerate(pages):
            # Save individual pages
            page_path = f"{output_dir}/{self.hotel_name}_page_{i+1}.png"
            page.save(page_path, "PNG")
            print(f"Saved page {i+1} as {page_path}")
        
        print("\nBrochure generation complete!")
        return pages

def main():
    # Example usage
    hotel_name = "Ocean Paradise Resort"
    location = "Maldives"
    
    print(f"Generating brochure for {hotel_name} in {location}")
    generator = BrochureGenerator(hotel_name, location)
    generator.generate_brochure()

if __name__ == "__main__":
    main()
