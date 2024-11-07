import os

basedirectory = os.path.abspath(os.path.dirname(__file__))

class Configuration:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedirectory, 'tracker.db')