#tutorial/config.py
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'erraetst-Du-nie'
    hostname = os.environ.get('hostname')
    sql_username = os.environ.get('sql_username')
    sql_password = os.environ.get('sql_password')
    database_name = 'snackrate'
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{sql_username}:{sql_password}@{hostname}:3306/{database_name}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ADMINS = ['admin@does.not.exist.com']
    SNACKS_PER_PAGE = 25
