from flask import Flask
from flasgger import Swagger
from .extensions import db, migrate, bcrypt
from .config import Config
from .routes import register_blueprints

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Victory APIs",
        "description": "API documentation",
        "version": "1.0.0",
    },
    "basePath": "/",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Token header using the Bearer scheme. Example: 'Bearer {token}'",
        }
    },
    "security": [{"Bearer": []}],
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,  # include all endpoints
            "model_filter": lambda tag: True,  # include all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Adding Swagger
    Swagger(app, template=swagger_template, config=swagger_config)

    return app
