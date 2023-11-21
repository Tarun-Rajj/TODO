
# auth/auth.py
from flask import Blueprint, request, jsonify,g
from flask_jwt_extended import create_access_token

from werkzeug.security import generate_password_hash, check_password_hash


auth_bp = Blueprint('auth_bp',__name__)


# Define the user schema
user_schema = {
    'username': str,
    'password': str
}
   
# Routes for signup
@auth_bp.route('/signup', methods=['POST'])
def signup():  
    mongo=g.mongo 
    try:
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        existing_user = mongo.db.users.find_one({'username': data['username']})
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        hashed_password = generate_password_hash(data['password'])
        new_user = {'username': data['username'], 'password': hashed_password}
        mongo.db.users.insert_one(new_user)
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)})
    
#route for login
@auth_bp.route('/signin', methods=['POST'])
def signin():
    mongo=g.mongo
    try:
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        user = mongo.db.users.find_one({'username': data['username']})
        if user and check_password_hash(user['password'], data['password']):
            print(user)
            access_token = create_access_token(identity=str(user['_id']))
            return jsonify({'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)})


   



    
