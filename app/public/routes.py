from flask import render_template
from . import public_bp


@public_bp.route("/")
def index():
    # This will render templates/public/index.html
    return render_template("public/index.html")


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact")
def contact():
    return render_template("public/contact.html")
