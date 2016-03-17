from flask import Flask, render_template
from flask.ext.bcrypt import Bcrypt
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface


app = Flask(__name__)
app.debug = True
app.config["MONGODB_HOST"] = 'localhost'
app.config["MONGODB_PORT"] = 27017
app.config["MONGODB_DATABASE"] = 'flask_rest_test'
SECRET_KEY = 'secret-key'

db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)

flask_bcrypt = Bcrypt(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')

