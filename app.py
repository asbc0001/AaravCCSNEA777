from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import os

basedirectory = os.path.abspath(os.path.dirname(__file__))

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
#app.config['SECRET_KEY'] = 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedirectory, 'tracker.db')
db.init_app(app)

class User(db.Model):
    user_id: Mapped[int] = mapped_column(primary_key=True)
    #username = db.Column(db.String(100), nullable = False)
    username: Mapped[str] = mapped_column(unique = True)
    #email = db.Column(db.String(200), nullable = False)
    email: Mapped[str] = mapped_column(unique = True)
    
    def __repr__(self):
        return f'<Users {self.username}>'


@app.route("/")
def index():
    return render_template('index.html', title='Home')