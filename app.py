from flask import Flask
import os

# Create a Flask application instance
app = Flask(__name__)

# Retrieve secret key from environment variable and set it
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Generic route for testing that the Flask application works, will be removed after
@app.route('/')
def index():
    return "Hello"

