from flask import Flask, render_template, request, redirect, flash
from pymongo import MongoClient
import bcrypt
from urllib.parse import quote_plus

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
username = quote_plus('')
password = quote_plus('')
MONGO_URI = f'mongodb://{username}:{password}@cluster0-shard-00-00.mongodb.net:27017,cluster0-shard-00-01.mongodb.net:27017,cluster0-shard-00-02.mongodb.net:27017/Usercred?retryWrites=true&w=majority'
DB_NAME = "Username"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email").strip()
        phone = request.form.get("phone").strip()
        password = request.form.get("password").strip()

        # Server-side validation
        if not email or not phone or not password:
            flash("All fields are required!", "error")
            return redirect("/signup")

        if users_collection.find_one({"email": email}):
            flash("Email already exists!", "error")
            return redirect("/signup")

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Save user data to MongoDB
        users_collection.insert_one({
            "email": email,
            "phone": phone,
            "password": hashed_password.decode('utf-8')
        })

        flash("Signup successful!", "success")
        return redirect("/signup")

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
