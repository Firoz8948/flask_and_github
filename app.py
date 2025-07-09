from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, User
# from datetime import datetime
from datetime import datetime
import random
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gymuser:347690%40Fk@localhost:5432/gymdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

# Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    plan_name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

def generate_unique_code():
    while True:
        code = str(random.randint(1000, 9999))
        if not User.query.filter_by(code=code).first():
            return code

# @app.before_first_request
# def create_tables():
#     db.create_all()

@app.before_request
def create_tables():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        plan_name = request.form['plan_name']
        amount = request.form['amount']
        expiry_date = request.form['expiry_date']
        code = generate_unique_code()
        user = User(
            name=name,
            age=int(age),
            plan_name=plan_name,
            amount=float(amount),
            expiry_date=datetime.strptime(expiry_date, "%Y-%m-%d").date(),
            code=code
        )
        db.session.add(user)
        db.session.commit()
        return render_template('register.html', code=code, registered=True)
    return render_template('register.html', registered=False)

@app.route('/login', methods=['POST'])
def login():
    code = request.form['code']
    user = User.query.filter_by(code=code).first()
    if user:
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid code, please try again.", "danger")
        return redirect(url_for('home'))

# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('home'))
#     user = User.query.get(session['user_id'])
#     if not user:
#         return redirect(url_for('home'))
#     today = datetime.today().date()
#     if user.expiry_date < today:
#         return render_template('expired.html', expiry_date=user.expiry_date.strftime('%Y-%m-%d'))
#     return render_template('dashboard.html', user=user)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('home'))
    today = datetime.today().date()
    if user.expiry_date < today:
        return render_template('expired.html', expiry_date=user.expiry_date.strftime('%Y-%m-%d'))
    days_remaining = (user.expiry_date - today).days
    return render_template('dashboard.html', user=user, days_remaining=days_remaining)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)