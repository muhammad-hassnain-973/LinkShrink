from src.models.user import db
from datetime import datetime
import string
import random

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.Text, nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    click_count = db.Column(db.Integer, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Url {self.short_code}>'

    def to_dict(self):
        return {
            'id': self.id,
            'original_url': self.original_url,
            'short_code': self.short_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'click_count': self.click_count,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

    @staticmethod
    def generate_short_code(length=6):
        """Generate a random short code for the URL"""
        characters = string.ascii_letters + string.digits
        while True:
            short_code = ''.join(random.choice(characters) for _ in range(length))
            # Check if this code already exists
            if not Url.query.filter_by(short_code=short_code).first():
                return short_code

    def increment_click_count(self):
        """Increment the click count for this URL"""
        self.click_count += 1
        db.session.commit()

