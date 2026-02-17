"""
models.py – SQLAlchemy ORM models for Disha Finance
All relationships use cascade="all, delete-orphan" on the parent side so that
deleting a User automatically removes their child records both at the ORM and
(if the DB supports it) at the FK-constraint level.
"""

from datetime import datetime, date
from flask_login import UserMixin
from .extensions import db


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(150), unique=True, nullable=False)
    phone           = db.Column(db.String(20), nullable=True)
    password_hash   = db.Column(db.String(255), nullable=False)
    role            = db.Column(
                        db.Enum("customer", "admin", name="user_role"),
                        nullable=False,
                        default="customer",
                    )
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(
                        db.DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow,
                    )
    last_login_at   = db.Column(db.DateTime, nullable=True)
    is_active       = db.Column(db.Boolean, default=True, nullable=False)
    avatar_filename = db.Column(db.String(255), nullable=True, default="default.jpg")

    # --- Relationships (cascade keeps child rows in sync) ---
    expenses        = db.relationship(
                        "Expense",
                        back_populates="user",
                        lazy=True,
                        cascade="all, delete-orphan",
                    )
    reminders       = db.relationship(
                        "Reminder",
                        back_populates="user",
                        lazy=True,
                        cascade="all, delete-orphan",
                    )
    ci_calculations = db.relationship(
                        "CICalculation",
                        back_populates="user",
                        lazy=True,
                        cascade="all, delete-orphan",
                    )

    def __repr__(self):
        return f"<User {self.email!r} role={self.role!r}>"


# ---------------------------------------------------------------------------
# ExpenseCategory
# ---------------------------------------------------------------------------

class ExpenseCategory(db.Model):
    __tablename__ = "expense_categories"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_default  = db.Column(db.Boolean, default=True, nullable=False)
    # NULL means it's a global/default category; a user_id makes it user-specific
    user_id     = db.Column(
                    db.Integer,
                    db.ForeignKey("users.id", ondelete="CASCADE"),
                    nullable=True,
                )

    user     = db.relationship("User", backref=db.backref("custom_categories", lazy=True))
    expenses = db.relationship("Expense", back_populates="category", lazy=True)

    def __repr__(self):
        return f"<ExpenseCategory {self.name!r}>"


# ---------------------------------------------------------------------------
# Expense
# ---------------------------------------------------------------------------

class Expense(db.Model):
    __tablename__ = "expenses"

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(
                    db.Integer,
                    db.ForeignKey("users.id", ondelete="CASCADE"),
                    nullable=False,
                )
    category_id  = db.Column(
                    db.Integer,
                    db.ForeignKey("expense_categories.id", ondelete="SET NULL"),
                    nullable=True,
                )
    title        = db.Column(db.String(100), nullable=True)
    amount       = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, default=date.today, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    notes        = db.Column(db.String(255), nullable=True)

    user     = db.relationship("User", back_populates="expenses")
    category = db.relationship("ExpenseCategory", back_populates="expenses")

    def __repr__(self):
        return f"<Expense {self.title!r} ₹{self.amount}>"


# ---------------------------------------------------------------------------
# Reminder
# ---------------------------------------------------------------------------

class Reminder(db.Model):
    __tablename__ = "reminders"

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(
                    db.Integer,
                    db.ForeignKey("users.id", ondelete="CASCADE"),
                    nullable=False,
                )
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.String(500), nullable=True)
    reminder_date = db.Column(db.DateTime, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder {self.title!r} on {self.reminder_date}>"


# ---------------------------------------------------------------------------
# CICalculation  (compound-interest history)
# ---------------------------------------------------------------------------

class CICalculation(db.Model):
    __tablename__ = "ci_calculations"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(
                        db.Integer,
                        db.ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False,
                    )
    principal       = db.Column(db.Numeric(12, 2), nullable=False)
    rate            = db.Column(db.Numeric(5, 2), nullable=False)
    years           = db.Column(db.Integer, nullable=False)
    n_compounds     = db.Column(db.Integer, default=1, nullable=False)
    maturity_amount = db.Column(db.Numeric(12, 2), nullable=False)
    total_interest  = db.Column(db.Numeric(12, 2), nullable=False)
    calculated_at   = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="ci_calculations")

    def __repr__(self):
        return f"<CICalc principal={self.principal} → {self.maturity_amount}>"


# ---------------------------------------------------------------------------
# InvestmentOption  (admin-managed content for the Advisor tab)
# ---------------------------------------------------------------------------

class InvestmentOption(db.Model):
    __tablename__ = "investment_options"

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), nullable=False)
    slug             = db.Column(db.String(50), unique=True, nullable=False)

    icon_class       = db.Column(db.String(50),  nullable=True)   # e.g. "lni lni-diamond"
    tagline          = db.Column(db.String(255), nullable=True)

    section1_label   = db.Column(db.String(100), nullable=True)
    section1_points  = db.Column(db.Text,        nullable=True)   # newline-separated bullets

    section2_label   = db.Column(db.String(100), nullable=True)
    section2_points  = db.Column(db.Text,        nullable=True)

    risk_pill_text   = db.Column(db.String(50),  nullable=True)   # e.g. "Medium risk"
    risk_pill_level  = db.Column(db.String(20),  nullable=True)   # "low" | "medium" | "high"

    external_label   = db.Column(db.String(100), nullable=True)
    external_url     = db.Column(db.String(255), nullable=True)

    sort_order       = db.Column(db.Integer, default=0,    nullable=False)
    is_active        = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<InvestmentOption {self.name!r}>"


# ---------------------------------------------------------------------------
# ContactMessage  (stores submissions from the public contact form)
# ---------------------------------------------------------------------------

class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(150), nullable=False)
    subject      = db.Column(db.String(200), nullable=True)
    topic        = db.Column(db.String(50),  nullable=True, default="general")
    message      = db.Column(db.Text,        nullable=False)
    submitted_at = db.Column(db.DateTime,    default=datetime.utcnow)
    # Optional: mark as read/resolved in admin panel later
    is_read      = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<ContactMessage from={self.email!r} subject={self.subject!r}>"
