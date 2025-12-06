from datetime import datetime
from app.utils import is_safe_url


from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

from . import auth_bp
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash


def redirect_after_login(user: User):
    """Redirect user based on role after login."""
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("dashboard.home"))



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_after_login(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # NEW: remember checkbox
        remember = True if request.form.get("remember") else False

        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("No account found with that email.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("This account is deactivated. Please contact admin.", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password_hash, password):
            flash("Incorrect password.", "danger")
            return redirect(url_for("auth.login"))

        # Successful login — NOW WITH REMEMBER ME
        login_user(user, remember=remember)

        user.last_login_at = datetime.utcnow()
        db.session.commit()

        flash("Logged in successfully.", "success")

        # Check if Flask-Login provided ?next=
        next_page = request.args.get("next")
        if next_page and is_safe_url(next_page):
            return redirect(next_page)

        return redirect_after_login(user)

    return render_template("auth/login.html")




@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect_after_login(current_user)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Name, email, and password are required.", "warning")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return redirect(url_for("auth.register"))

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            name=name,
            email=email,
            phone=phone,
            role="customer",
            password_hash=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    # GET
    return render_template("auth/register.html")



@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.index"))
