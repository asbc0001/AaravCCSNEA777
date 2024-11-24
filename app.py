from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import os

class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

basedirectory = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-wont-ever-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedirectory, 'tracker.db')
db.init_app(app)

class User(db.Model):
    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique = True)
    password_has: Mapped[str]
    
    def __repr__(self):
        return f'<Users {self.username}>'
      
class LoginForm(FlaskForm):
  email = StringField('Email address', validators=[DataRequired()])
  password = StringField('Password', validators=[DataRequired()])
  remember_me=BooleanField('Remember Me')
  submit = SubmitField('Sign In')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')
  
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      flash('Login requested for user {}, remember_me={}'.format(form.email.data, form.remember_me.data))
      return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)