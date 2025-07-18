from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    registered_on = db.Column(db.Date, default=datetime.utcnow)