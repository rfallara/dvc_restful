import os

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
PORT = 5000
HOST = "127.0.0.1"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER="***REMOVED***", DB_PASS="***REMOVED***", DB_ADDR="127.0.0.1", DB_NAME="dvctest")
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
