from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import gcp_auth
from models import db
from views import api_bp

app = Flask(__name__)
app.config.from_object('config')
CORS(app)
db.init_app(app)
app.register_blueprint(api_bp, url_prefix='/api')


app.config['JWT_SECRET_KEY'] = gcp_auth.token_secret
jwt = JWTManager(app)

if app.config['ENV'].upper() == 'DEVELOPMENT':
    print('FLASK DEVELOPMENT ENVIRONMENT')
else:
    print('FLASK PRODUCTION ENVIRONMENT')

# app.run()

# print(__name__)
# if __name__ == '__main__':
#     app.run(host=app.config['HOST'],
#             port=app.config['PORT'],
#             debug=app.config['DEBUG'])
#
# if __name__ == 'builtins':
#     app.app_context().push()
