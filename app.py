from flask import Flask, render_template, redirect, flash, request                                                                                                           # type: ignore
from typing import List
from flask_sqlalchemy import SQLAlchemy                                                                                                                              # type: ignore
from typing import List
import sqlalchemy as sa                                                                                                                                              # type: ignore
from typing import List
import datetime
import os
import re         
from typing import List
from werkzeug.security import generate_password_hash                                                                                                                    # type: ignore

# Import list of dictionaries of default exercises from defaultexercises.py
from defaultexercises import default_exercises                                                                                                                               #type:ignore

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

# Define array of catgeories    
categories = ["Back", "Biceps", "Chest", "Forearms", "Legs", "Shoulders", "Triceps"]


# Route for allowing users to register and create an account
@app.route('/register', methods=["GET", "POST"])
def Register():
    if request.method == "GET":
        return render_template("register.html")
    
    elif request.method == "POST":
        # Get user inputs from register form
        email_address = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Perform input validations:
        
        if not email_address or not password or not confirm_password:
            flash("Must complete all fields", "negative")
            
        # Define regular expression format of an email address
        email_format = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        # Check whether email_address is in email address format
        if not re.match(email_format, email_address):
            flash("Must enter a valid email address", "negative")
        
        # Get all user email addresses from the user table
        emails = User.query.with_entities(User.email).all()
        # Extract email addresses from the resulting list of tuples
        email_list = [email[0] for email in emails]
        if email_address in email_list:
            flash("User with that email address already exists", "negative")
        
        # Define regular expression pattern for a strong password
        password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        if not re.match(password_pattern, password):
            flash("Password must be at least 8 characters long and use at least one each of"
                  " upper-case letters, lower-case letters, numbers and symbols", "negative")
            
        if password != confirm_password:
            flash("Both passwords must be the same", "negative")
        
        # Process of creating a new user, if inputs have passed all validation checks
        else:
            # Generate hash of password
            hash = generate_password_hash(password)
            
            # Add new user to user table of tracker.db
            new_user = User(email=email_address, password_hash=hash)
            db.session.add(new_user)
            db.session.commit()
            
            # Get the new user's user_id
            user_id = new_user.user_id

            # Add default exercises to exercise table with the new user's user_id
            for exercise in default_exercises:
                new_exercise = Exercise(name=exercise["name"], category=exercise["category"], user_id=user_id)
                db.session.add(new_exercise)
            db.session.commit()
            
            flash("User created succesfully", "positive")
            return redirect("/login")
        return redirect("/register")

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
    return redirect("/workouts")

@app.route('/workouts')
def Workouts():
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