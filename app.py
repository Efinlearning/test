from flask import Flask, render_template, request, redirect, flash
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient("mongodb+srv://KP025M:Mitra@1230@cluster0.mongodb.net/Usercred?retryWrites=true&w=majority")
db = client["Usercred"]
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
