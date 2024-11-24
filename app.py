from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user
import os

class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

basedirectory = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-wont-ever-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedirectory, 'tracker.db')
db.init_app(app)
login = LoginManager(app)

class User(UserMixin, db.Model):
    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique = True)
    password_hash: Mapped[str]

    def __repr__(self):
      return f'<Users {self.username}>'
      
    def set_password(self, password):
      self.password_hash = generate_password_hash(password)

    def check_password(self, password):
      return check_password_hash(self.password_hash, password)
      
class LoginForm(FlaskForm):
  email = StringField('Email address', validators=[DataRequired()])
  password = StringField('Password', validators=[DataRequired()])
  remember_me=BooleanField('Remember Me')
  submit = SubmitField('Sign In')


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')
  
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
      return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
      user = db.session.scalar(
        sqlalchemy.select(User).where(User.email == form.email.data))
      if user is None or not user.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('login'))
      login_user(user, remember=form.remember_me.data)
      return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)