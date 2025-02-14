# test_trifold.py

from models.generate_single_page_brochure import SinglePageBrochureGenerator



def test_trifold_layout():
    hotel_name = "Mayan Beach Club"
    location = "Goa, India"
    layout = "trifold"  # Specify the trifold layout

    # Create a brochure generator instance
    generator = SinglePageBrochureGenerator(hotel_name, location, layout)

    # Generate the brochure
    png_path, pdf_path = generator.generate_brochure()

    # Check if files were created successfully
    assert os.path.exists(png_path), "PNG brochure was not created."
    assert os.path.exists(pdf_path), "PDF brochure was not created."
    print("Trifold layout test passed!")

if __name__ == "__main__":
    test_trifold_layout()