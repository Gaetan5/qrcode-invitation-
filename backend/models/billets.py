from flask_sqlalchemy import SQLAlchemy
from validate_email import validate_email
import uuid
from datetime import datetime


db = SQLAlchemy()

class Billet(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, email):
        if not validate_email(email):
            raise ValueError("Invalid email address")
        
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email

    def to_json(self):
        return {
        "id": self.id,
        "name": self.name,
        "email": self.email,
        "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Billet {self.id}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Billet.query.all()
    
    @staticmethod
    def get_by_id(id):
        return Billet.query.get(id)
    
    @staticmethod
    def get_by_email(email):
        return Billet.query.filter_by(email=email).first()

    @staticmethod
    def get_by_name(name):
        return Billet.query.filter_by(name=name).first()
    
    @staticmethod
    def get_by_name_and_email(name, email):
        return Billet.query.filter_by(name=name, email=email).first()
    
    @staticmethod
    def delete_all():
        Billet.query.delete()
        db.session.commit()
    
    @staticmethod
    def count():
        return Billet.query.count()
