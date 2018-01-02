# Configuration.

import os

# Base configuration
class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = '<Insert Secret Key Here>' # Insert secret key here.
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    print(SQLALCHEMY_DATABASE_URI)

# For development
class DevelopmentConfig(BaseConfig):
    DEBUG = True

# For production
class ProductionConfig(BaseConfig):
    DEBUG = False