from flask import Flask
from flask_cors import CORS


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    CORS(app)

    from models import db
    db.init_app(app)

    from views import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

