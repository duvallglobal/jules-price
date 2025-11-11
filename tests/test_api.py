import unittest
import json
from app import app, db
from models.listing import Listing
from models.photo import Photo
from models.tag import Tag

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

    def test_create_listing(self):
        # We'll need to simulate a file upload for the 'photo' field
        from io import BytesIO
        data = {
            'photo': (BytesIO(b'my file contents'), 'test.jpg')
        }
        response = self.app.post('/api/listings', content_type='multipart/form-data', data=data)
        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['title'], 'Vintage Leather Jacket')
        self.assertIn('vintage', json_response['tags'])
        self.assertEqual(len(json_response['photos']), 1)

    def test_get_listing(self):
        # First, create a listing to get
        from io import BytesIO
        data = {'photo': (BytesIO(b'my file contents'), 'test.jpg')}
        self.app.post('/api/listings', content_type='multipart/form-data', data=data)

        response = self.app.get('/api/listings/1')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['id'], 1)

    def test_update_listing(self):
        # Create a listing to update
        from io import BytesIO
        data = {'photo': (BytesIO(b'my file contents'), 'test.jpg')}
        self.app.post('/api/listings', content_type='multipart/form-data', data=data)

        update_data = {'title': 'New Title', 'sku': '12345'}
        response = self.app.put('/api/listings/1', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['title'], 'New Title')
        self.assertEqual(json_response['sku'], '12345')

    def test_generate_photos(self):
        # Create a listing
        from io import BytesIO
        data = {'photo': (BytesIO(b'my file contents'), 'test.jpg')}
        self.app.post('/api/listings', content_type='multipart/form-data', data=data)

        response = self.app.post('/api/listings/1/photos/generate')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        # 1 original photo + 3 generated photos
        self.assertEqual(len(json_response['photos']), 4)

    def test_publish_listing(self):
        # Create a listing
        from io import BytesIO
        data = {'photo': (BytesIO(b'my file contents'), 'test.jpg')}
        self.app.post('/api/listings', content_type='multipart/form-data', data=data)

        response = self.app.post('/api/listings/1/publish')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['message'], 'Listing 1 has been pushed to Shopify.')

if __name__ == '__main__':
    unittest.main()
