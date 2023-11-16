from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv 

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
load_dotenv()

import jwt
import datetime
app = Flask(__name__)
jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

#print(os.getenv('MONGO_URI'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

#print(os.getenv("SECRET_KEY"))


# User Schema
user_schema = { 
    'username': str,
    'password': str
}

# Task Schema
task_schema = {
    'name': str,
    'description': str,
    'completed': bool
}

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        # Access the identity of the current user with get_jwt_identity
        current_user = get_jwt_identity()
        print(current_user)
        return jsonify(logged_in_as=current_user), 200
    except Exception as e:
        return jsonify({'error': str(e)})
    
# Routes for signup

@app.route('/signup', methods=['POST'])

def signup():
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

@app.route('/signin', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400

        user = mongo.db.users.find_one({'username': data['username']})
        if user and check_password_hash(user['password'], data['password']):
            # Generate JWT token
            # expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token expires in 1 day
            # access_token = jwt.encode({'username': data['username'], 'exp': expiration}, app.config['SECRET_KEY']== os.getenv('SECRET_KEY'))     #original one 
            
            access_token = create_access_token(identity=data['username'])

            # # Print the decoded identity
            # decoded_identity = get_jwt_identity()
            # print(f"Decoded Identity: {decoded_identity}")

            return jsonify({'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)})


# Routes for add tasks 
@app.route('/tasks', methods=['POST'])
@jwt_required()  # Requires a valid JWT token
def add_task():
    try:
        current_user = get_jwt_identity()
        print(f"Current User: {current_user}")
        data = request.get_json()
        if data.get('name') == '' or data.get('description') == '':
            return jsonify({'error': 'Name and description cannot be blank'}), 400
        task={
            
            'name': data['name'],
            'description': data['description'],
            'completed': data.get('completed',False),
            'user': current_user

        }
        result = mongo.db.tasks.insert_one(task)
        inserted_task = mongo.db.tasks.find_one({'_id': result.inserted_id})
        response_data = {
            '_id': str(result.inserted_id),
            'name': inserted_task['name'],
            'description': inserted_task['description']
        }
        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({'error': str(e)})

# Route to view all tasks

@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_all_tasks():
    try:

        current_user= get_jwt_identity()
        tasks = list(mongo.db.tasks.find({'user': current_user}))
        formatted_tasks = [{'_id': str(task['_id']), 'name': task.get('name',None)} for task in tasks]

        return jsonify({'tasks':formatted_tasks})
    except Exception as e:
        return jsonify({'error':str(e)})

# Route to view a specific task

@app.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    try:
        current_user = get_jwt_identity()
        task = mongo.db.tasks.find_one({'_id': ObjectId(task_id),'user': current_user})
        if task:
            formatted_task = {'_id': str(task['_id']), 'name': task['name'], 'description': task['description']}
            return jsonify({'task': formatted_task})
        else:
            return jsonify({'message': 'Task not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error':str(e)})

# Route for update task
@app.route('/tasks/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        current_user=get_jwt_identity()
        data = request.get_json()
        task = mongo.db.tasks.find_one({'_id':ObjectId(task_id),'user':current_user})
        if not task:
            return jsonify({'message':'Task not found or unauthorized'}),404
        
        # Check if the task was found and updated

        if data.get('name') == '' or data.get('description') == '':
            return jsonify({'error': 'Name and description cannot be blank'}), 400
        if 'completed' in data and type(data['completed']) != bool:
            return jsonify({'error': 'Completed must be a boolean value'}), 400
        
        update_data = {k: task_schema[k](v) for k, v in data.items() if k in task_schema}
        result = mongo.db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': update_data})
        # Check if the task was found and updated
        if result.modified_count > 0:
            return jsonify({'message': 'Task updated successfully'})
        else: 
            return jsonify({'message': 'Task not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)})

# Route to delete a task
@app.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        current_user=get_jwt_identity()
        task = mongo.db.tasks.find_one({'_id':ObjectId(task_id),'user':current_user})
        if task:
            mongo.db.tasks.delete_one({'_id': ObjectId(task_id)})
            return jsonify({'message': 'Task deleted successfully'})
        else:
            return jsonify({'message': 'Task not found or unauthorized'}),404
    except Exception as e:
            return jsonify({'error':str(e)})


if __name__ == '__main__':
    app.run(debug=True)
