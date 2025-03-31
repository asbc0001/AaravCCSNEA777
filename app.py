from flask import Flask

# Create a Flask application instance
app = Flask(__name__)


# Generic route for testing that the Flask application works, will be removed after
@app.route('/')
def index():
    return "Hello"

