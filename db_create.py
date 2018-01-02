# Set up database.

from app import db
from models import *
import os

# Drop all existing tables and then make table based off of models (WARNING! Will delete old data if table already exists!)

db.drop_all()
db.create_all()

# no items to initially insert

# commit

db.session.commit()

