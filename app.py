from flask import Flask, render_template, redirect, flash, request                                                                                                           # type: ignore
from typing import List
from flask_sqlalchemy import SQLAlchemy                                                                                                                              # type: ignore
import sqlalchemy as sa                                                                                                                                              # type: ignore
import datetime
import os
import re         
from werkzeug.security import generate_password_hash, check_password_hash                                                                                                                    # type: ignore
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required                                                                                                  #type: ignore
from flask_mail import Mail, Message                                                                                                                                                                #type: ignore
import jwt                                                                                                                                                                                                  #type:ignore
from time import time
from threading import Thread
from collections import defaultdict, OrderedDict
from dateutil.relativedelta import relativedelta                                                                                                                                                                        #type:ignore

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
        return jwt.encode({'change_password': self.user_id, 'exp': time() + 900}, app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['change_password']
        except:
            return None
        # Use the load_user function to fetch user by their user_id
        return load_user(id)
    
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

# Function for checking whether something is a positive float
def is_positive_float(value):
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False

# Function for checking whether something is a positive integer
def is_positive_int(value):
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False

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


# Route for allowing a user to change their password using the link from a password reset email
@app.route('/change_password/<token>', methods = ["GET", "POST"])
def Change_Password(token):
    if current_user.is_authenticated:
        return redirect("/workouts")
    
    # Get user from token
    user = User.verify_token(token)
    if not user:
        flash("Invalid or expired token", "negative")
        return redirect("/login")
    
    if request.method == "GET":
        return render_template("change_password.html", token = token)
    
    elif request.method == "POST":
        # Get user inputs from change_password form
        new_password = request.form.get("password")
        confirm_new_password = request.form.get("confirm_password")
        
        # Perform input validations:
        errors = False
        
        if not new_password or not confirm_new_password:
            flash("Must complete all fields", "negative")
            errors = True
            
        # Define regular expression pattern for a strong password
        password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        if not re.match(password_pattern, new_password):
            flash("New password must be at least 8 characters long and use at least one each of"
                  " upper-case letters, lower-case letters, numbers and symbols", "negative")
            errors = True
            
        if new_password != confirm_new_password:
            flash("Both passwords must be the same", "negative")
            errors = True
        
        if errors:
            return redirect(f"/change_password/{token}")
        
        # Generate password hash and update password_hash for the user
        hash = generate_password_hash(new_password)
        user.password_hash = hash
        db.session.commit()
        
        flash("Password has been changed", "positive")
        return redirect("/login")

@app.route('/')
@app.route('/index')
@login_required
def Index():
    return redirect("/workouts")

# Home page route, for allowing a user to add / edit / delete sets and view / copy workouts
@app.route('/workouts', methods = ["GET", "POST"])
@login_required
def Workouts():
    # Define boolean to keep track of whether the user has submitted the workouts form or not
    submitted = False 
    # Get string of the date of a week ago in YYYY-MM-DD format
    one_week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
    start_date = one_week_ago.strftime('%Y-%m-%d')
    # Get string of the current date in YYYY-MM-DD format
    current_date = datetime.datetime.today().strftime('%Y-%m-%d')
    # Define dictionary holding default values of fields in workouts form
    filter = {"exercise_or_category": "All", "start_date": start_date, "end_date": current_date}
    # Get a list of the names of the current user's exercises using the relationship between the User and Exercise models
    exercise_names = sorted([e.name for e in current_user.exercises])
    # Create list of exercise and category names (and "All")
    exercises_and_categories = sorted(exercise_names.copy() + categories + ["All"])
    # Create empty filtered_workouts dictionary
    filtered_workouts = {}

    if request.method == "POST":
        errors = False
        # Check if add_set form submitted
        if 'add_set' in request.form:
            exercise = request.form.get("exercise")
            weight = request.form.get("weight")
            reps = request.form.get("reps")
            date = request.form.get("date")
            if not exercise or not weight or not reps or not date:
                flash("Must complete all fields", "negative")
                errors = True
            if exercise not in exercise_names:
                flash("Must enter a valid exercise", "negative")
                errors = True
            if not is_positive_float(weight):
                flash("Weight must be a number greater than 0", "negative")
                errors = True
            if not is_positive_int(reps):
                flash("Reps must be a whole number greater than 0", "negative")
                errors = True
            if date > current_date:
                flash("Date must not be later than the current date", "negative")
                errors = True
            # Add new set if no errors have occured
            if not errors:
                estimated_1RM = float(weight) / (1.0278 - 0.0278 * int(reps)) # Calculate estimated 1RM using Brzycki formula
                exercise_id = Exercise.query.filter_by(name=exercise, user_id=current_user.user_id).first().exercise_id # Get exercise_id of the exercise
                date_object = datetime.datetime.strptime(date, "%Y-%m-%d").date() # Convert date to a datetime date object from a string
                # Create and add new set record
                new_set = Set(weight = round(float(weight), 1), reps = int(reps), estimated_1RM = round(estimated_1RM, 1), date = date_object, 
                              exercise_id = exercise_id, user_id = current_user.user_id)
                db.session.add(new_set)
                db.session.commit()
                flash("Set added", "positive")
        
        # Check if workouts form submitted
        if 'workouts' in request.form:
            submitted = True
            exercise_or_category = request.form.get("exercisecategory")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            if not exercise_or_category or not start_date or not end_date:
                flash("Must complete all fields", "negative")
                errors = True
            if exercise_or_category not in exercises_and_categories:
                flash("Must enter a valid exercise or category", "negative")
                errors = True
            if start_date > end_date or start_date > current_date or end_date > current_date:
                flash("Start date must not be later than end date, and neither can be later than current date", "negative")
                errors = True
            # Get sets if no errors have occured
            if not errors:
                # Update filter
                filter["exercise_or_category"] = exercise_or_category
                filter["start_date"] = start_date
                filter["end_date"] = end_date
                # Convert dates to correct format for database
                start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                # Build base query
                query = Set.query.join(Exercise).filter(
                    Set.user_id == current_user.user_id,
                    Set.date.between(start_date_obj, end_date_obj))
                if exercise_or_category in exercise_names:
                    query = query.filter(Exercise.name == exercise_or_category)
                elif exercise_or_category in categories:
                    query = query.filter(Exercise.category == exercise_or_category)
                    
                # Get all sets ordered by date from latest to oldest
                sets = query.order_by(Set.date.desc()).all()
                
                # Build filtered_workouts data structure:
                
                raw_workouts = defaultdict(lambda: defaultdict(list))
                for set in sets:
                    date_key = set.date.strftime('%d/%m/%Y') # Format dates in dd/mm/yyyy format
                    exercise_key = f"{set.exercise.name} ({set.exercise.category})" # Combine exercise names with their category
                    raw_workouts[date_key][exercise_key].append({
                        "weight":set.weight,
                        "reps": set.reps,
                        "estimated_1RM": set.estimated_1RM,
                        "set_id": set.set_id
                    })
                
                # Sort by date
                filtered_workouts = OrderedDict(sorted(raw_workouts.items(), key=lambda x: x[0], reverse=True))
                
        # Check if copy_workout form submitted
        if 'copy_workout' in request.form:
            old_workout_date = request.form.get("old_workout_date")
            new_workout_date = request.form.get("new_workout_date")
            errors = False
            if not new_workout_date:
                flash("Must enter a new date", "negative")
                errors = True
            if new_workout_date > current_date:
                flash("New date must not be later than current date", "negative")
                errors = False
            if not errors:
                # Convert dates to correct format
                old_workout_date_object = datetime.datetime.strptime(old_workout_date, "%d/%m/%Y").date()
                new_workout_date_object = datetime.datetime.strptime(new_workout_date, "%Y-%m-%d").date()
                # Get the sets which have to be copied using old_workout_date
                sets_to_copy = Set.query.filter_by(user_id=current_user.user_id, date=old_workout_date_object).all()
                for set in sets_to_copy:
                    new_set = Set(weight = set.weight, reps = set.reps, date = new_workout_date_object,
                        estimated_1RM = set.estimated_1RM, exercise_id = set.exercise_id, user_id = set.user_id)
                    db.session.add(new_set)
                db.session.commit()
                flash("Workout copied", "positive")
            
        # Check if edit_set form submitted
        if 'edit_set' in request.form:
            set_id = request.form.get("set_id")
            new_exercise = request.form.get("new_exercise")
            new_weight = request.form.get("new_weight")
            new_reps = request.form.get("new_reps")
            new_date = request.form.get("new_date")
            if not new_exercise or not new_weight or not new_reps or not new_date:
                flash("Must complete all fields", "negative")
                errors = True
            if new_exercise not in exercise_names:
                flash("Must enter a valid exercise", "negative")
                errors = True
            if not is_positive_float(new_weight):
                flash("Weight must be a number greater than 0", "negative")
                errors = True
            if not is_positive_int(new_reps):
                flash("Reps must be a whole number greater than 0", "negative")
                errors = True
            if new_date > current_date:
                flash("Date must not be later than the current date", "negative")
                errors = True
            # Edit set if no errors have occured
            if not errors:
                new_estimated_1RM = float(new_weight) / (1.0278 - 0.0278 * int(new_reps))
                new_exercise_id = Exercise.query.filter_by(name=new_exercise, user_id=current_user.user_id).first().exercise_id
                new_date_object = datetime.datetime.strptime(new_date, "%Y-%m-%d").date()
                # Get set to edit using its set_id
                set = db.session.get(Set, set_id)
                set.weight = round(float(new_weight), 1)
                set.reps = int(new_reps)
                set.estimated_1RM = round(new_estimated_1RM, 1)
                set.date = new_date_object
                set.exercise_id = new_exercise_id
                db.session.commit()
                flash("Set edited", "positive")
                
        # Check if delete_set button pressed (form submitted)
        if 'delete_set' in request.form:
            set_id = request.form.get("set_id")
            # Get set to delete using set_id
            set = db.session.get(Set, set_id)
            db.session.delete(set)
            db.session.commit()
            flash("Set deleted", "positive")
            
    return render_template("workouts.html", submitted=submitted, filter = filter, current_date = current_date, exercises=exercise_names, 
                           exercises_and_categories = exercises_and_categories, filtered_workouts = filtered_workouts)

# Route for allowing users to create, edit, delete and view their exercises
@app.route('/exercises', methods = ["GET", "POST"])
@login_required
def Exercises():
    if request.method == "GET":
        # Get user's exercises sorted by category and name
        exercises = sorted(current_user.exercises, key = lambda exercise: (exercise.category.lower(), exercise.name.lower()))
        # Create exercises_dict with categories as keys and lists of exercises as values
        exercises_dict = {}
        for exercise in exercises:
            exercises_dict.setdefault(exercise.category, []).append(exercise)
        return render_template("exercises.html", exercises_dict = exercises_dict, categories = categories)
    
    if request.method == "POST":
        categories_lower = [category.lower() for category in categories]
        # If create_exercise form submitted:
        if "create_exercise" in request.form:
            name = request.form.get("exercise_name").strip()
            category = request.form.get("category")
            errors = False
            if not name or not category:
                flash("Must complete all fields", "negative")
                errors = True
            # Check whether name contains only letters
            if not name.replace(" ", "").isalpha():
                flash("Name must contain only letters", "negative")
                errors = True
            # Check whether exercise name already exists or whether it is a category name
            name_exists = Exercise.query.filter(Exercise.user_id == current_user.user_id, Exercise.name.ilike(name.lower())).first()
            if name_exists or name.lower() in categories_lower:
                flash("An exercise or category with this name already exists", "negative")
                errors = True
            if not errors:
                # Create new exercise and add to database
                exercise = Exercise(name = name, category = category, user_id = current_user.user_id)
                db.session.add(exercise)
                db.session.commit()
                flash("Exercise created", "positive")

        # If edit_exercise popup form submitted:
        if "edit_exercise" in request.form:
            exercise_id = request.form.get("exercise_id")
            new_name = request.form.get("new_exercise_name").strip()
            new_category = request.form.get("new_category")
            exercise = db.session.get(Exercise, exercise_id)
            errors = False
            if not new_name or not new_category:
                flash("Must complete all fields", "negative")
                errors = True
            # Check whether name contains only letters
            if not new_name.replace(" ", "").isalpha():
                flash("Name must contain only letters", "negative")
                errors = True
            # Skip this check if the names are the same
            if new_name.lower() != exercise.name.lower():
                # Check whether exercise name already exists or whether it is a category name
                name_exists = Exercise.query.filter(Exercise.user_id == current_user.user_id, Exercise.name.ilike(new_name.lower())).first()
                if name_exists or new_name.lower() in categories_lower:
                    flash("An exercise or category with this name already exists", "negative")
                    errors = True
            if not errors:
                # Edit exercise
                exercise.name = new_name
                exercise.category = new_category
                db.session.commit()
                flash("Exercise edited", "positive")
        
        # If confirm_deletion popup form submitted:
        if "confirm_deletion" in request.form:
            exercise_id = request.form.get("deleted_exercise_id")
            confirmation = request.form.get("confirm_deletion")
            if confirmation == "Yes":
                # get the exercise using exercise_id and delete it
                exercise = db.session.get(Exercise, exercise_id)
                db.session.delete(exercise)
                db.session.commit()
                flash("Exercise deleted", "positive")
            else:
                flash("Deletion cancelled", "negative")
        return redirect("/exercises")

@app.route('/exercise_graph', methods = ["GET", "POST"])
@login_required
def Exercise_Graph():
    # Define boolean to keep track of whether the user has submitted the exercise_graph form or not
    submitted = False
    # Get string of the date of a month ago in YYYY-MM-DD format
    one_month_ago = datetime.date.today() - relativedelta(months=1)
    start_date = one_month_ago.strftime("%Y-%m-%d")
    # Get string of the current date in YYYY-MM-DD format
    current_date = datetime.datetime.today().strftime('%Y-%m-%d')
    # Define dictionary holding default values of fields in exercise_graph form
    filter = {"exercise": "", "metric": "", "start_date": start_date, "end_date": current_date}
    # Get a list of the names of the current user's exercises using the relationship between the User and Exercise models
    exercise_names = sorted([e.name for e in current_user.exercises])
    # Define list of available metrics
    metrics = ["Highest Estimated 1RM", "Highest Weight", "Highest Reps", "Sets", "Total Reps", "Total Volume"]
    # Create empty final_data 2d list
    final_data = []
    
    if request.method == "POST":
        submitted = True
        exercise = request.form.get("exercise")
        metric = request.form.get("metric")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        errors = False
        if not exercise or not metric or not start_date or not end_date:
            flash("Must complete all fields", "negative")
            errors = True
        if exercise not in exercise_names:
            flash("Must enter a valid exercise", "negative")
            errors = True
        if start_date > end_date or start_date > current_date or end_date > current_date:
            flash("Start date must not be later than end date, and neither can be later than current date", "negative")
            errors = True
        if not errors:
            # Update values in filter
            filter["exercise"] = exercise
            filter["metric"] = metric
            filter["start_date"] = start_date
            filter["end_date"] = end_date
            # Convert dates to correct format for database
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            # Get the exercise_id of the exercise
            exercise_id = Exercise.query.filter_by(name=exercise, user_id=current_user.user_id).first().exercise_id
            # Create and execute query to get all sets for the exercise within the date range
            query = Set.query.filter(Set.exercise_id == exercise_id, Set.date.between(start_date_obj, end_date_obj))
            sets = query.all()
            
            # Get all unique dates from the sets, and sort them from oldest to newest
            unique_dates = sorted(set(set.date for set in sets))
            for date in unique_dates:
                # Create a new list of only the sets that match the date
                sets_on_date = [set for set in sets if set.date == date]
                # Check which metric needs to be calculated and calculate the value for the date
                if metric == "Highest Estimated 1RM":
                    metric_value = max(set.estimated_1RM for set in sets_on_date)
                elif metric == "Highest Weight":
                    metric_value = max(set.weight for set in sets_on_date)
                elif metric == "Highest Reps":
                    metric_value = max(set.reps for set in sets_on_date)
                elif metric == "Sets":
                    metric_value = len(sets_on_date)
                elif metric == "Total Reps":
                    metric_value = sum(set.reps for set in sets_on_date)
                elif metric == "Total Volume":
                    metric_value = sum(set.weight * set.reps for set in sets_on_date)
                # Append entry to final_data
                final_data.append([date.strftime("%Y-%m-%d"), round(metric_value, 1)])

    return render_template("exercise_graph.html", submitted = submitted, filter= filter, exercises=exercise_names, metrics = metrics, set_data = final_data)

@app.route('/workout_graph', methods = ["GET", "POST"])
@login_required
def Workout_Graph():
    # Define boolean to keep track of whether the user has submitted the workout_graph form or not
    submitted = False
    # Get string of the date of a month ago in YYYY-MM-DD format
    one_month_ago = datetime.date.today() - relativedelta(months=1)
    start_date = one_month_ago.strftime("%Y-%m-%d")
    # Get string of the current date in YYYY-MM-DD format
    current_date = datetime.datetime.today().strftime('%Y-%m-%d')
    # Define dictionary holding default values of fields in workout_graph form
    filter = {"metric": "", "start_date": start_date, "end_date": current_date}
    # Define list of available metrics
    metrics = ["Total Sets", "Total Reps", "Total Volume"]
    # Create empty final_data 2d list
    final_data = []
    
    if request.method == "POST":
        submitted = True
        metric = request.form.get("metric")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        errors = False
        if not metric or not start_date or not end_date:
            flash("Must complete all fields", "negative")
            errors = True
        if start_date > end_date or start_date > current_date or end_date > current_date:
            flash("Start date must not be later than end date, and neither can be later than current date", "negative")
            errors = True
        if not errors:
            # Update values in filter
            filter["metric"] = metric
            filter["start_date"] = start_date
            filter["end_date"] = end_date
            # Convert dates to correct format for database
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            # Create and execute query to get all of the users sets within the date range
            query = Set.query.filter(Set.user_id == current_user.user_id, Set.date.between(start_date_obj, end_date_obj))
            sets = query.all()
            
            # Get all unique dates from the sets, and sort them from oldest to newest
            unique_dates = sorted(set(set.date for set in sets))
            for date in unique_dates:
                # Create a new list of only the sets that match the date
                sets_on_date = [set for set in sets if set.date == date]
                # Check which metric needs to be calculated and calculate the value for the date
                if metric == "Total Sets":
                    metric_value = len(sets_on_date)
                elif metric == "Total Reps":
                    metric_value = sum(set.reps for set in sets_on_date)
                elif metric == "Total Volume":
                    metric_value = sum(set.weight * set.reps for set in sets_on_date)
                # Append entry to final_data
                final_data.append([date.strftime("%Y-%m-%d"), round(metric_value, 1)])

    
    return render_template("workout_graph.html", submitted = submitted, filter= filter, metrics = metrics, set_data = final_data)

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