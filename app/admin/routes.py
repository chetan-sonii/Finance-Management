# app/admin/routes.py
from flask_login import login_required
from app.utils import admin_required
from . import admin_bp  # use the blueprint from __init__.py


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    # Later: admin stats page
    return "<h1>Admin Dashboard (placeholder)</h1>"
    # later: return render_template("admin/dashboard.html")
