from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# MongoDB Configuration
client = MongoClient(config.MONGODB_URI)
db = client['user_db']
users_collection = db['users']

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])

        # Check if the email already exists
        if users_collection.find_one({'email': email}):
            return "Email already registered."

        # Insert user into database
        users_collection.insert_one({'email': email, 'phone': phone, 'password': password})
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check user in database
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_name'] = user['email']  # Store user name in session
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials."

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_name' in session:
        return render_template('dashboard.html', name=session['user_name'])
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
