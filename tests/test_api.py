import unittest
import json
from unittest.mock import patch, MagicMock
from app import app, db
from models.listing import Listing
from models.photo import Photo
from models.tag import Tag
from io import BytesIO

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    @patch('api.listing_routes.save_file')
    @patch('api.listing_routes.extract_details_from_image')
    def test_create_listing(self, mock_extract_details, mock_save_file):
        # Mock save_file and extract_details_from_image
        mock_save_file.return_value = 'uploads/test.jpg'
        mock_extract_details.return_value = {
            'title': 'Vintage Leather Jacket',
            'description': 'A high-quality vintage leather jacket...',
            'category': 'Apparel > Coats & Jackets',
            'brand': 'Wilson Leathers',
            'color': 'Brown',
            'size': 'Medium',
            'condition': 'Used',
            'price': 125.00,
            'tags': ['vintage', 'leather', '80s']
        }

        data = {'photo': (BytesIO(b'my file contents'), 'test.jpg')}
        response = self.app.post('/api/listings', content_type='multipart/form-data', data=data)

        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['title'], 'Vintage Leather Jacket')
        self.assertEqual(json_response['price'], 125.00)
        self.assertIn('vintage', json_response['tags'])

    def test_get_listing(self):
        # Create a listing to test with
        with app.app_context():
            new_listing = Listing(title="Test Listing", description="Test Desc")
            db.session.add(new_listing)
            db.session.commit()
            listing_id = new_listing.id

        response = self.app.get(f'/api/listings/{listing_id}')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['title'], 'Test Listing')

    def test_update_listing(self):
        with app.app_context():
            new_listing = Listing(title="Old Title", description="Old Desc")
            db.session.add(new_listing)
            db.session.commit()
            listing_id = new_listing.id

        update_data = {'title': 'New Title', 'sku': '12345', 'price': 99.99}
        response = self.app.put(f'/api/listings/{listing_id}', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['title'], 'New Title')
        self.assertEqual(json_response['sku'], '12345')
        self.assertEqual(json_response['price'], 99.99)

    @patch('api.listing_routes.generate_backgrounds')
    def test_generate_photos(self, mock_generate_backgrounds):
        # Mock generate_backgrounds
        mock_generate_backgrounds.return_value = ['uploads/gen1.jpg', 'uploads/gen2.jpg', 'uploads/gen3.jpg']

        with app.app_context():
            new_listing = Listing(title="Test Listing", description="Test Desc")
            db.session.add(new_listing)
            db.session.commit()
            listing_id = new_listing.id
            new_photo = Photo(listing_id=listing_id, original_url='uploads/test.jpg', is_primary=True)
            db.session.add(new_photo)
            db.session.commit()

        response = self.app.post(f'/api/listings/{listing_id}/photos/generate')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        # 1 original + 3 generated
        self.assertEqual(len(json_response['photos']), 4)

    @patch('api.listing_routes.push_to_shopify')
    def test_publish_listing(self, mock_push_to_shopify):
        # Mock push_to_shopify
        mock_push_to_shopify.return_value = {'status': 'success', 'shopify_id': '12345'}

        with app.app_context():
            new_listing = Listing(title="Test Listing", description="Test Desc")
            db.session.add(new_listing)
            db.session.commit()
            listing_id = new_listing.id
            new_photo = Photo(listing_id=listing_id, original_url='uploads/test.jpg', is_primary=True)
            db.session.add(new_photo)
            db.session.commit()

        response = self.app.post(f'/api/listings/{listing_id}/publish')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['message'], f'Listing {listing_id} has been pushed to Shopify with ID 12345.')

if __name__ == '__main__':
    unittest.main()
