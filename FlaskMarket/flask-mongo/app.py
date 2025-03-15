



from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Connect to MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/contactdb"
mongo = PyMongo(app)

# Sample User Schema
users_collection = mongo.db.users  # Stores users
contacts_collection = mongo.db.contacts  # Stores contacts


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    existing_user = users_collection.find_one({"email": data["email"]})
    
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(data["password"])
    
    user = {
        "email": data["email"],
        "password": hashed_password
    }
    
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully!"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})

    if user and check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


from flask_mail import Mail, Message
import secrets

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "your_email@gmail.com"
app.config["MAIL_PASSWORD"] = "your_password"

mail = Mail(app)

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})

    if user:
        token = secrets.token_hex(16)
        reset_link = f"http://127.0.0.1:5000/reset-password/{token}"
        
        msg = Message("Password Reset", sender="your_email@gmail.com", recipients=[data["email"]])
        msg.body = f"Click this link to reset your password: {reset_link}"
        mail.send(msg)

        return jsonify({"message": "Password reset link sent!"}), 200
    else:
        return jsonify({"error": "Email not found"}), 404


@app.route('/add-contact', methods=['POST'])
def add_contact():
    data = request.json

    contact = {
        "mobile": data["mobile"],
        "email": data["email"],
        "address": data["address"],
        "registration_number": data["registration_number"]
    }
    
    contacts_collection.insert_one(contact)
    return jsonify({"message": "Contact saved!"}), 201

@app.route('/search-contact/<registration_number>', methods=['GET'])
def search_contact(registration_number):
    contact = contacts_collection.find_one({"registration_number": registration_number}, {"_id": 0})

    if contact:
        return jsonify(contact), 200
    else:
        return jsonify({"error": "Contact not found"}), 404
