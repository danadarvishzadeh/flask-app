from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import config

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from .models import Discussion, Post, User, Invitation, Participate, Follow
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    from discussion.api.views import api_bp
    from discussion.auth.views import auth_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
