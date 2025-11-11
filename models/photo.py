from app import db

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    original_url = db.Column(db.String(255), nullable=False)
    generated_url = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'original_url': self.original_url,
            'generated_url': self.generated_url,
            'is_primary': self.is_primary
        }
