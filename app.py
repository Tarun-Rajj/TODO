from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ramrama'

# MongoDB Configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MyDatabase'
mongo = PyMongo(app)

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
            access_token = jwt.encode({'username': str(data['username'])}, app.config['SECRET_KEY'])
            return jsonify({'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)})


# Routes for add tasks 
@app.route('/tasks', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        if data.get('name') == '' or data.get('description') == '':
            return jsonify({'error': 'Name and description cannot be blank'}), 400
            
        # Create the task dictionary
        task = {k: task_schema[k](v) for k, v in data.items() if k in task_schema}
        result = mongo.db.tasks.insert_one(task)
        inserted_task = mongo.db.tasks.find_one({'_id': result.inserted_id})
        response_data = {
            '_id': str(result.inserted_id),
            'name': inserted_task['name'],
            'description': inserted_task['description']
        }
        return jsonify(response_data), 201
        # return jsonify({'_id': str(result.inserted_id)})
    except Exception as e:
        return jsonify({'error': str(e)})

# Route to view all tasks

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    tasks = list(mongo.db.tasks.find())
    formatted_tasks = [{'_id': str(task['_id']), 'name': task.get('name',None)} for task in tasks]

    return jsonify({'tasks':formatted_tasks})

# Route to view a specific task
@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = mongo.db.tasks.find_one({'_id': ObjectId(task_id)})
    if task:
        formatted_task = {'_id': str(task['_id']), 'name': task['name'], 'description': task['description']}
        return jsonify({'task': formatted_task})
    else:
        return jsonify({'message': 'Task not found'}), 404

# Route for update task
@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.get_json()
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
            return jsonify({'message': 'Task not found'}), 404
    except Exception as e:
        print("hi",e)
        return jsonify({'error': str(e)})

# Route to delete a task
@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    mongo.db.tasks.delete_one({'_id': ObjectId(task_id)})
    return jsonify({'message': 'Task deleted successfully'})



if __name__ == '__main__':
    app.run(debug=True)
