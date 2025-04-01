from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
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


#
class User(db.Model):
    id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    email: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(120), unique=True)
    password_hash: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(255))
    sets_unit: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(2), default="kg")
    bodyweight_unit: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(2), default="kg")
    receive_reports: sa.orm.Mapped[bool] = sa.orm.mapped_column(sa.Boolean, default = True)
    
    def __repr__(self):
        return f"<User {self.email}>"



# Generic route for testing that the Flask application works
@app.route('/')
def index():
    return "Hello"

