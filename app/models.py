from datetime import datetime, date
from flask_login import UserMixin
from .extensions import db



class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("customer", "admin", name="user_role"), nullable=False, default="customer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    avatar_filename = db.Column(db.String(255), nullable=True)

    # Relationships (optional but useful later)
    expenses = db.relationship("Expense", back_populates="user", lazy=True)
    reminders = db.relationship("Reminder", back_populates="user", lazy=True)
    ci_calculations = db.relationship("CICalculation", back_populates="user", lazy=True)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class ExpenseCategory(db.Model):
    __tablename__ = "expense_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    is_default = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # for custom categories


    user = db.relationship("User", backref="custom_categories")
    expenses = db.relationship("Expense", back_populates="category", lazy=True)

    def __repr__(self):
        return f"<ExpenseCategory {self.name}>"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("expense_categories.id"), nullable=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(255))

    user = db.relationship("User", back_populates="expenses")
    category = db.relationship("ExpenseCategory", back_populates="expenses")

    def __repr__(self):
        return f"<Expense {self.title or ''} {self.amount}>"


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    reminder_date = db.Column(db.DateTime, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder {self.title}>"



class CICalculation(db.Model):
    __tablename__ = "ci_calculations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    principal = db.Column(db.Numeric(12, 2), nullable=False)
    rate = db.Column(db.Numeric(5, 2), nullable=False)
    years = db.Column(db.Integer, nullable=False)
    n_compounds = db.Column(db.Integer, default=1)
    maturity_amount = db.Column(db.Numeric(12, 2), nullable=False)
    total_interest = db.Column(db.Numeric(12, 2), nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="ci_calculations")

    def __repr__(self):
        return f"<CICalc {self.principal} -> {self.maturity_amount}>"

class InvestmentOption(db.Model):
    __tablename__ = "investment_options"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

    icon_class = db.Column(db.String(50))          # e.g. "lni lni-diamond"
    tagline = db.Column(db.String(255))           # short one-line description

    section1_label = db.Column(db.String(100))    # e.g. "Why consider it?" or "How it works"
    section1_points = db.Column(db.Text)          # bullet points separated by new lines

    section2_label = db.Column(db.String(100))    # e.g. "Risk & points to note"
    section2_points = db.Column(db.Text)          # bullet points separated by new lines

    risk_pill_text = db.Column(db.String(50))     # text in the pill, e.g. "Medium risk"
    risk_pill_level = db.Column(db.String(20))    # "low", "medium", "high"  (used for CSS class)

    external_label = db.Column(db.String(100))    # button label
    external_url = db.Column(db.String(255))      # link URL

    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<InvestmentOption {self.name}>"

