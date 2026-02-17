# app/dashboard/routes.py
import os
from datetime import datetime,date,timedelta
from app.models import InvestmentOption,Reminder,Expense,ExpenseCategory
from flask import (
    redirect,
    url_for,
    render_template,
    current_app,
    request,
    flash,
    Response,
    jsonify,
)
import csv
from io import StringIO
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from . import dashboard_bp
from app.extensions import db
from sqlalchemy import func


# ---------- Helpers ----------

def allowed_avatar_file(filename: str) -> bool:
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    allowed = current_app.config.get("ALLOWED_IMAGE_EXTENSIONS", {"png", "jpg", "jpeg", "gif"})
    return "." in filename and ext in allowed


# ---------- Main dashboard routes ----------

@dashboard_bp.route("/")
@login_required
def home():
    # Default tab
    return redirect(url_for("dashboard.profile"))


@dashboard_bp.route("/profile")
@login_required
def profile():
    # You can compute extra stats later (expenses count, reminders etc.)
    return render_template("dashboard/profile.html")

@dashboard_bp.route("/expenses")
@login_required
def expenses():
    """
    Show expense calculator + recent monthly history for this user.
    """
    # Group all saved expenses by year+month and show last 6 periods
    recent = (
        db.session.query(
            func.year(Expense.expense_date).label("y"),
            func.month(Expense.expense_date).label("m"),
            func.min(Expense.expense_date).label("first_date"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(Expense.user_id == current_user.id)
        .group_by("y", "m")
        .order_by(func.min(Expense.expense_date).desc())
        .limit(6)
        .all()
    )

    history = []
    for r in recent:
        period = f"{int(r.y):04d}-{int(r.m):02d}"  # e.g. "2025-12"
        history.append(
            {
                "period": period,
                "date": r.first_date,          # any date from that month
                "total": float(r.total or 0),
            }
        )

    return render_template("dashboard/expenses.html", history=history)



@dashboard_bp.route("/compound")
@login_required
def compound():
    return render_template("dashboard/compound.html")


@dashboard_bp.route("/advisor")
@login_required
def advisor():
    options = (
        InvestmentOption.query
        .filter_by(is_active=True)
        .order_by(InvestmentOption.sort_order, InvestmentOption.id)
        .all()
    )
    return render_template("dashboard/advisor.html", options=options)



@dashboard_bp.route("/calendar")
@login_required
def calendar():
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.reminder_date).all()
    return render_template("dashboard/calendar.html", reminders=reminders)



@dashboard_bp.route("/overview")
@login_required
def overview():
    return render_template("dashboard/overview.html")

@dashboard_bp.route("/overview/summary")
@login_required
def overview_summary():
    """High-level stats for top cards."""
    user_id = current_user.id
    today = date.today()

    # Current month boundaries
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        next_month_start = date(today.year + 1, 1, 1)
    else:
        next_month_start = date(today.year, today.month + 1, 1)

    # Previous month boundaries
    if today.month == 1:
        prev_start = date(today.year - 1, 12, 1)
        prev_end = month_start
    else:
        prev_start = date(today.year, today.month - 1, 1)
        prev_end = month_start

    # Totals for current month
    total_month = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.user_id == user_id,
            Expense.expense_date >= month_start,
            Expense.expense_date < next_month_start,
        )
        .scalar()
        or 0
    )

    # Previous month total
    prev_month_total = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.user_id == user_id,
            Expense.expense_date >= prev_start,
            Expense.expense_date < prev_end,
        )
        .scalar()
        or 0
    )

    # Month-over-month change %
    if prev_month_total > 0:
        month_change = ((total_month - prev_month_total) / prev_month_total) * 100
    else:
        month_change = 0.0

    # Daily average for this month (based on days passed including today)
    days_passed = (today - month_start).days + 1
    daily_average = float(total_month) / days_passed if days_passed > 0 else 0.0

    # Upcoming reminders
    now = datetime.utcnow()
    upcoming_q = (
        Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.reminder_date >= now,
        )
        .order_by(Reminder.reminder_date.asc())
    )

    upcoming_count = upcoming_q.count()
    next_reminder = upcoming_q.first()

    if next_reminder:
        next_obj = {
            "title": next_reminder.title,
            "when": next_reminder.reminder_date.strftime("%d %b, %I:%M %p"),
        }
    else:
        next_obj = None

    # Top category (current month)
    cat_rows = (
        db.session.query(
            ExpenseCategory.name,
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .join(Expense, Expense.category_id == ExpenseCategory.id)
        .filter(
            Expense.user_id == user_id,
            Expense.expense_date >= month_start,
            Expense.expense_date < next_month_start,
        )
        .group_by(ExpenseCategory.id, ExpenseCategory.name)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    top_category = None
    top_category_amount = 0.0
    if cat_rows:
        top_category, top_category_amount = cat_rows[0].name, float(cat_rows[0].total)

    return jsonify(
        {
            "total_month": float(total_month),
            "prev_month_total": float(prev_month_total),
            "month_change": float(month_change),
            "daily_average": float(daily_average),
            "upcoming_count": int(upcoming_count),
            "next_reminder": next_obj,
            "top_category": top_category,
            "top_category_amount": float(top_category_amount),
        }
    )

@dashboard_bp.route("/overview/expense_trend")
@login_required
def overview_expense_trend():
    """Monthly totals for last 6 months (including current)."""
    user_id = current_user.id
    today = date.today()

    labels = []
    values = []

    # 5,4,3,2,1,0 months ago
    for offset in range(5, -1, -1):
        # compute year/month offset months ago
        month = today.month - offset
        year = today.year
        while month <= 0:
            month += 12
            year -= 1

        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        total = (
            db.session.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(
                Expense.user_id == user_id,
                Expense.expense_date >= start,
                Expense.expense_date < end,
            )
            .scalar()
            or 0
        )

        labels.append(start.strftime("%b %Y"))
        values.append(float(total))

    return jsonify({"labels": labels, "values": values})
@dashboard_bp.route("/overview/category_breakdown")
@login_required
def overview_category_breakdown():
    """Category-wise totals for current month."""
    user_id = current_user.id
    today = date.today()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        next_month_start = date(today.year + 1, 1, 1)
    else:
        next_month_start = date(today.year, today.month + 1, 1)

    rows = (
        db.session.query(
            ExpenseCategory.name,
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .join(Expense, Expense.category_id == ExpenseCategory.id)
        .filter(
            Expense.user_id == user_id,
            Expense.expense_date >= month_start,
            Expense.expense_date < next_month_start,
        )
        .group_by(ExpenseCategory.id, ExpenseCategory.name)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    labels = [row.name for row in rows]
    values = [float(row.total) for row in rows]

    # If there are expenses without category, you can optionally add an "Uncategorized" bucket here.

    return jsonify({"labels": labels, "values": values})

@dashboard_bp.route("/overview/reminders_list")
@login_required
def overview_reminders_list():
    """Next few reminders used in overview list."""
    user_id = current_user.id
    now = datetime.utcnow()
    end = now + timedelta(days=30)

    reminders = (
        Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.reminder_date >= now,
            Reminder.reminder_date <= end,
        )
        .order_by(Reminder.reminder_date.asc())
        .limit(6)
        .all()
    )

    items = []
    for r in reminders:
        items.append(
            {
                "title": r.title,
                "description": r.description or "",
                "when": r.reminder_date.strftime("%d %b %Y, %I:%M %p"),
            }
        )

    return jsonify({"items": items})

@dashboard_bp.route("/overview/recent_expenses")
@login_required
def overview_recent_expenses():
    """Latest expenses for the table in overview."""
    user_id = current_user.id

    # join category for name
    rows = (
        db.session.query(
            Expense,
            ExpenseCategory.name.label("category_name"),
        )
        .outerjoin(ExpenseCategory, Expense.category_id == ExpenseCategory.id)
        .filter(Expense.user_id == user_id)
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .limit(8)
        .all()
    )

    items = []
    for exp, cat_name in rows:
        items.append(
            {
                "date": exp.expense_date.strftime("%d %b %Y")
                if exp.expense_date
                else "",
                "category": cat_name,
                "title": exp.title or "",
                "amount": float(exp.amount or 0),
            }
        )

    return jsonify({"items": items})

# ---------- Profile actions ----------

@dashboard_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    name = (request.form.get("name") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    

    if not name:
        flash("Name cannot be empty.", "warning")
        return redirect(url_for("dashboard.profile"))

    current_user.name = name
    current_user.phone = phone if phone else None
    current_user.updated_at = datetime.utcnow()


    db.session.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for("dashboard.profile"))

@dashboard_bp.route("/profile/avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")

    if not file or file.filename == "":
        flash("Please choose an image file to upload.", "warning")
        return redirect(url_for("dashboard.profile"))

    if not allowed_avatar_file(file.filename):
        flash("Invalid image type. Please upload PNG, JPG, or GIF.", "danger")
        return redirect(url_for("dashboard.profile"))

    filename = secure_filename(file.filename)
    if "." not in filename:
        flash("Uploaded file has no extension.", "danger")
        return redirect(url_for("dashboard.profile"))

    ext = filename.rsplit(".", 1)[-1].lower()
    new_filename = f"user_{current_user.id}.{ext}"

    # Resolve upload folder to absolute path (helps with relative-config bugs)
    upload_folder_cfg = current_app.config.get("AVATAR_UPLOAD_FOLDER", "uploads/avatars")
    upload_folder = os.path.abspath(
        os.path.join(current_app.root_path, upload_folder_cfg)
        if not os.path.isabs(upload_folder_cfg)
        else upload_folder_cfg
    )
    current_app.logger.debug("Avatar upload folder resolved to: %s", upload_folder)

    try:
        os.makedirs(upload_folder, exist_ok=True)
    except Exception:
        current_app.logger.exception("Could not create upload folder: %s", upload_folder)
        flash("Server error creating upload folder. Contact admin.", "danger")
        return redirect(url_for("dashboard.profile"))

    file_path = os.path.join(upload_folder, new_filename)

    # Delete old avatar if it's not the default
    old_filename = getattr(current_user, "avatar_filename", None)
    if old_filename and old_filename != "default.jpg":
        old_path = os.path.join(upload_folder, old_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                current_app.logger.exception("Failed to remove old avatar: %s", old_path)

    # Save new file with error handling
    try:
        file.save(file_path)
        # double-check that the file exists on disk
        if not os.path.exists(file_path):
            raise IOError("file.save() completed but file not found on disk")
        # optionally fsync to ensure write (usually unnecessary)
        # with open(file_path, "rb+") as f:
        #     os.fsync(f.fileno())
    except Exception:
        current_app.logger.exception("Failed to save uploaded avatar to %s", file_path)
        flash("Failed to save the uploaded file to the server.", "danger")
        return redirect(url_for("dashboard.profile"))

    # Update the user model and commit safely
    try:
        current_user.avatar_filename = new_filename
        current_user.updated_at = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()
    except Exception:
        current_app.logger.exception("Database commit failed after avatar upload")
        db.session.rollback()
        # Optionally remove the file because DB didn't persist the change
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            current_app.logger.exception("Failed to remove orphaned avatar after DB error")
        flash("Could not update profile (database error).", "danger")
        return redirect(url_for("dashboard.profile"))

    current_app.logger.info("Avatar updated for user %s -> %s", current_user.id, new_filename)
    flash("Profile picture updated.", "success")
    return redirect(url_for("dashboard.profile"))



@dashboard_bp.route("/profile/delete", methods=["POST"])
@login_required
def delete_account():
    # ----------------------------------------------------------------
    # IMPORTANT: capture everything from current_user BEFORE calling
    # logout_user(), because that turns current_user into an
    # AnonymousUserMixin and all attribute access will crash.
    # ----------------------------------------------------------------
    user_id         = current_user.id
    avatar_filename = current_user.avatar_filename

    confirm = (request.form.get("confirm") or "").strip().upper()
    if confirm != "DELETE":
        flash("Type DELETE in the box to confirm account deletion.", "warning")
        return redirect(url_for("dashboard.profile"))

    # Re-fetch a fresh User instance tied to this db session
    from app.models import User, Expense, Reminder, CICalculation
    user = db.session.get(User, user_id)   # SQLAlchemy 2.x compatible
    if user is None:
        # Fallback for older SQLAlchemy
        user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        flash("User account not found.", "danger")
        return redirect(url_for("public.index"))

    # Log out first (Flask-Login session cleared)
    logout_user()

    # Delete avatar file from disk
    upload_folder = current_app.config.get("AVATAR_UPLOAD_FOLDER", "")
    if avatar_filename and avatar_filename != "default.jpg" and upload_folder:
        old_path = os.path.join(upload_folder, avatar_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    # Expunge the user object so SQLAlchemy's cascade doesn't try to
    # delete children that we're about to bulk-delete ourselves.
    # This avoids "Instance is already deleted" errors.
    db.session.expunge(user)

    # Bulk-delete all child records (works even without DB-level cascade)
    db.session.query(Expense).filter_by(user_id=user_id).delete(synchronize_session="fetch")
    db.session.query(Reminder).filter_by(user_id=user_id).delete(synchronize_session="fetch")
    db.session.query(CICalculation).filter_by(user_id=user_id).delete(synchronize_session="fetch")

    # Re-fetch user cleanly after expunge and delete
    user = db.session.query(User).filter_by(id=user_id).first()
    if user:
        db.session.delete(user)

    db.session.commit()

    flash("Your account has been permanently deleted.", "info")
    return redirect(url_for("public.index"))

@dashboard_bp.route("/expenses/current_month")
@login_required
def expenses_current_month():
    """Return today's saved expenses as JSON for the calculator."""
    today = date.today()
    rows = (
        Expense.query
        .filter(
            Expense.user_id == current_user.id,
            Expense.expense_date == today,
        )
        .order_by(Expense.id.asc())
        .all()
    )
    items = [{"title": e.title or "", "amount": float(e.amount or 0)} for e in rows]
    return jsonify({"items": items})


@dashboard_bp.route("/expenses/save", methods=["POST"])
@login_required
def save_expenses():
    # Get arrays from the form (names: types[] and amounts[])
    types = request.form.getlist("types[]")
    amounts = request.form.getlist("amounts[]")

    entries = []
    for t, a in zip(types, amounts):
        label = (t or "").strip()

        try:
            value = float(a)
        except (TypeError, ValueError):
            continue

        if not label or value <= 0:
            continue

        entries.append((label, value))

    if not entries:
        flash("No valid expenses to save.", "warning")
        return redirect(url_for("dashboard.expenses"))

    # Optional: clear existing expenses for today to avoid duplicates
    # (You can comment this block out if you prefer to keep all versions)
    db.session.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date == date.today(),
    ).delete()

    # Insert new rows
    for label, value in entries:
        expense = Expense(
            user_id=current_user.id,
            title=label,          # <-- maps to your model's 'title' field
            amount=value,         # Numeric(10,2) – float is fine here
            expense_date=date.today(),
            # category_id=None,
            # notes=None,
        )
        db.session.add(expense)

    db.session.commit()
    flash("Expenses saved successfully.", "success")
    return redirect(url_for("dashboard.expenses"))


@dashboard_bp.route("/expenses/export")
@login_required
def expenses_export_csv():
    """
    Export all expenses for a given YYYY-MM period as CSV.
    """
    period = request.args.get("period")
    if not period:
        flash("No period selected for export.", "warning")
        return redirect(url_for("dashboard.expenses"))

    try:
        year_str, month_str = period.split("-")
        year = int(year_str)
        month = int(month_str)
    except ValueError:
        flash("Invalid period format for export.", "danger")
        return redirect(url_for("dashboard.expenses"))

    # Filter expenses for that month
    expenses_q = (
        Expense.query
        .filter(Expense.user_id == current_user.id)
        .filter(func.year(Expense.expense_date) == year,
                func.month(Expense.expense_date) == month)
        .order_by(Expense.expense_date.asc(), Expense.id.asc())
        .all()
    )

    # Build CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Date", "Title", "Amount"])

    for exp in expenses_q:
        writer.writerow([
            exp.expense_date.isoformat(),
            exp.title or "",
            float(exp.amount),
        ])

    output = si.getvalue()
    filename = f"expenses_{period}.csv"

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )



@dashboard_bp.route("/calendar/events")
@login_required
def calendar_events():
    events = Reminder.query.filter_by(user_id=current_user.id).all()

    result = [
        {
            "id": r.id,
            "title": r.title,
            "start": r.reminder_date.isoformat(),
            "description": r.description or "",
        }
        for r in events
    ]

    return jsonify(result)


@dashboard_bp.route("/calendar/add", methods=["POST"])
@login_required
def add_reminder():
    title = (request.form.get("title") or "").strip()
    desc = (request.form.get("description") or "").strip()
    date_str = request.form.get("date")

    if not title:
        return jsonify({"status": "error", "message": "Title is required"}), 400

    try:
        date_obj = datetime.fromisoformat(date_str)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid date"}), 400

    new_r = Reminder(
        user_id=current_user.id,
        title=title,
        description=desc or None,
        reminder_date=date_obj,
    )
    db.session.add(new_r)
    db.session.commit()

    return jsonify({
        "status": "success",
        "reminder": {
            "id": new_r.id,
            "title": new_r.title,
            "description": new_r.description or "",
            "reminder_date_display": new_r.reminder_date.strftime("%d %b %Y, %I:%M %p"),
            "reminder_date_badge": new_r.reminder_date.strftime("%d %b"),
            "reminder_date_iso": new_r.reminder_date.isoformat(),
        }
    })

@dashboard_bp.route("/calendar/edit/<int:id>", methods=["POST"])
@login_required
def edit_reminder(id):
    reminder = Reminder.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    title    = (request.form.get("title")       or "").strip()
    desc     = (request.form.get("description") or "").strip()
    date_str = request.form.get("date")

    if not title:
        return jsonify({"status": "error", "message": "Title is required"}), 400

    try:
        reminder.reminder_date = datetime.fromisoformat(date_str)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid date"}), 400

    reminder.title       = title
    reminder.description = desc or None
    db.session.commit()

    return jsonify({
        "status": "success",
        "reminder": {
            "id": reminder.id,
            "title": reminder.title,
            "description": reminder.description or "",
            "reminder_date_display": reminder.reminder_date.strftime("%d %b %Y, %I:%M %p"),
            "reminder_date_badge":   reminder.reminder_date.strftime("%d %b"),
            "reminder_date_iso":     reminder.reminder_date.isoformat(),
        }
    })

@dashboard_bp.route("/calendar/delete/<int:id>", methods=["POST"])
@login_required
def delete_reminder(id):
    reminder = Reminder.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({"status": "success"})
