import os
import gcp_auth

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = False
# PORT = 5000
# HOST = "127.0.0.1"
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# postgres://***REMOVED***
# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(
SQLALCHEMY_DATABASE_URI = "postgres://{DB_USER}:{DB_PASS}@{DB_ADDR}:5432/{DB_NAME}".format(
    DB_USER=gcp_auth.gcp_db['username'],
    DB_PASS=gcp_auth.gcp_db['password'],
    DB_ADDR=gcp_auth.gcp_db['db_addr'],
    DB_NAME=gcp_auth.gcp_db['db_name'])
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_POOL_RECYCLE = 60

print('ACTIVE DB: ' + gcp_auth.gcp_db['db_name'])
