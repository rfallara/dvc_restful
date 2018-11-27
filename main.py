from os import environ
from app import create_app
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import gcp_auth

app = create_app('config')
CORS(app)
app.config['JWT_SECRET_KEY'] = gcp_auth.token_secret
jwt = JWTManager(app)


if environ.get('DEV_SERVER') is not None:
    print('DEVELOPMENT ENVIRONMENT')
    print(__name__)
    app.run()
else:
    print('PRODUCTION ENVIRONMENT')

# app.run()

# print(__name__)
# if __name__ == '__main__':
#     app.run(host=app.config['HOST'],
#             port=app.config['PORT'],
#             debug=app.config['DEBUG'])
#
# if __name__ == 'builtins':
#     app.app_context().push()
