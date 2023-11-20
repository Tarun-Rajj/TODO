from flask import Blueprint,jsonify,request,g
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId


task_bp = Blueprint('task_bp',__name__)

task_schema = {
    'name': str,
    'description': str,
    'completed': bool
}

# Routes for add tasks 
@task_bp.route('/', methods=['POST'])
@jwt_required()  
def add_task():
    mongo = g.mongo
    try:
        current_user = get_jwt_identity()
        print(f"Current User: {current_user}")
        data = request.get_json()
        if data.get('name') == '' or data.get('description') == '':
            return jsonify({'error': 'Name and description cannot be blank'}), 400
        task={
            
            'name': data['name'],
            'description': data['description'],
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
@task_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_tasks():
        mongo=g.mongo
        current_user= get_jwt_identity()
        tasks = list(mongo.db.tasks.find({'user': current_user}))
        formatted_tasks = [{'_id': str(task['_id']), 'name': task.get('name',None)} for task in tasks]
        return jsonify({'tasks':formatted_tasks})
   
# Route to view a specific task
@task_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    mongo=g.mongo
    current_user = get_jwt_identity()
    task = mongo.db.tasks.find_one({'_id': ObjectId(task_id), 'user': current_user})
    if task:
        formatted_task = {'_id': str(task['_id']), 'name': task['name'], 'description': task['description']}
        return jsonify({'task': formatted_task})
    else:
        return jsonify({'message': 'Task not found or unauthorized'}), 404
    
# Route for update task
@task_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
        mongo=g.mongo
        current_user=get_jwt_identity()
        data = request.get_json()
        task = mongo.db.tasks.find_one({'_id':ObjectId(task_id),'user':current_user})
        if not task:
            return jsonify({'message':'Task not found or unauthorized'}),404 
        if data.get('name') == '' or data.get('description') == '':
            return jsonify({'error': 'Name and description cannot be blank'}), 400
        if 'completed' in data and type(data['completed']) != bool:
            return jsonify({'error': 'Completed must be a boolean value'}), 400       
        update_data = {k: task_schema[k](v) for k, v in data.items() if k in task_schema}
        result = mongo.db.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': update_data})
        if result.modified_count > 0:
            return jsonify({'message': 'Task updated successfully'})
        else: 
            return jsonify({'message': 'Task not found or unauthorized'}), 404
    
# Route to delete a task
@task_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
        mongo=g.mongo
        current_user=get_jwt_identity()
        task = mongo.db.tasks.find_one({'_id':ObjectId(task_id),'user':current_user})
        if task:
            mongo.db.tasks.delete_one({'_id': ObjectId(task_id)})
            return jsonify({'message': 'Task deleted successfully'})
        else:
            return jsonify({'message': 'Task not found or unauthorized'}),404
   

