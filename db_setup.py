#!/usr/bin/env python3
"""
db_setup.py

- DEV ONLY: Drops all tables, creates schema from models, and seeds
  realistic demo data for disha_finance.

Run:
    python db_setup.py

Dependencies:
    pip install python-dotenv Faker mysql-connector-python
"""

import os
import random
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP

from dotenv import load_dotenv
from faker import Faker
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text

# -------------------------
# Load environment
# -------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "disha_finance")

# Engine for CREATE DATABASE (no DB selected)
admin_engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}",
    isolation_level="AUTOCOMMIT",
)

print("Ensuring database exists...")
with admin_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))

print("Database ensured:", DB_NAME)

# Now import the app and models (assumes create_app() and app package exist)
from app import create_app
from app.extensions import db
from app.models import (
    User,
    ExpenseCategory,
    Expense,
    Reminder,
    CICalculation,
    PageContent,
    InvestmentOption,
)

# Reproducible demo seed
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
faker = Faker("en_IN")
Faker.seed(RANDOM_SEED)

# Create app and context
app = create_app()

def to_decimal(val):
    return Decimal(val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

with app.app_context():
    # WARNING: destructive
    print("Dropping all tables (dev only!)...")
    db.drop_all()
    print("Creating tables...")
    db.create_all()

    # -------------------------
    # Users: 3 admins, 10 customers
    # -------------------------
    print("Seeding users...")
    users = []
    admins_data = [
        {"name": "Priya Sharma", "email": "admin1@disha.finance"},
        {"name": "Rohit Verma",  "email": "admin2@disha.finance"},
        {"name": "Anita Kapoor", "email": "admin3@disha.finance"},
    ]
    for i, a in enumerate(admins_data, start=1):
        u = User(
            name=a["name"],
            email=a["email"],
            phone=f"+91{random.choice(['9','8','7','6'])}{faker.random_number(digits=9, fix_len=True)}",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            last_login_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
            avatar_filename=None,
        )
        users.append(u)

    # Realistic customers (Indian names & realistic emails)
    for i in range(1, 11):
        name = faker.name()
        # use a plausible personal email
        local = "".join(name.lower().split())[:10]
        domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "example.com"])
        email = f"{local}{random.randint(1,99)}@{domain}"
        phone = f"+91{random.choice(['9','8','7','6'])}{faker.random_number(digits=9, fix_len=True)}"
        u = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash("user123"),
            role="customer",
            last_login_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            avatar_filename=None,
        )
        users.append(u)

    db.session.add_all(users)
    db.session.commit()

    admins = [u for u in users if u.role == "admin"]
    customers = [u for u in users if u.role == "customer"]

    # -------------------------
    # Expense Categories
    # -------------------------
    print("Seeding expense categories...")
    default_cats = [
        ("Groceries", "Monthly groceries, daily food purchases"),
        ("Rent", "House rent / EMI"),
        ("Transport", "Fuel, metro, taxi, rideshare"),
        ("Utilities", "Electricity, water, gas"),
        ("Internet & Phone", "Mobile and broadband bills"),
        ("Healthcare", "Doctor, medicines, hospital bills"),
        ("Education", "School/college fees, courses"),
        ("Insurance", "Health, vehicle, life insurance"),
        ("Entertainment", "Dining out, movies, streaming"),
        ("Subscriptions", "Netflix, Spotify, SaaS"),
        ("Investments", "SIP, mutual funds, stocks"),
        ("Travel", "Flights, hotels, trips"),
    ]
    categories = []
    for name, desc in default_cats:
        categories.append(ExpenseCategory(name=name, description=desc, is_default=True))
    # Personal custom categories for some users
    for user in random.sample(customers, k=5):
        categories.append(ExpenseCategory(
            name="Freelance Income Tax",
            description="Tax prep for freelance assignments",
            is_default=False,
            user=user
        ))
        categories.append(ExpenseCategory(
            name="Home Maintenance",
            description="Plumbing, electrician, carpentry",
            is_default=False,
            user=user
        ))

    db.session.add_all(categories)
    db.session.commit()

    # Build a category list for random choice (prefer default ones for expenses)
    default_category_objs = [c for c in categories if c.is_default]
    custom_category_objs = [c for c in categories if not c.is_default]

    # -------------------------
    # Expenses: 15-40 per customer with realistic amounts
    # -------------------------
    print("Seeding expenses...")
    expense_titles = [
        "Grocery shopping", "Monthly rent", "Petrol", "Electricity bill", "Mobile recharge",
        "Doctor consultation", "School fees", "Movie night", "Online purchase", "Restaurant dinner",
        "Flight booking", "Mutual fund SIP", "Train ticket", "Pharmacy", "House repair"
    ]

    for user in customers:
        num = random.randint(15, 40)
        for _ in range(num):
            # Choose category biased toward groceries/transport/essentials
            if random.random() < 0.6:
                category = random.choice(default_category_objs)
            else:
                category = random.choice(custom_category_objs + default_category_objs)
            title = random.choice(expense_titles)
            # realistic amount distribution:
            # small everyday: 50-2000, rent/flight etc: 10000-80000
            if title in ["Monthly rent", "Flight booking", "School fees", "House repair"]:
                amount = to_decimal(random.uniform(8000, 80000))
            elif title in ["Mutual fund SIP"]:
                amount = to_decimal(random.uniform(500, 5000))
            elif title in ["Monthly rent"]:
                amount = to_decimal(random.uniform(8000, 40000))
            else:
                amount = to_decimal(random.uniform(50, 8000))

            expense_date = date.today() - timedelta(days=random.randint(0, 180))
            notes = faker.sentence(nb_words=8)
            exp = Expense(
                user=user,
                category=category,
                title=title,
                amount=amount,
                expense_date=expense_date,
                notes=notes,
            )
            db.session.add(exp)
    db.session.commit()

    # -------------------------
    # Reminders: bills, taxes, SIP topups
    # -------------------------
    print("Seeding reminders...")
    reminder_templates = [
        ("Electricity Bill Due", "Pay electricity bill online to avoid late fee"),
        ("SIP Top-up Reminder", "Top-up SIP amount if income changed"),
        ("Tax Filing Reminder", "Check documents and start e-filing"),
        ("Insurance Renewal", "Renew car/health insurance"),
        ("Loan EMI Due", "Loan EMI due this month"),
    ]

    for user in customers:
        # 2-4 reminders in future spread
        for i in range(random.randint(2, 4)):
            tpl = random.choice(reminder_templates)
            remind_days = random.randint(3, 60)
            r = Reminder(
                user=user,
                title=tpl[0],
                description=tpl[1],
                reminder_date=datetime.utcnow() + timedelta(days=remind_days),
            )
            db.session.add(r)
    db.session.commit()

    # -------------------------
    # Compound Interest Calculations
    # -------------------------
    print("Seeding compound interest calculations...")
    # realistic product choices: FD, MF, Stocks expectations
    for user in customers:
        cnt = random.randint(1, 3)
        for _ in range(cnt):
            principal = to_decimal(random.uniform(10000, 500000))
            rate = Decimal(random.choice([5.5, 6.5, 7.0, 8.0, 9.5, 12.0, 15.0]))
            years = random.randint(1, 20)
            n = random.choice([1, 4, 12])  # yearly, quarterly, monthly compounding
            # maturity calculation: A = P*(1 + r/n)^(n*t)
            r_decimal = float(rate) / 100.0
            maturity = Decimal(principal * Decimal((1 + r_decimal / n) ** (n * years))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total_interest = (maturity - principal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            ci = CICalculation(
                user=user,
                principal=principal,
                rate=rate,
                years=years,
                n_compounds=n,
                maturity_amount=maturity,
                total_interest=total_interest,
            )
            db.session.add(ci)
    db.session.commit()

    # -------------------------
    # PageContent (CMS)
    # -------------------------
    print("Seeding page content...")
    admin_user = random.choice(admins)
    page_entries = [
        ("home", "hero_title", "Manage your money. Build your future."),
        ("home", "hero_subtitle", "Disha Finance — expense tracking, investment planning, and reminders in one place."),
        ("home", "feature_1", "Expense tracker with smart categories and monthly insights."),
        ("home", "feature_2", "Automated reminders for bills & investments."),
        ("about", "intro", "Disha Finance is a student-built demo that simulates personal finance management for learning and presentation."),
        ("about", "mission", "We make it simple to track expenses, plan investments, and reach financial goals."),
        ("contact", "email", "support@disha.finance"),
        ("contact", "phone", "+91 90000 00000"),
        ("contact", "address", "123 Demo Street, Bangalore, India"),
    ]
    for slug, section, content in page_entries:
        pc = PageContent(
            page_slug=slug,
            section_name=section,
            content=content,
            updated_by=admin_user.id,
        )
        db.session.add(pc)
    db.session.commit()

    # -------------------------
    # InvestmentOptions
    # -------------------------
    print("Seeding investment options...")
    invs = [
        {
            "name": "Fixed Deposit",
            "slug": "fixed-deposit",
            "tagline": "Low-risk bank deposits with fixed interest.",
            "section1_label": "Why consider FD?",
            "section1_points": "Guaranteed returns\nLow risk\nGood for emergency funds",
            "section2_label": "Things to note",
            "section2_points": "Interest taxed\nPenalty for early withdrawal",
            "risk_pill_text": "Low risk",
            "risk_pill_level": "low",
            "external_label": "Bank rates",
            "external_url": "https://rbi.org.in",
        },
        {
            "name": "Public Provident Fund (PPF)",
            "slug": "ppf",
            "tagline": "Long-term tax-efficient savings.",
            "section1_label": "Why PPF?",
            "section1_points": "Tax benefits\nLong-term savings\nGovernment backed",
            "section2_label": "Things to note",
            "section2_points": "15-year lock-in\nPartial withdrawals have rules",
            "risk_pill_text": "Low to Medium",
            "risk_pill_level": "low",
            "external_label": "Learn PPF",
            "external_url": "https://incometax.gov.in",
        },
        {
            "name": "Mutual Funds (SIP)",
            "slug": "mutual-funds",
            "tagline": "Start SIPs for disciplined investing.",
            "section1_label": "Why SIPs?",
            "section1_points": "Rupee cost averaging\nDiversified exposure\nProfessional management",
            "section2_label": "Things to note",
            "section2_points": "Market risk\nChoose fund based on horizon",
            "risk_pill_text": "Medium risk",
            "risk_pill_level": "medium",
            "external_label": "Explore funds",
            "external_url": "https://www.amfiindia.in",
        },
        {
            "name": "Direct Equity (Stocks)",
            "slug": "stocks",
            "tagline": "High-growth but higher volatility.",
            "section1_label": "Why stocks?",
            "section1_points": "High upside potential\nOwnership in companies",
            "section2_label": "Things to note",
            "section2_points": "High volatility\nRequires research",
            "risk_pill_text": "High risk",
            "risk_pill_level": "high",
            "external_label": "Market info",
            "external_url": "https://www.nseindia.com",
        },
    ]

    for i, item in enumerate(invs):
        opt = InvestmentOption(
            name=item["name"],
            slug=item["slug"],
            tagline=item["tagline"],
            section1_label=item["section1_label"],
            section1_points=item["section1_points"],
            section2_label=item["section2_label"],
            section2_points=item["section2_points"],
            risk_pill_text=item["risk_pill_text"],
            risk_pill_level=item["risk_pill_level"],
            external_label=item["external_label"],
            external_url=item["external_url"],
            sort_order=i,
            is_active=True,
        )
        db.session.add(opt)
    db.session.commit()

    print("✅ Seeding complete. Users:", len(users),
          "Expenses:", db.session.query(Expense).count(),
          "Reminders:", db.session.query(Reminder).count(),
          "CI records:", db.session.query(CICalculation).count())

print("All done. Remember: this script is destructive. Use only in development/demo.")
