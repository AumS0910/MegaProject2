from models.generate_single_page_brochure import SinglePageBrochureGenerator

def test_brochures():
    # Test cases with different hotels using full_bleed layout
    test_cases = [
        {
            "hotel_name": "Tropical Paradise Resort",
            "location": "Bora Bora",
            "layout": "full_bleed"
        },
        {
            "hotel_name": "Ancient City Palace Hotel",
            "location": "Jaipur, India",
            "layout": "full_bleed"
        },
        {
            "hotel_name": "Northern Lights Lodge",
            "location": "Iceland",
            "layout": "full_bleed"
        },
        {
            "hotel_name": "Cherry Blossom Inn",
            "location": "Kyoto, Japan",
            "layout": "full_bleed"
        }
    ]
    
    for case in test_cases:
        try:
            print(f"\nGenerating brochure for {case['hotel_name']}...")
            
            # Create generator instance
            generator = SinglePageBrochureGenerator(
                hotel_name=case['hotel_name'],
                location=case['location'],
                layout=case['layout']
            )
            
            # Generate brochure
            generator.generate_brochure()
            print(f"Successfully generated brochure for {case['hotel_name']}!")
            
        except Exception as e:
            print(f"Error generating brochure for {case['hotel_name']}: {str(e)}")
            # Add a delay if we hit rate limits
            import time
            time.sleep(5)

if __name__ == "__main__":
    test_brochures()
