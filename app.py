from flask import Flask, request, session, redirect, url_for, send_from_directory
from models import db, User
from datetime import datetime
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gymuser:347690%40Fk@localhost:5432/gymdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

def generate_unique_code():
    while True:
        code = str(random.randint(1000, 9999))
        if not User.query.filter_by(code=code).first():
            return code

def render_html(filename, **kwargs):
    filepath = os.path.join(TEMPLATES_FOLDER, filename)
    with open(filepath, encoding='utf-8') as f:
        html = f.read()
    for key, value in kwargs.items():
        html = html.replace('{{' + key + '}}', str(value))
    return html

@app.route('/')
def home():
    return redirect(url_for('login'))

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
        message = f"""
            <div class='flash'>
                Thank you for registering!<br>
                Your unique 4-digit code is: <strong>{code}</strong><br>
                Please use this code to log in.<br>
                <a href="/login">Go to Login</a>
            </div>
        """
        return render_html('register.html', register_message=message)
    else:
        return render_html('register.html', register_message='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        code = request.form['code']
        user = User.query.filter_by(code=code).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            error = "<div class='flash'>Invalid code, please try again.</div>"
    return render_html('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    today = datetime.today().date()
    days_remaining = (user.expiry_date - today).days
    if days_remaining < 0:
        return render_html('expired.html', expiry_date=user.expiry_date.strftime('%Y-%m-%d'))
    return render_html(
        'dashboard.html',
        name=user.name,
        code=user.code,
        age=user.age,
        plan_name=user.plan_name,
        amount="{:.2f}".format(user.amount),
        expiry_date=user.expiry_date.strftime('%Y-%m-%d'),
        days_remaining=days_remaining,
        registered_on=user.registered_on.strftime('%Y-%m-%d')
    )

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)