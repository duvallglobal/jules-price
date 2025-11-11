from app import db

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    condition = db.Column(db.String(50))
    sku = db.Column(db.String(50))
    item_weight = db.Column(db.Float)
    package_length = db.Column(db.Float)
    package_width = db.Column(db.Float)
    package_height = db.Column(db.Float)
    price = db.Column(db.Float)
    tags = db.relationship('Tag', backref='listing', lazy=True)
    photos = db.relationship('Photo', backref='listing', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'brand': self.brand,
            'color': self.color,
            'size': self.size,
            'condition': self.condition,
            'sku': self.sku,
            'item_weight': self.item_weight,
            'price': self.price,
            'package_dimensions': {
                'length': self.package_length,
                'width': self.package_width,
                'height': self.package_height
            },
            'tags': [tag.name for tag in self.tags],
            'photos': [photo.to_dict() for photo in self.photos]
        }
