from .user_routes import user_bp
from .roles_routes import roles_bp

# Import any other blueprints you may have


def register_blueprints(app):
    """Function to register all blueprints."""
    app.register_blueprint(user_bp)
    app.register_blueprint(roles_bp)
