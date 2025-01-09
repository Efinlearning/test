from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import re
import config
from datetime import timedelta
import uuid  # For generating unique access tokens

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = timedelta(days=7)  # Set session expiry time

# MongoDB Configuration
client = MongoClient(config.MONGODB_URI)
db = client['user_db']
users_collection = db['users']
brokers_collection = db['brokers']

# Email Validation
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Password Validation
def is_valid_password(password):
    return len(password) >= 8  # Example password validation

# Generate Access Token
def generate_access_token():
    return str(uuid.uuid4())  # Generate a unique access token

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_name' in session:  # Check if the user is already logged in
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Check if email is valid
        if not is_valid_email(email):
            flash("Invalid email format.", "error")
            return redirect(url_for('signup'))

        # Check if password is valid
        if not is_valid_password(password):
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('signup'))

        # Check if email already exists
        if users_collection.find_one({'email': email}):
            flash("Email already registered.", "error")
            return redirect(url_for('signup'))

        # Hash the password and insert the user into the database
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'email': email, 'phone': phone, 'password': hashed_password})
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_name' in session:  # Check if the user is already logged in
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check user in database
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session.permanent = True  # Make session permanent
            session['user_name'] = user['email']  # Store user name in session
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_name' in session:
        return render_template('dashboard.html', name=session['user_name'])
    return redirect(url_for('login'))

@app.route('/add_broker', methods=['GET', 'POST'])
def add_broker():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_name']
    
    if request.method == 'POST':
        # Fetch form data
        broker_name = request.form['broker_name']
        api_key = request.form['api_key']
        secret_key = request.form['secret_key']
        redirect_url = request.form['redirect_url']

        # Save data to MongoDB
        broker_data = {
            "email": user_email,
            "broker_name": broker_name,
            "api_key": api_key,
            "secret_key": secret_key,
            "redirect_url": redirect_url
        }

        # Check if user already has broker details
        existing_broker = brokers_collection.find_one({"email": user_email, "broker_name": broker_name})
        if existing_broker:
            # Update existing details
            brokers_collection.update_one({"_id": existing_broker["_id"]}, {"$set": broker_data})
            flash(f"Broker {broker_name} details updated successfully!", "success")
        else:
            # Insert new broker details
            brokers_collection.insert_one(broker_data)
            flash(f"Broker {broker_name} connected successfully!", "success")
        
        return redirect(url_for('dashboard'))
    
    # Fetch existing broker details for the user
    user_brokers = list(brokers_collection.find({"email": user_email}))
    return render_template('connect_broker.html', brokers=user_brokers)

@app.route('/logout')
def logout():
    if 'user_name' in session:
        # Generate access token
        access_token = generate_access_token()
        user_email = session['user_name']
       
        # Optionally, store or log the access token for audit purposes
        print(f"User {user_email} signed out. Access Token: {access_token}")
       
        # Remove user session
        session.pop('user_name', None)
        flash("You have been logged out.", "info")
   
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
