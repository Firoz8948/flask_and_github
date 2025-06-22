from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    pack_name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    validity_days = db.Column(db.Integer, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)