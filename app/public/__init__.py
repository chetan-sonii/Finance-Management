from flask import Blueprint

public_bp = Blueprint("public", __name__)

from . import routes  # noqa: E402,F401  (import routes after blueprint is created)
