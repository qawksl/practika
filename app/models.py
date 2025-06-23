from .extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    sur_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    telegram_id = db.Column(db.String(60), nullable=True)
    is_active = db.Column(db.Boolean, default=True,  nullable=False)

    def get_id(self):
        return str(self.id)  # Flask-Login ожидает строку
    
    def __repr__(self):
        return f'<User {self.name}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    sur_name = db.Column(db.String(120), nullable=False)
    data_of_birth = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'<Patient {self.name}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f'<Event {self.name}>'