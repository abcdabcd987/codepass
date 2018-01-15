import os
import pytz
import datetime


class Settings:
    BASEDIR = os.path.realpath(os.path.dirname(__file__))
    WEBSITE_NAME = 'Online Judge'
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://username:mypassword@localhost/dike-oj'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/dike-oj.db'
    SECRET_KEY = 'you can copy from: python -c "print(repr(__import__(\"os\").urandom(30)))"'
    WEBROOT = ''
