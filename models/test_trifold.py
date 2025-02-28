from models.generate_single_page_brochure import SinglePageBrochureGenerator

def test_trifold_layout():
    # Create a brochure generator with a different hotel
    generator = SinglePageBrochureGenerator(
        hotel_name="Sunset Paradise Resort",
        location="Manali",
        layout='trifold'
    )
    
    # Generate custom amenities to test flexibility
    custom_amenities = [
        ("Luxury Suites", "Experience unparalleled comfort in our oceanfront suites with private balconies and panoramic views."),
        ("Beachfront Dining", "Savor exquisite cuisine at our signature restaurants, featuring local and international flavors."),
        ("Wellness Sanctuary", "Rejuvenate your body and soul in our world-class spa with traditional Balinese treatments.")
    ]
    
    # Set custom amenities
    generator.amenities = custom_amenities
    
    # Generate the brochure
    png_path, pdf_path = generator.generate_brochure()
    
    if png_path and pdf_path:
        print("\nSuccess! Generated files:")
        print(f"PNG: {png_path}")
        print(f"PDF: {pdf_path}")
    else:
        print("\nFailed to generate brochure")

if __name__ == "__main__":
    test_trifold_layout()
