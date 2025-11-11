import os
import json
import google.generativeai as genai
from vertexai.preview.generative_models import Part
from PIL import Image
import io
import uuid
from services.file_service import UPLOAD_FOLDER

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_details_from_image(image_file):
    """
    Uses Gemini to extract product details from an image, with Google Search grounding.
    """
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-latest',
            tools=['google_search']
        )

        # Open the image file
        image = Image.open(image_file)

        prompt = """
        You are an expert e-commerce merchandiser. Analyze the product in this image.
        Use Google Search to find similar products and determine a competitive price.
        Return a JSON object with the following details.
        Your response should be only the JSON object, with no other text or formatting.

        - "title": A compelling and descriptive title for the product.
        - "description": A detailed and appealing product description.
        - "category": The most appropriate e-commerce category (e.g., "Apparel > Coats & Jackets").
        - "brand": The brand of the product, if visible or identifiable. If not, use "Unbranded".
        - "color": The primary color of the product.
        - "size": The size of the product, if visible. If not, use "Not specified".
        - "condition": The condition of the aproduct (e.g., "New", "Used", "Vintage").
        - "price": A suggested price for the product, as a float, based on your research.
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
    Uses Gemini to generate new product photos with different backgrounds.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-image')

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        prompts = [
            """<image_variants>
                <variant id="1" name="Lighter Gradient E-commerce Photo">
                    <goal>Clean, soft, professional look.</goal>
                    <prompt>
                        Transform the product in the original photo into a high-resolution, professional e-commerce studio photograph.
                        Remove the existing background entirely and replace it with a smooth, white-to-light-grey radial gradient.
                        Ensure accurate, realistic reflections on any glossy or metallic surfaces.
                        Apply soft, evenly distributed studio lighting to eliminate harsh shadows while maintaining true texture and material detail.
                        The product must be perfectly centered, sharply focused, and color-accurate.
                        Important: The AI is strictly prohibited from modifying the physical structure, proportions, or components of the product.
                        No alterations, additions, or removals that change the product’s physical state are allowed.
                    </prompt>
                </variant>
            </image_variants>""",
            """<image_variants>
                <variant id="2" name="Darker Gradient E-commerce Photo">
                    <goal>Rich, contrasting, premium look.</goal>
                    <prompt>
                        Transform the product in the original photo into a high-resolution, premium e-commerce studio photograph.
                        Remove the existing background entirely and replace it with a dark, charcoal-to-black radial gradient.
                        Use precise studio lighting to create balanced highlights and professional rim lighting that emphasizes the product’s shape and contours.
                        Ensure realistic reflections and surface textures for a lifelike, high-contrast finish.
                        The product should be perfectly centered, color-accurate, and crisply detailed.
                        Important: The AI is strictly prohibited from altering the physical form, structure, or any attached elements of the product.
                        It must not add, remove, or modify any parts that would change the product’s physical state.
                    </prompt>
                </variant>
            </image_variants>""",
            """<image_variants>
                <variant id="3" name="Lifestyle Photo">
                    <goal>Contextual and aspirational use of the product.</goal>
                    <prompt>
                        Create a realistic, high-resolution lifestyle photograph using the context, lighting, and environment suggested by the original image.
                        The result should appear natural and believable, maintaining realistic reflections, shadows, and material details consistent with the product’s setting.
                        Ensure that the product remains the clear focal point, accurately rendered, and visually integrated into the surrounding environment.
                        Important: The AI is strictly prohibited from changing the physical characteristics, shape, or design of the product.
                        It must not add, remove, or alter any physical components or features in any way.
                    </prompt>
                </variant>
            </image_variants>"""
        ]

        generated_images = []
        for prompt in prompts:
            response = model.generate_content(
                [prompt, Part.from_data(image_bytes, mime_type="image/jpeg")]
            )

            # Save the generated image
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(response.parts[0].data)
            generated_images.append(filepath)

        return generated_images

    except Exception as e:
        print(f"Error during image generation: {e}")
        return []
