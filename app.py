from flask import Flask,g
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv 
from flask_jwt_extended import JWTManager
from auth import auth_bp 
from task import task_bp
load_dotenv()
import datetime
app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1) 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

#We use this to set mongo instance global g object, so it can accessible within blueprint during request.
@app.before_request  
def before_request():                           
    g.mongo = mongo                          
                            
#Register Blueprints here
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(task_bp,url_prefix='/task')

if __name__ == '__main__':
    app.run(debug=True)
