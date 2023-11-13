from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)

# MongoDB Configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MyDatabase'
mongo = PyMongo(app)

# Task Schema

task_schema={
    'name': str,
    'description': str,
    'completed': bool
}

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
            'description': inserted_task['description'],
            # 'completed': inserted_task['completed']
        }
        return jsonify(response_data), 201
        # return jsonify({'_id': str(result.inserted_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to view all tasks

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    tasks = list(mongo.db.tasks.find())
    # return jsonify({'tasks': tasks})
    formatted_tasks = [{'_id': str(task['_id']), 'name': task.get('name',None)} for task in tasks]

    return jsonify({'tasks':formatted_tasks})

# Route to view a specific task
@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = mongo.db.tasks.find_one({'_id': ObjectId(task_id)})
    if task:
        formatted_task = {'_id': str(task['_id']), 'name': task['name'], 'description': task['description'], 'completed': task['completed']}
        return jsonify({'task': formatted_task})
    else:
        return jsonify({'message': 'Task not found'}), 404

# Route for update task
@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.get_json()
        if 'name' in data and not data['name'].strip():
            return jsonify({'error': 'Name cannot be blank'}), 400

        # Using direct equality check for 'description'
        if 'description' in data and data['description'] == '':
            return jsonify({'error': 'Description cannot be blank'}), 400

        # Adding a condition for 'completed'
        if 'completed' in data and data['completed'] not in [True, False]:
            return jsonify({'error': 'Completed must be a boolean value'}), 400
        
        update_data = {k: task_schema[k](v) for k, v in data.items() if k in task_schema}
        result = mongo.db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': update_data})
        # Check if the task was found and updated
        if result.modified_count > 0:
            return jsonify({'message': 'Task updated successfully'})
        else: 
            return jsonify({'message': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), #500

# Route to delete a task
@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    mongo.db.tasks.delete_one({'_id': ObjectId(task_id)})
    return jsonify({'message': 'Task deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
