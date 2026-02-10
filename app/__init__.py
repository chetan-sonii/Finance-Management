# app/__init__.py
import os
from flask import Flask
from datetime import datetime

from app.extensions import db, login_manager, migrate
from config import DevelopmentConfig


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)

    # ---- Load config ----
    app.config.from_object(config_class)

    # ---- Context processors ----
    @app.context_processor
    def inject_now():
        return {"current_year": datetime.utcnow().year}

    # ---- Ensure instance folder ----
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # ---- Init extensions ----
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # ---- User loader ----
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

    # ---- Register blueprints ----
    from .public import public_bp
    from .auth import auth_bp
    from .dashboard import dashboard_bp
    from .admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
