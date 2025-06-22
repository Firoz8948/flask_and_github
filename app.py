from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import random

from models import db, User  # Import db and User from models.py

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Register the app with the db

def generate_unique_code():
    while True:
        code = str(random.randint(1000, 9999))
        if not User.query.filter_by(code=code).first():
            return code

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        pack_name = request.form['pack_name']
        amount = float(request.form['amount'])
        validity_days = int(request.form['validity_days'])
        code = generate_unique_code()
        expiry = datetime.now() + timedelta(days=validity_days)
        user = User(code=code, name=name, age=age, pack_name=pack_name, amount=amount,
                    validity_days=validity_days, expiry=expiry)
        db.session.add(user)
        db.session.commit()
        return render_template('register_success.html', code=code, expiry=expiry.strftime('%Y-%m-%d'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form['code']
        user = User.query.filter_by(code=code).first()
        if user:
            now = datetime.now()
            days_left = (user.expiry - now).days
            if days_left < 0:
                return render_template('expired.html')
            return render_template('welcome.html', name=user.name, expiry=user.expiry.strftime('%Y-%m-%d'), days_left=days_left)
        else:
            flash("Invalid code. Please try again.")
            return redirect(url_for('login'))
    return render_template('login.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)