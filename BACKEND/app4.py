from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Yuva:Yuva_06@localhost/image_bot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)
CORS(app)

db = SQLAlchemy(app)

# Database model for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Create database tables if not already created
with app.app_context():
    db.create_all()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name, email, password = data['name'], data['email'], data['password']
    hashed_password = generate_password_hash(password)  # Hash the password
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists!"}), 400

    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Signup successful!"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email, password = data['email'], data['password']
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session['user'] = user.name  # Store user's name in session
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"error": "Invalid credentials!"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logout successful!"}), 200

@app.route('/current_user', methods=['GET'])
def current_user():
    user = session.get('user')
    if user:
        return jsonify({"name": user}), 200
    return jsonify({"error": "No user logged in"}), 401

if __name__ == '__main__':
    app.run(debug=True)
