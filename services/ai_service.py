import os
import json
import google.generativeai as genai
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from PIL import Image
import io
import uuid
from services.file_service import UPLOAD_FOLDER

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location="us-central1")

def extract_details_from_image(image_file):
    """
    Uses Gemini to extract product details from an image.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

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
        - "price": A suggested price for the product, as a float.
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
            'price': 0.0,
            'tags': []
        }

def generate_backgrounds(image_path):
    """
    Uses Imagen to generate new product photos with different backgrounds.
    """
    try:
        model = GenerativeModel("imagen-3")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        prompts = [
            "A professional product photo of the item on a clean, light gray background.",
            "A professional product photo of the item on a dark, textured background.",
            "A lifestyle photo of the item in a setting that matches its use. For example, if it's a jacket, show it on a mannequin in a stylish room."
        ]

        generated_images = []
        for prompt in prompts:
            response = model.generate_content(
                [Part.from_data(image_bytes, mime_type="image/jpeg"), prompt]
            )

            # Save the generated image
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(response.images[0]._image_bytes)
            generated_images.append(filepath)

        return generated_images

    except Exception as e:
        print(f"Error during image generation: {e}")
        return []
