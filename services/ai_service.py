import os
import json
import google.generativeai as genai
from PIL import Image
import io
import uuid
from services.file_service import UPLOAD_FOLDER

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_details_from_image(image_file):
    """
    Uses Gemini to extract product details from an image.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-latest')

        # Open the image file
        image = Image.open(image_file)

        prompt = """
        You are an expert e-commerce merchandiser. Analyze the product in this image and return a JSON object with the following details.
        Your response should be only the JSON object, with no other text or formatting.

        - "title": A compelling and descriptive title for the product.
        - "description": A detailed and appealing product description.
        - "category": The most appropriate e-commerce category (e.g., "Apparel > Coats & Jackets").
        - "brand": The brand of the product, if visible or identifiable. If not, use "Unbranded".
        - "color": The primary color of the product.
        - "size": The size of the product, if visible. If not, use "Not specified".
        - "condition": The condition of the aproduct (e.g., "New", "Used", "Vintage").
        - "tags": An array of 3-5 relevant keywords for search.
        """

        response = model.generate_content([prompt, image])

        # Clean up the response and parse the JSON
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        details = json.loads(cleaned_response)

        return details

    except Exception as e:
        print(f"Error calling Gemini API for detail extraction: {e}")
        # Return a default error structure if the API fails
        return {
            'title': 'Unable to generate title',
            'description': 'An error occurred while analyzing the image.',
            'category': 'Uncategorized',
            'brand': 'Unknown',
            'color': 'Unknown',
            'size': 'Unknown',
            'condition': 'Unknown',
            'tags': []
        }

def generate_backgrounds(image_path):
    """
    Uses an image generation model to create new product photos.
    """
    try:
        # This is a placeholder for a real image generation model.
        # In a real application, you would use a library like google-cloud-aiplatform
        # to call a model like Imagen.

        generated_images = []
        for i in range(3):
            # Create a dummy image
            img = Image.new('RGB', (600, 600), color = 'red')
            # Save the dummy image to a unique path
            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            img.save(filepath)
            generated_images.append(filepath)

        return generated_images

    except Exception as e:
        print(f"Error during image generation: {e}")
        return []
