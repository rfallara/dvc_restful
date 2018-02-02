import os

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
PORT = 5000
HOST = "127.0.0.1"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER="dvcuser", DB_PASS="dvc123", DB_ADDR="35.224.69.151", DB_NAME="dvc")
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

