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
from werkzeug.security import generate_password_hash, check_password_hash                                                                                                                    # type: ignore
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required                                                                                                  #type: ignore
from flask_mail import Mail, Message
import jwt
from time import time
from threading import Thread

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
# Set the session lifetime to 30 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)

# Configure Flask-Mail variables
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'actrackeremails@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'actrackeremails@gmail.com'

# Initialize Flask-Login
login = LoginManager(app)

# Create Flask-Mail instance
mail = Mail(app)

# Set the route to which users will be redirected if attempting to access a route requiring authentication
login.login_view = 'Login'

# Initialize SQLAlchemy for the Flask app
db = SQLAlchemy(app)


# Model to define the structure of the database user table
class User(UserMixin, db.Model):
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
    
    # Override get_id method to use user_id instead of id
    def get_id(self):
        return str(self.user_id)
    
    # Method for returning JWT token as a string
    def get_reset_password_token(self):
        return jwt.encode({'reset_password': self.user_id, 'exp': time() + 900}, app.config['SECRET_KEY'], algorithm='HS256')
    
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

# Configure user loader function
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# Function for pushing app context and sending an email
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)

# Define array of catgeories    
categories = ["Back", "Biceps", "Chest", "Forearms", "Legs", "Shoulders", "Triceps"]


# Route for allowing users to register and create an account
@app.route('/register', methods=["GET", "POST"])
def Register():
    if current_user.is_authenticated:
        return redirect("/workouts")
    
    if request.method == "GET":
        return render_template("register.html")
    
    elif request.method == "POST":
        # Get user inputs from register form
        email_address = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Perform input validations:
        errors = False
        
        if not email_address or not password or not confirm_password:
            flash("Must complete all fields", "negative")
            errors = True
            
        # Define regular expression format of an email address
        email_format = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        # Check whether email_address is in email address format
        if not re.match(email_format, email_address):
            flash("Must enter a valid email address", "negative")
            errors = True
        
        # Get all user email addresses from the user table
        emails = User.query.with_entities(User.email).all()
        # Extract email addresses from the resulting list of tuples
        email_list = [email[0].lower() for email in emails]
        if email_address.lower() in email_list:
            flash("User with that email address already exists", "negative")
            errors = True
        
        # Define regular expression pattern for a strong password
        password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        if not re.match(password_pattern, password):
            flash("Password must be at least 8 characters long and use at least one each of"
                  " upper-case letters, lower-case letters, numbers and symbols", "negative")
            errors = True
            
        if password != confirm_password:
            flash("Both passwords must be the same", "negative")
            errors = True
        
        if errors:
            return redirect("/register") 
        
        # Process of creating a new user, if inputs have passed all validation checks
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

# Route for allowing users to log in to the workout tracker
@app.route('/login', methods = ["GET", "POST"])
def Login():
    if current_user.is_authenticated:
        return redirect("/workouts")
    
    if request.method == "GET":
        return render_template("login.html")
    
    elif request.method == "POST":
        # Get user inputs from login form
        email_address = request.form.get("email")
        password = request.form.get("password")
        errors = False
        if not email_address or not password:
            flash("Must enter email address and password", "negative")
            errors = True
        
        # Query to get user based on email_address
        user = User.query.filter_by(email=email_address).first()

        # Check if the user exists and if the password matches the hash
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password", "negative")
            errors = True
            
        if errors:
            return redirect("/login")   
        
        # Log user in
        login_user(user)
        return redirect("/workouts")
        
        
# Route for logging out a user from the workout tracker
@app.route('/logout')
def Logout():
    logout_user()
    return redirect("/login")

# Route for sending a password reset email to a user who has forgotten their password
@app.route('/reset_password', methods = ["GET", "POST"])
def Reset_Password():
    if current_user.is_authenticated:
        return redirect("/workouts")
    
    if request.method == "GET":
        return render_template("reset_password.html")
    
    elif request.method == "POST":
        # Get user inputs from reset_password form
        email_address = request.form.get("email")
        errors = False
        if not email_address:
            flash("Must enter email address", "negative")
            errors = True
        
        # Query to get user based on email_address
        user = User.query.filter_by(email=email_address).first()
        if not user:
            flash("No user found with this email address", "negative")
            errors = True

        if errors:
            return redirect("/reset_password")
        
        # Generate password reset email token
        token = user.get_reset_password_token()
        # Create message object
        msg = Message("Reset Your Password for AC\'s Tracker", sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email])
        # Define the email content in both plaintext and html
        msg.body=render_template('email/reset_email.txt', token=token)
        msg.html=render_template('email/reset_email.html', token=token)
        
        # Starts a background thread to send the email asynchronously.
        Thread(target=send_async_email, args = (msg, )).start() 
        
        flash("Password reset email sent. The password reset link will expire in 15 minutes. You may need to check your spam folder", "positive")
        return redirect("/login")



@app.route('/change_password')
def Change_Password():
    return "Change password"

@app.route('/')
@app.route('/index')
@login_required
def Index():
    return redirect("/workouts")

@app.route('/workouts')
@login_required
def Workouts():
    return render_template("workouts.html")

@app.route('/exercises')
@login_required
def Exercises():
    return "Exercises"

@app.route('/exercise_graph')
@login_required
def Exercise_Graph():
    return render_template("exercise_graph.html")

@app.route('/workout_graph')
@login_required
def Workout_Graph():
    return "Workout graph"

@app.route('/workout_chart')
@login_required
def Workout_Chart():
    return "Workout chart"

@app.route('/bodyweight')
@login_required
def Bodyweights():
    return "Bodyweight"

@app.route('/bodyweight_graph')
@login_required
def Bodyweight_Graph():
    return "Bodyweight graph"

@app.route('/settings')
@login_required
def Settings():
    return "Settings"

@app.route('/goals')
@login_required
def Goals():
    return "Goals"

@app.route('/1rm_prediction')
@login_required
def Prediction():
    return "1RM Prediction"