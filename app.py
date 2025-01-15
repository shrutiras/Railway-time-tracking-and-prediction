from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:password@localhost/railway')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_name = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.String(50), nullable=False)
    arrival_time = db.Column(db.String(50), nullable=False)

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # Default role is 'user'

    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    # Hash password and save user
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Find user
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Generate JWT token
    token = create_access_token(identity={'username': username, 'role': user.role})
    return jsonify({'token': token})

@app.route('/fetch-trains', methods=['GET'])
@jwt_required()
def fetch_trains():
    try:
        # Fetch trains from external API
        API_KEY = os.getenv('API_KEY')
        API_BASE_URL = os.getenv('API_BASE_URL')
        url = f"{API_BASE_URL}/schedule"
        headers = {'Authorization': f"Bearer {API_KEY}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/add-train', methods=['POST'])
@jwt_required()
def add_train():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    train = Train(
        train_name=data['train_name'],
        source=data['source'],
        destination=data['destination'],
        departure_time=data['departure_time'],
        arrival_time=data['arrival_time']
    )
    db.session.add(train)
    db.session.commit()

    return jsonify({'message': 'Train added successfully'})

@app.route('/admin/view-users', methods=['GET'])
@jwt_required()
def view_users():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role} for u in users])

@app.route('/user/view-trains', methods=['GET'])
@jwt_required()
def view_trains():
    trains = Train.query.all()
    return jsonify([
        {
            'id': train.id,
            'train_name': train.train_name,
            'source': train.source,
            'destination': train.destination,
            'departure_time': train.departure_time,
            'arrival_time': train.arrival_time
        }
        for train in trains
    ])

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
 
