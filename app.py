from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config["MONGO_URI"] = "your_mongodb_atlas_connection_string"
mongo = PyMongo(app)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match!"

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email address!"

        if not re.match(r"^[0-9]{10}$", phone):
            return "Invalid phone number!"

        hashed_password = generate_password_hash(password)

        user = {
            'email': email,
            'phone': phone,
            'password': hashed_password
        }

        mongo.db.users.insert_one(user)

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['user'] = email
            return redirect(url_for('dashboard'))

        return "Invalid email or password!"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Welcome {session['user']}! <br><a href='/logout'>Logout</a>"
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
