from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Get the path of the directory where the app.py script is located
basedirectory = os.path.abspath(os.path.dirname(__file__))

# Create a Flask application instance
app = Flask(__name__)

# Retrieve secret key from environment variable and set it
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# Configure the SQLite database URI by joining the base directory with 'tracker.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedirectory, 'tracker.db')

# Initialize SQLAlchemy for the Flask app
db = SQLAlchemy(app)

# Generic route for testing that the Flask application works
@app.route('/')
def index():
    return "Hello"

