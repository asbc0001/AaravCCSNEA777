from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import DeclarativeBase

import os

basedirectory = os.path.abspath(os.path.dirname(__file__))

class Configuration:
    #need to add secret key variable thing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedirectory, 'tracker.db')
    
app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(200), nullable = False)
    
    def __repr__(self):
        return f'<Users {self.username}>'

with app.app_context():
    db.create_all()
    ### change to if not exists instead? check what grinberg does here, whether to just use flask shell instead

@app.route("/")
def index():
    return "Hello"