from pathlib import Path
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# configuration
DATABASE = "shareSpace.db"
SECRET_KEY = "change_me"

basedir = Path(__file__).resolve().parent
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{Path(basedir).joinpath(DATABASE)}")

# create and initialize a new Flask app
app = Flask(__name__)
# load the config
app.config.from_object(__name__)
# init sqlalchemy
db = SQLAlchemy(app)