from flask import Flask, render_template, redirect, flash                                                                                                           # type: ignore
from typing import List
from flask_sqlalchemy import SQLAlchemy                                                                                                                              # type: ignore
from typing import List
import sqlalchemy as sa                                                                                                                                              # type: ignore
from typing import List
import datetime
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


# Model to define the structure of the database user table
class User(db.Model):
    __tablename__ = "user"
    
    user_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    email: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(120), unique=True)
    password_hash: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(255))
    sets_unit: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(2), default="kg")
    bodyweight_unit: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(2), default="kg")
    receive_reports: sa.orm.Mapped[bool] = sa.orm.mapped_column(sa.Boolean, default = True)
    
    # Define relationship to Bodyweight model
    bodyweights: sa.orm.Mapped[list["Bodyweight"]] = sa.orm.relationship(back_populates="user")
    
    # Define relationship to Exercise model
    exercises: sa.orm.Mapped[list["Exercise"]] = sa.orm.relationship(back_populates="user")
    
    # Define relationship to Goal model
    goals: sa.orm.Mapped[list["Goal"]] = sa.orm.relationship(back_populates="user")
    
    # Define relationship to Set model
    sets: sa.orm.Mapped[list["Set"]] = sa.orm.relationship(back_populates="user")
    
    # Method for providing string representation (email) of the User instance for debugging/logging purposes
    def __repr__(self):
        return f"<User {self.email}>"

# Model to define the structure of the database bodyweight table
class Bodyweight(db.Model):
    weight_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    weight: sa.orm.Mapped[float] = sa.orm.mapped_column(sa.Float)
    date: sa.orm.Mapped[datetime.date] = sa.orm.mapped_column(sa.Date)
    time_entered: sa.orm.Mapped[datetime.time] = sa.orm.mapped_column(sa.Time)
    user_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, sa.ForeignKey("user.user_id"))
                                               
    # Define relationship to User model
    user: sa.orm.Mapped[User] = sa.orm.relationship(back_populates="bodyweights")
    
    # Displays data about a Bodyweight entry for debugging / logging purposes
    def __repr__(self):
        return f"<Bodyweight {self.weight} on {self.date} for User {self.user_id}>"

# Model to define structure of the database exercise table
class Exercise(db.Model):
    exercise_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(50))
    category:sa.orm.Mapped[str] = sa.orm.mapped_column(sa.String(10))
    user_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, sa.ForeignKey("user.user_id"))
    
    # Define relationship to User model
    user: sa.orm.Mapped[User] = sa.orm.relationship(back_populates="exercises")
    
    # Define relationship to Goal model
    goals: sa.orm.Mapped[list["Goal"]] = sa.orm.relationship(back_populates="exercise", cascade="all, delete")
    
    # Define relationship to Set model
    sets: sa.orm.Mapped[list["Set"]] = sa.orm.relationship(back_populates="exercise", cascade="all, delete")
    
    # Display data about an Exercise entry for debugging / logging purposes
    def __repr__(self):
        return f"<Exercise {self.name} for User {self.user_id}>"

# Model to define structure of the database goal table    
class Goal(db.Model):
    goal_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    target: sa.orm.Mapped[float] = sa.orm.mapped_column(sa.Float)
    date_entered: sa.orm.Mapped[datetime.date] = sa.orm.mapped_column(sa.Date)
    user_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, sa.ForeignKey("user.user_id"))
    exercise_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, sa.ForeignKey("exercise.exercise_id"))
    
    # Define relationship to User model
    user: sa.orm.Mapped[User] = sa.orm.relationship(back_populates="goals")
    
    # Define relationship to Exercise model
    exercise: sa.orm.Mapped[Exercise] = sa.orm.relationship(back_populates="goals")
    
    # Display data about a Goal entry for debugging / logging purposes
    def __repr__(self):
        return f"<Goal {self.target} for Exercise {self.exercise_id} for User {self.user_id}>"

# Model to define structure of the database set table
class Set(db.Model):
    set_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    weight: sa.orm.Mapped[float] = sa.orm.mapped_column(sa.Float)
    reps: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer)
    estimated_1RM: sa.orm.Mapped[float] = sa.orm.mapped_column(sa.Float)
    date: sa.orm.Mapped[datetime.date] = sa.orm.mapped_column(sa.Date)
    user_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, sa.ForeignKey("user.user_id"))
    exercise_id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.Integer, sa.ForeignKey("exercise.exercise_id"))
    
    # Define relationship to User model
    user: sa.orm.Mapped[User] = sa.orm.relationship(back_populates="sets")
    
    # Define relationship to Exercise model
    exercise: sa.orm.Mapped[Exercise] = sa.orm.relationship(back_populates="sets")
    
    # Display data about a Set entry for debugging / logging purposes
    def __repr__(self):
        return f"<Weight {self.weight} for reps {self.reps} on date {self.date} for exercise {self.exercise_id} for User {self.user_id}>"
    
categories = ["Abs", "Back", "Biceps", "Chest", "Forearms", "Legs", "Shoulders", "Triceps"]

# Temporary placeholder versions of each route to allow navigation bar to be implemented
@app.route('/register')
def Register():
    return "Register"

@app.route('/login')
def Login():
    return "Login"

@app.route('/logout')
def Logout():
    return "Logout"

@app.route('/reset_password')
def Reset_Password():
    return "Reset Password"

@app.route('/change_password')
def Change_Password():
    return "Change password"

@app.route('/')
@app.route('/index')
def Index():
    return redirect('/workouts')

@app.route('/workouts')
def Workouts():
    flash("Negative", "negative")
    flash("Positive", "positive")
    return render_template("workouts.html")

@app.route('/exercises')
def Exercises():
    return "Exercises"

@app.route('/exercise_graph')
def Exercise_Graph():
    return render_template("exercise_graph.html")

@app.route('/workout_graph')
def Workout_Graph():
    return "Workout graph"

@app.route('/workout_chart')
def Workout_Chart():
    return "Workout chart"

@app.route('/bodyweight')
def Bodyweights():
    return "Bodyweight"

@app.route('/bodyweight_graph')
def Bodyweight_Graph():
    return "Bodyweight graph"

@app.route('/settings')
def Settings():
    return "Settings"

@app.route('/goals')
def Goals():
    return "Goals"

@app.route('/1rm_prediction')
def Prediction():
    return "1RM Prediction"