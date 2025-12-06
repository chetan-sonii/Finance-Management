import os
from flask import Flask
from .extensions import db, login_manager
from datetime import datetime


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    @app.context_processor
    def inject_now():
        return {"current_year": datetime.utcnow().year}

    app.config.from_mapping(
        SECRET_KEY="dev-change-this-key",
        SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://chetan:Chetan_123@localhost:3307/disha_finance",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # NEW: avatar upload settings
    app.config["AVATAR_UPLOAD_FOLDER"] = os.path.join(
        app.static_folder, "uploads", "avatars"
    )
    app.config["ALLOWED_IMAGE_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

    @app.context_processor
    def inject_now():
        return {"current_year": datetime.utcnow().year}

    # ---- Basic config for now ----
    app.config.from_mapping(
        SECRET_KEY="dev-change-this-key",  # change in production
        SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://chetan:Chetan_123@localhost:3307/disha_finance",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # ---- Init extensions ----
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # ---- Real user_loader using User model ----
    from .models import User  # import here to avoid circular import


    @login_manager.user_loader
    def load_user(user_id: str):
        # Flask-Login stores user_id in session as string
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
