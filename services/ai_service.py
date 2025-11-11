import random

def extract_details_from_image(image):
    """
    Mock function to extract product details from an image.
    In a real implementation, this would involve a call to a computer vision AI.
    """
    return {
        'title': 'Vintage Leather Jacket',
        'description': 'A high-quality vintage leather jacket from the 1980s. Well-preserved with minimal wear. Features a classic design with a durable zipper and two side pockets.',
        'category': 'Apparel > Coats & Jackets',
        'brand': 'Wilson Leathers',
        'color': 'Brown',
        'size': 'Medium',
        'condition': 'Used',
        'tags': ['vintage', 'leather', '80s', 'jacket']
    }

def generate_backgrounds(image_url):
    """
    Mock function to generate new photos with different backgrounds.
    In a real implementation, this would call an image generation AI.
    """
    backgrounds = [
        'https://placehold.co/600x600/e0e0e0/000000?text=Light+Background',
        'https://placehold.co/600x600/333333/ffffff?text=Dark+Background',
        'https://placehold.co/600x600/f0f0f0/000000?text=Lifestyle+Scene'
    ]
    return random.sample(backgrounds, 3)
