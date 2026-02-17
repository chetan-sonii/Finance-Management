from flask import render_template, request, flash, redirect, url_for
from . import public_bp


@public_bp.route("/")
def index():
    return render_template("public/index.html")


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = (request.form.get("name")    or "").strip()
        email   = (request.form.get("email")   or "").strip()
        subject = (request.form.get("subject") or "").strip()
        topic   = (request.form.get("topic")   or "general").strip()
        message = (request.form.get("message") or "").strip()

        if not name or not email or not message:
            flash("Please fill in your name, email and message.", "warning")
            return redirect(url_for("public.contact"))

        from app.models import ContactMessage
        from app.extensions import db

        msg = ContactMessage(
            name=name,
            email=email,
            subject=subject or None,
            topic=topic,
            message=message,
        )
        db.session.add(msg)
        db.session.commit()

        flash(
            f"Thank you, {name}! Your message has been received. "
            "We'll get back to you soon.",
            "success",
        )
        return redirect(url_for("public.contact"))

    return render_template("public/contact.html")
