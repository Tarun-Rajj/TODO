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
@app.route('/add/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    task = {k: task_schema[k](v) for k, v in data.items() if k in task_schema}
    result = mongo.db.tasks.insert_one(task)
    return jsonify({'_id': str(result.inserted_id)})

# Route to view all tasks

@app.route('/viewall/tasks', methods=['GET'])
def get_all_tasks():
    tasks = list(mongo.db.tasks.find())
    # return jsonify({'tasks': tasks})
    formatted_tasks = [{'_id': str(task['_id']), 'name': task.get('name',None)} for task in tasks]

    return jsonify({'tasks':formatted_tasks})

# Route to view a specific task
@app.route('/view/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = mongo.db.tasks.find_one({'_id': ObjectId(task_id)})
    if task:
        formatted_task = {'_id': str(task['_id']), 'name': task['name'], 'description': task['description'], 'completed': task['completed']}
        return jsonify({'task': formatted_task})
    else:
        return jsonify({'message': 'Task not found'}), 404

# Route to update the task
@app.route('/update/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    update_data = {k: task_schema[k](v) for k, v in data.items() if k in task_schema}
    mongo.db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': update_data})
    return jsonify({'message': 'Task updated successfully'})

# Route to delete a task

@app.route('/delete/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    mongo.db.tasks.delete_one({'_id': ObjectId(task_id)})
    return jsonify({'message': 'Task deleted successfully'})
# Route to complete a task

@app.route('/complete/tasks/<task_id>', methods=['PUT'])
def complete_task(task_id):
    mongo.db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': {'completed': complete_task}})
    return jsonify({'message': 'Task marked as completed'})

if __name__ == '__main__':
    app.run(debug=True)
