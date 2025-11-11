from flask import Blueprint, request, jsonify
from app import db
from models.listing import Listing
from models.photo import Photo
from models.tag import Tag
from services.ai_service import extract_details_from_image, generate_backgrounds

listing_bp = Blueprint('listing_bp', __name__)

@listing_bp.route('/api/listings', methods=['POST'])
def create_listing():
    # For now, we'll simulate an image upload
    # In a real app, you'd handle the file from request.files
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo uploaded'}), 400

    image = request.files['photo']

    # Use the mock AI service to get details
    details = extract_details_from_image(image)

    new_listing = Listing(
        title=details['title'],
        description=details['description'],
        category=details['category'],
        brand=details['brand'],
        color=details['color'],
        size=details['size'],
        condition=details['condition']
    )

    db.session.add(new_listing)
    db.session.commit()

    # Add tags
    for tag_name in details['tags']:
        new_tag = Tag(name=tag_name, listing_id=new_listing.id)
        db.session.add(new_tag)

    # Add photo
    # In a real app, you would save the photo and get a URL
    new_photo = Photo(listing_id=new_listing.id, original_url='https://placehold.co/600x600/ccc/000?text=Uploaded', is_primary=True)
    db.session.add(new_photo)

    db.session.commit()

    return jsonify(new_listing.to_dict()), 201

@listing_bp.route('/api/listings/<int:id>', methods=['GET'])
def get_listing(id):
    listing = Listing.query.get_or_404(id)
    return jsonify(listing.to_dict())

@listing_bp.route('/api/listings/<int:id>', methods=['PUT'])
def update_listing(id):
    listing = Listing.query.get_or_404(id)
    data = request.get_json()

    listing.title = data.get('title', listing.title)
    listing.description = data.get('description', listing.description)
    listing.category = data.get('category', listing.category)
    listing.brand = data.get('brand', listing.brand)
    listing.color = data.get('color', listing.color)
    listing.size = data.get('size', listing.size)
    listing.condition = data.get('condition', listing.condition)
    listing.sku = data.get('sku', listing.sku)
    listing.item_weight = data.get('item_weight', listing.item_weight)

    if 'package_dimensions' in data:
        listing.package_length = data['package_dimensions'].get('length', listing.package_length)
        listing.package_width = data['package_dimensions'].get('width', listing.package_width)
        listing.package_height = data['package_dimensions'].get('height', listing.package_height)

    db.session.commit()

    return jsonify(listing.to_dict())

@listing_bp.route('/api/listings/<int:id>/publish', methods=['POST'])
def publish_listing(id):
    listing = Listing.query.get_or_404(id)
    # In a real app, you'd have logic here to push to Shopify
    print(f"Publishing listing {listing.id} to Shopify...")
    return jsonify({'message': f'Listing {listing.id} has been pushed to Shopify.'})

@listing_bp.route('/api/listings/<int:id>/photos/generate', methods=['POST'])
def generate_photos(id):
    listing = Listing.query.get_or_404(id)
    primary_photo = next((p for p in listing.photos if p.is_primary), None)

    if not primary_photo:
        return jsonify({'error': 'No primary photo found for this listing'}), 404

    generated_urls = generate_backgrounds(primary_photo.original_url)

    # Remove old generated photos
    for photo in listing.photos:
        if photo.generated_url:
            db.session.delete(photo)

    for url in generated_urls:
        new_photo = Photo(listing_id=listing.id, original_url=primary_photo.original_url, generated_url=url)
        db.session.add(new_photo)

    db.session.commit()

    return jsonify(listing.to_dict())
