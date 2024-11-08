from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import DeclarativeBase

import os

basedirectory = os.path.abspath(os.path.dirname(__file__))

class Configuration:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedirectory, 'tracker.db')
    
app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)


@app.route("/")
def index():
    return "Hello"