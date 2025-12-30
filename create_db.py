# create_db.py


from project.config import app, db
from project import models


with app.app_context():
    # create the database and the db table
    db.create_all()

    # commit the changes
    db.session.commit()
