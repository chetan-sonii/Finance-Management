#!/usr/bin/env python3
"""
seed_all.py  ─  Disha Finance · Complete Database Seed
═══════════════════════════════════════════════════════
Populates ALL tables with rich, realistic Indian-context mock data:

  ┌─────────────────────────┬───────────────────────────────────────────┐
  │ Table                   │ What gets seeded                          │
  ├─────────────────────────┼───────────────────────────────────────────┤
  │ users                   │ 2 admins + 10 customers (varied profiles) │
  │ expense_categories      │ 14 default + 8 user-specific categories   │
  │ expenses                │ 20-45 expenses per customer (6 months)    │
  │ reminders               │ 4-8 realistic reminders per customer      │
  │ ci_calculations         │ 2-5 calculations per customer             │
  │ investment_options      │ 7 options (FD → Crypto)                  │
  │ contact_messages        │ 18 realistic contact form submissions     │
  └─────────────────────────┴───────────────────────────────────────────┘

Usage:
    python seed_all.py

    ⚠  DESTRUCTIVE — drops all tables and recreates them.
    For development / demo use only.

Requirements:
    pip install faker python-dotenv
    (werkzeug, sqlalchemy, flask already installed with the app)
"""

import os
import sys
import random
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP

# ── Locate project root and bootstrap Flask app ────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

try:
    from faker import Faker
except ImportError:
    sys.exit("❌  'faker' not installed. Run:  pip install faker")

from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text

# ── Ensure the database exists before Flask connects ──────────────────────
DB_USER     = os.getenv("DB_USER",     "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST     = os.getenv("DB_HOST",     "127.0.0.1")
DB_PORT     = os.getenv("DB_PORT",     "3306")
DB_NAME     = os.getenv("DB_NAME",     "disha_finance")

print(f"📡  Connecting to MySQL at {DB_HOST}:{DB_PORT} ...")
admin_engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}",
    isolation_level="AUTOCOMMIT",
)
with admin_engine.connect() as conn:
    conn.execute(text(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    ))
print(f"✅  Database `{DB_NAME}` ready.\n")

# ── Import Flask app + models ─────────────────────────────────────────────
from app import create_app
from app.extensions import db
from app.models import (
    User,
    ExpenseCategory,
    Expense,
    Reminder,
    CICalculation,
    InvestmentOption,
    ContactMessage,
)

# ── Reproducible randomness ────────────────────────────────────────────────
SEED = 2025
random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

app = create_app()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def dec(value: float) -> Decimal:
    """Round a float to a 2-decimal Decimal (for Numeric columns)."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def days_ago(n: int) -> datetime:
    return datetime.utcnow() - timedelta(days=n)


def days_from_now(n: int) -> datetime:
    return datetime.utcnow() + timedelta(days=n)


def date_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


def random_indian_phone() -> str:
    prefix = random.choice(["6", "7", "8", "9"])
    rest   = "".join([str(random.randint(0, 9)) for _ in range(9)])
    return f"+91{prefix}{rest}"


# ─────────────────────────────────────────────────────────────────────────────
# Seed data definitions
# ─────────────────────────────────────────────────────────────────────────────

# ── Users ─────────────────────────────────────────────────────────────────

ADMIN_USERS = [
    {
        "name":  "Priya Sharma",
        "email": "priya.admin@disha.finance",
        "phone": "+919876543210",
        "last_login_at": days_ago(1),
    },
    {
        "name":  "Rohit Verma",
        "email": "rohit.admin@disha.finance",
        "phone": "+918765432109",
        "last_login_at": days_ago(3),
    },
]

CUSTOMER_USERS = [
    {
        "name":          "Aarav Mehta",
        "email":         "aarav.mehta91@gmail.com",
        "phone":         "+917654321098",
        "last_login_at": days_ago(0),
        "profile":       "salaried_mid",     # helps pick realistic expenses
    },
    {
        "name":          "Sneha Patel",
        "email":         "sneha.patel88@yahoo.com",
        "phone":         "+916543210987",
        "last_login_at": days_ago(2),
        "profile":       "salaried_high",
    },
    {
        "name":          "Vikram Singh",
        "email":         "vikramsingh23@outlook.com",
        "phone":         "+919988776655",
        "last_login_at": days_ago(5),
        "profile":       "freelancer",
    },
    {
        "name":          "Kavya Nair",
        "email":         "kavya.nair77@gmail.com",
        "phone":         "+917788990011",
        "last_login_at": days_ago(1),
        "profile":       "student",
    },
    {
        "name":          "Arjun Reddy",
        "email":         "arjunreddy09@gmail.com",
        "phone":         "+918899001122",
        "last_login_at": days_ago(10),
        "profile":       "business_owner",
    },
    {
        "name":          "Meera Iyer",
        "email":         "meera.iyer55@gmail.com",
        "phone":         "+916677889900",
        "last_login_at": days_ago(0),
        "profile":       "salaried_mid",
    },
    {
        "name":          "Rohan Gupta",
        "email":         "rohan.gupta44@outlook.com",
        "phone":         "+919900112233",
        "last_login_at": days_ago(7),
        "profile":       "salaried_high",
    },
    {
        "name":          "Pooja Joshi",
        "email":         "pooja.joshi32@gmail.com",
        "phone":         "+917711223344",
        "last_login_at": days_ago(3),
        "profile":       "freelancer",
    },
    {
        "name":          "Karan Malhotra",
        "email":         "karan.malhotra@example.com",
        "phone":         "+918822334455",
        "last_login_at": days_ago(15),
        "profile":       "business_owner",
    },
    {
        "name":          "Divya Krishnamurthy",
        "email":         "divya.krishna01@gmail.com",
        "phone":         "+919933445566",
        "last_login_at": days_ago(0),
        "profile":       "student",
    },
]

# ── Expense categories ────────────────────────────────────────────────────

DEFAULT_CATEGORIES = [
    ("Groceries",           "Monthly groceries, daily food purchases"),
    ("Rent",                "House rent / PG / hostel"),
    ("Transport",           "Fuel, metro, Ola/Uber, auto"),
    ("Utilities",           "Electricity, water, gas cylinder"),
    ("Internet & Phone",    "Mobile recharge, broadband bills"),
    ("Healthcare",          "Doctor fees, medicines, lab tests"),
    ("Education",           "Tuition, courses, books, stationery"),
    ("Insurance",           "Health, life, vehicle insurance premiums"),
    ("Entertainment",       "Movies, dining out, events"),
    ("Subscriptions",       "Netflix, Spotify, Zomato Gold, apps"),
    ("Investments",         "SIP, PPF, NPS, gold purchases"),
    ("Travel",              "Flights, hotels, cabs, trip expenses"),
    ("Clothing & Personal", "Clothes, salon, skincare, accessories"),
    ("Miscellaneous",       "One-off or uncategorised expenses"),
]

# User-specific custom categories (assigned randomly to customers)
CUSTOM_CATEGORIES = [
    ("Freelance Tax",       "GST and income tax for freelance income"),
    ("Home Maintenance",    "Plumbing, electrician, painting, repairs"),
    ("Pet Expenses",        "Vet, food, grooming for pets"),
    ("Gym & Fitness",       "Gym membership, protein, supplements"),
    ("Business Overheads",  "Office rent, supplies, staff wages"),
    ("Stock Trading Fees",  "Brokerage, STT, exchange fees"),
    ("Charity & Donations", "NGO donations, temple, crowdfunding"),
    ("Vehicle EMI",         "Two-wheeler or car loan EMI"),
]

# ── Expense templates per profile ─────────────────────────────────────────
# (category_name, title, min_amount, max_amount, frequency_weight)

EXPENSE_TEMPLATES = {
    "salaried_mid": [
        ("Rent",                "Monthly rent – 2BHK",              12000, 18000, 3),
        ("Groceries",           "D-Mart grocery run",                2000,  5000, 4),
        ("Groceries",           "BigBasket order",                   800,   2500, 3),
        ("Transport",           "Monthly metro pass",                800,   1200, 2),
        ("Transport",           "Ola/Uber rides",                    300,   1500, 4),
        ("Transport",           "Petrol",                            1500,  4000, 3),
        ("Utilities",           "Electricity bill",                  800,   2200, 2),
        ("Utilities",           "Gas cylinder refill",               900,   950,  2),
        ("Internet & Phone",    "JioFiber broadband",                599,   999,  2),
        ("Internet & Phone",    "Mobile recharge – Airtel",          239,   719,  2),
        ("Healthcare",          "Doctor consultation",               500,   1500, 1),
        ("Healthcare",          "Pharmacy – medicines",              200,   1200, 2),
        ("Entertainment",       "Restaurant dinner",                 600,   2500, 3),
        ("Entertainment",       "Movie tickets – PVR",               400,   900,  2),
        ("Subscriptions",       "Netflix subscription",              499,   649,  1),
        ("Subscriptions",       "Amazon Prime",                      179,   179,  1),
        ("Investments",         "SIP – Nifty 50 index fund",         3000,  7000, 2),
        ("Clothing & Personal", "Myntra clothing order",             500,   3000, 2),
        ("Clothing & Personal", "Salon / haircut",                   200,   800,  2),
        ("Miscellaneous",       "Amazon household purchase",         300,   2500, 3),
    ],
    "salaried_high": [
        ("Rent",                "Monthly rent – 3BHK premium",      25000, 55000, 2),
        ("Groceries",           "Nature's Basket / premium grocery", 5000,  12000, 3),
        ("Transport",           "Car EMI",                          15000, 35000, 2),
        ("Transport",           "Petrol / fuel",                     4000,  8000, 3),
        ("Transport",           "Uber / ola",                        800,   4000, 3),
        ("Utilities",           "Electricity bill",                  2000,  5000, 2),
        ("Utilities",           "Piped gas",                         600,   1200, 2),
        ("Internet & Phone",    "Broadband – premium plan",          999,   1999, 2),
        ("Internet & Phone",    "Mobile – corporate plan",           599,   999,  2),
        ("Healthcare",          "Health check-up",                   2000,  8000, 1),
        ("Healthcare",          "Gym membership",                    2500,  5000, 1),
        ("Entertainment",       "Fine dining",                       2000,  8000, 3),
        ("Entertainment",       "Weekend trip",                      5000,  20000, 2),
        ("Subscriptions",       "Netflix + Hotstar + Prime bundle",  700,   1200, 1),
        ("Subscriptions",       "LinkedIn Premium",                  1200,  1500, 1),
        ("Investments",         "SIP – flexi-cap fund",             15000, 50000, 2),
        ("Investments",         "Stocks – direct equity",            5000,  50000, 2),
        ("Travel",              "Flight tickets – domestic",        4000,  18000, 2),
        ("Travel",              "Hotel booking",                     3000,  15000, 2),
        ("Clothing & Personal", "Branded clothing / accessories",    2000,  12000, 2),
        ("Insurance",           "Term life insurance premium",       7000,  20000, 1),
        ("Insurance",           "Health insurance – family floater", 15000, 35000, 1),
    ],
    "freelancer": [
        ("Rent",                "Co-working space membership",       5000,  12000, 2),
        ("Rent",                "Home office rent",                  8000,  20000, 2),
        ("Groceries",           "Grocery shopping",                  1500,  4000, 4),
        ("Transport",           "Client meeting – cab",              300,   1500, 4),
        ("Transport",           "Petrol",                            1500,  3500, 3),
        ("Internet & Phone",    "High-speed fibre – freelancer plan",999,   1499, 2),
        ("Internet & Phone",    "Mobile data plan",                  399,   799,  2),
        ("Education",           "Udemy / Coursera course",           500,   5000, 2),
        ("Education",           "Book – skill / tech",               300,   2000, 2),
        ("Subscriptions",       "Adobe Creative Cloud",              1675,  5676, 1),
        ("Subscriptions",       "GitHub Copilot",                    830,   830,  1),
        ("Subscriptions",       "Notion / Figma / Slack",            400,   1500, 1),
        ("Healthcare",          "Pharmacy",                          200,   1000, 2),
        ("Entertainment",       "Cafe working – coffee + snacks",    200,   700,  4),
        ("Entertainment",       "OTT subscription",                  200,   700,  1),
        ("Investments",         "SIP – ELSS fund",                   2000,  10000, 2),
        ("Miscellaneous",       "Software / domain / hosting",       500,   8000, 2),
        ("Miscellaneous",       "Client gift / business expense",    500,   3000, 2),
        ("Clothing & Personal", "Personal grooming",                 300,   1000, 2),
    ],
    "student": [
        ("Education",           "College tuition fees",             20000, 90000, 1),
        ("Education",           "Books and stationery",             300,   2000, 3),
        ("Education",           "Online course – Coursera/Udemy",   500,   4000, 2),
        ("Rent",                "PG / hostel rent",                 5000,  14000, 2),
        ("Groceries",           "Mess bill / tiffin",               1500,  4000, 3),
        ("Groceries",           "Zomato / Swiggy order",            150,   700,  4),
        ("Transport",           "Metro / local bus pass",           500,   1000, 2),
        ("Transport",           "Auto / ola shared",                100,   500,  4),
        ("Internet & Phone",    "Mobile recharge",                  199,   399,  2),
        ("Entertainment",       "Movie / event outing",             200,   800,  2),
        ("Entertainment",       "Gaming / steam purchases",         300,   2000, 2),
        ("Subscriptions",       "Spotify / YouTube Premium",        59,    179,  1),
        ("Healthcare",          "Medicines / OTC",                  100,   500,  2),
        ("Clothing & Personal", "Clothing – Meesho / Flipkart",     300,   2000, 2),
        ("Miscellaneous",       "Stationery / printing",            50,    500,  3),
        ("Miscellaneous",       "Misc college expense",             100,   1000, 3),
    ],
    "business_owner": [
        ("Rent",                "Office / shop rent",               30000, 150000, 2),
        ("Rent",                "Warehouse rent",                   20000, 80000,  1),
        ("Transport",           "Company vehicle fuel",             5000,  15000,  3),
        ("Transport",           "Staff travel reimbursement",       2000,  10000,  2),
        ("Utilities",           "Commercial electricity",           5000,  30000,  2),
        ("Internet & Phone",    "Business broadband + phone",       2000,  5000,   2),
        ("Internet & Phone",    "Business mobile plans (staff)",    3000,  10000,  2),
        ("Insurance",           "Business insurance",               10000, 50000,  1),
        ("Insurance",           "Vehicle fleet insurance",          15000, 60000,  1),
        ("Entertainment",       "Client entertainment",             2000,  15000,  3),
        ("Entertainment",       "Team lunch / dinner",              3000,  12000,  2),
        ("Investments",         "SIP – balanced advantage fund",   10000, 100000,  2),
        ("Investments",         "PPF annual contribution",          10000, 150000,  1),
        ("Travel",              "Business travel – flights",         5000,  30000,  2),
        ("Travel",              "Hotel – business trip",             4000,  20000,  2),
        ("Miscellaneous",       "Office supplies & stationery",     1000,  8000,   2),
        ("Miscellaneous",       "Professional fees – CA / lawyer",  5000,  30000,  2),
        ("Education",           "Staff training programme",         5000,  25000,  1),
    ],
}

# ── Reminder templates ────────────────────────────────────────────────────

REMINDER_TEMPLATES = {
    "salaried_mid": [
        ("Credit Card Bill – HDFC",      "Pay HDFC credit card before due date to avoid interest.",        3, 28),
        ("SIP Auto-debit – Nifty 50",    "Monthly SIP will be debited. Ensure funds in account.",          1, 5),
        ("Electricity Bill",             "BESCOM / MSEDCL electricity bill due.",                         10, 20),
        ("JioFiber Renewal",             "Broadband plan expires. Recharge to avoid disconnection.",        5, 35),
        ("Rent Payment",                 "Monthly house rent – transfer via NEFT / UPI.",                  1, 5),
        ("Aadhaar / PAN Linking",        "Complete Aadhaar-PAN linking to avoid higher TDS.",             30, 90),
        ("Form 16 / ITR Filing",         "Collect Form 16 from employer and file ITR by 31st July.",      60, 150),
        ("Vehicle Insurance Renewal",    "Car / bike insurance expires. Renew before lapse.",             10, 60),
    ],
    "salaried_high": [
        ("EMI – Home Loan",              "Housing loan EMI auto-debit on 5th. Ensure balance.",            2, 6),
        ("Term Insurance Premium",       "Annual term life insurance premium due.",                        10, 60),
        ("Health Insurance Renewal",     "Family floater health policy renewal date.",                     15, 90),
        ("Portfolio Review",             "Quarterly review of mutual fund and stock portfolio.",           30, 90),
        ("Tax-saving Investment (ELSS)", "Last date to invest in ELSS for Section 80C benefit.",          30, 120),
        ("Advance Tax Payment",          "Quarterly advance tax payment due. Check CA for amount.",        15, 90),
        ("Passport / Visa Renewal",      "Passport expiring. Start renewal process early.",               90, 300),
        ("Club Membership Renewal",      "Annual club or gym membership fee due.",                        10, 60),
    ],
    "freelancer": [
        ("GST Return Filing",            "Monthly GSTR-1 / quarterly GSTR-3B filing deadline.",           5, 45),
        ("Advance Tax – Q1/Q2/Q3/Q4",   "Quarterly advance tax instalment due. Pay to avoid interest.",  5, 90),
        ("Client Invoice Follow-up",     "Send reminder to client for pending invoice payment.",          1, 15),
        ("Domain / Hosting Renewal",     "Website hosting or domain name renewal due.",                   7, 60),
        ("Professional Tax",             "State professional tax payment deadline.",                      10, 90),
        ("Portfolio Update",             "Update Behance / GitHub / LinkedIn portfolio with new work.",   7, 30),
        ("TDS Certificate Collection",   "Collect Form 16A / TDS certificate from clients.",             30, 90),
        ("Subscription Audit",           "Review all SaaS subscriptions. Cancel unused ones.",           15, 45),
    ],
    "student": [
        ("Tuition Fee Payment",          "Semester / monthly tuition fee payment deadline.",              5, 30),
        ("Library Book Return",          "Return library books before due date to avoid fine.",           1, 14),
        ("Scholarship Application",      "Apply / renew scholarship before application closes.",         30, 90),
        ("Exam Registration",            "Register for upcoming university / competitive exams.",         15, 60),
        ("Internship / Placement Form",  "Submit internship application or placement form.",              7, 30),
        ("Mobile / DTH Recharge",        "Prepaid recharge to avoid SIM deactivation.",                   3, 28),
        ("Hostel Fee Deadline",          "Pay hostel / PG rent before the 5th of the month.",            1, 5),
        ("Study Group Meeting",          "Weekly group study session – prepare notes beforehand.",        1, 7),
    ],
    "business_owner": [
        ("GST Return (GSTR-1)",          "File monthly GSTR-1 by 11th of next month.",                   1, 15),
        ("GST Return (GSTR-3B)",         "Pay GST liability and file GSTR-3B by 20th.",                  5, 20),
        ("Employee Salary Credit",       "Process payroll by end of month. Verify attendance.",          2, 5),
        ("TDS Deposit",                  "Deposit TDS deducted from vendors/employees by 7th.",          2, 7),
        ("Vendor Payment – Outstanding", "Clear outstanding vendor bills to maintain credit terms.",     5, 30),
        ("Business Insurance Renewal",   "General liability / fire insurance renewal due.",              15, 90),
        ("CA Appointment – Audit",       "Schedule CA meeting for statutory / tax audit.",               30, 90),
        ("ROC Annual Filing",            "File Annual Return (ROC) for Pvt Ltd / LLP.",                 30, 120),
    ],
}

# ── CI Calculation presets ────────────────────────────────────────────────

CI_PRESETS = {
    "salaried_mid": [
        {"label": "FD – Bank",              "min_p": 50000,   "max_p": 300000,  "rates": [6.5, 7.0, 7.25], "years_range": (1, 5),  "n_opts": [1, 4]},
        {"label": "PPF",                    "min_p": 10000,   "max_p": 150000,  "rates": [7.1],             "years_range": (5, 15), "n_opts": [1]},
        {"label": "Recurring Deposit",      "min_p": 5000,    "max_p": 50000,   "rates": [6.5, 7.0],        "years_range": (1, 3),  "n_opts": [12]},
    ],
    "salaried_high": [
        {"label": "Mutual Fund – Flexi",    "min_p": 100000,  "max_p": 1000000, "rates": [12.0, 15.0],      "years_range": (5, 20), "n_opts": [1]},
        {"label": "NPS Pension",            "min_p": 50000,   "max_p": 500000,  "rates": [9.0, 10.0, 11.0], "years_range": (10, 25),"n_opts": [1]},
        {"label": "FD – Corporate",         "min_p": 200000,  "max_p": 1000000, "rates": [7.5, 8.0],        "years_range": (1, 5),  "n_opts": [4]},
    ],
    "freelancer": [
        {"label": "ELSS Mutual Fund",       "min_p": 25000,   "max_p": 200000,  "rates": [12.0, 14.0],      "years_range": (3, 10), "n_opts": [1]},
        {"label": "Liquid Fund",            "min_p": 10000,   "max_p": 100000,  "rates": [6.0, 6.5],        "years_range": (1, 2),  "n_opts": [4]},
        {"label": "FD – Small Finance",     "min_p": 30000,   "max_p": 150000,  "rates": [8.0, 8.5, 9.0],  "years_range": (1, 3),  "n_opts": [4]},
    ],
    "student": [
        {"label": "Post Office RD",         "min_p": 1000,    "max_p": 10000,   "rates": [6.7],             "years_range": (1, 5),  "n_opts": [12]},
        {"label": "Savings FD",             "min_p": 5000,    "max_p": 30000,   "rates": [5.5, 6.0],        "years_range": (1, 2),  "n_opts": [4]},
    ],
    "business_owner": [
        {"label": "Commercial FD",          "min_p": 500000,  "max_p": 5000000, "rates": [7.0, 7.5, 8.0],  "years_range": (1, 3),  "n_opts": [4]},
        {"label": "MF – Balanced Advantage","min_p": 200000,  "max_p": 2000000, "rates": [10.0, 12.0],      "years_range": (3, 10), "n_opts": [1]},
        {"label": "PPF – Business Owner",   "min_p": 50000,   "max_p": 150000,  "rates": [7.1],             "years_range": (10, 15),"n_opts": [1]},
        {"label": "NPS – Tier II",          "min_p": 100000,  "max_p": 500000,  "rates": [9.5, 10.0],       "years_range": (5, 15), "n_opts": [1]},
    ],
}

# ── Investment options ────────────────────────────────────────────────────

INVESTMENT_OPTIONS = [
    {
        "name":            "Fixed Deposit (FD)",
        "slug":            "fixed-deposit",
        "icon_class":      "lni lni-protection",
        "tagline":         "Safe, guaranteed returns from your bank.",
        "section1_label":  "Why consider FD?",
        "section1_points": (
            "Guaranteed returns — no market risk\n"
            "Insured up to ₹5 lakh per bank by DICGC\n"
            "Flexible tenures from 7 days to 10 years\n"
            "Premature withdrawal allowed (with penalty)"
        ),
        "section2_label":  "Points to note",
        "section2_points": (
            "Interest income is fully taxable as per your slab\n"
            "TDS deducted if interest > ₹40,000 p.a.\n"
            "Returns may not beat inflation in the long run\n"
            "Lock-in means limited liquidity"
        ),
        "risk_pill_text":  "Low risk",
        "risk_pill_level": "low",
        "external_label":  "Compare FD rates",
        "external_url":    "https://www.bankbazaar.com/fixed-deposit.html",
        "sort_order":      1,
    },
    {
        "name":            "Public Provident Fund (PPF)",
        "slug":            "ppf",
        "icon_class":      "lni lni-government",
        "tagline":         "15-year government-backed tax-free savings.",
        "section1_label":  "Why PPF?",
        "section1_points": (
            "EEE tax benefit — contribution, interest, and maturity all tax-free\n"
            "Government-backed — zero default risk\n"
            "Current interest rate: 7.1% p.a. (compounded annually)\n"
            "Can extend in 5-year blocks after 15 years"
        ),
        "section2_label":  "Things to watch",
        "section2_points": (
            "Strict 15-year lock-in period\n"
            "Partial withdrawal allowed only from year 7\n"
            "Maximum deposit: ₹1.5 lakh per financial year\n"
            "Cannot be attached by court decree"
        ),
        "risk_pill_text":  "Very low risk",
        "risk_pill_level": "low",
        "external_label":  "PPF calculator (Govt)",
        "external_url":    "https://www.indiapost.gov.in",
        "sort_order":      2,
    },
    {
        "name":            "Mutual Funds – SIP",
        "slug":            "mutual-funds-sip",
        "icon_class":      "lni lni-bar-chart",
        "tagline":         "Invest small amounts monthly. Let compounding do the heavy lifting.",
        "section1_label":  "Why SIP?",
        "section1_points": (
            "Rupee cost averaging — buy more units when market dips\n"
            "Start with as little as ₹500/month\n"
            "Access to equity, debt, hybrid, and international funds\n"
            "ELSS funds give Section 80C tax deduction up to ₹1.5 lakh"
        ),
        "section2_label":  "Risk & considerations",
        "section2_points": (
            "Returns are market-linked — no guarantee\n"
            "Past performance does not guarantee future results\n"
            "Exit load may apply for short-term redemption\n"
            "Choose fund category based on time horizon and risk appetite"
        ),
        "risk_pill_text":  "Medium risk",
        "risk_pill_level": "medium",
        "external_label":  "Explore funds – AMFI",
        "external_url":    "https://www.amfiindia.com",
        "sort_order":      3,
    },
    {
        "name":            "National Pension System (NPS)",
        "slug":            "nps",
        "icon_class":      "lni lni-users",
        "tagline":         "Build your retirement corpus with tax benefits.",
        "section1_label":  "Why NPS?",
        "section1_points": (
            "Additional ₹50,000 deduction under Section 80CCD(1B)\n"
            "Low cost — fund management fees among lowest globally\n"
            "Equity, corporate bonds, and government bonds allocation\n"
            "Regulated by PFRDA — safe and transparent"
        ),
        "section2_label":  "Things to note",
        "section2_points": (
            "Locked until age 60 (partial withdrawal allowed in emergencies)\n"
            "40% of corpus must be annuitised at retirement\n"
            "Annuity income is taxable in retirement\n"
            "Returns depend on asset allocation chosen"
        ),
        "risk_pill_text":  "Low to Medium",
        "risk_pill_level": "low",
        "external_label":  "Open NPS account",
        "external_url":    "https://www.npscra.nsdl.co.in",
        "sort_order":      4,
    },
    {
        "name":            "Direct Equity (Stocks)",
        "slug":            "direct-equity",
        "icon_class":      "lni lni-graph",
        "tagline":         "Own a piece of India's best companies.",
        "section1_label":  "Why stocks?",
        "section1_points": (
            "Highest long-term wealth creation potential (Nifty ~13% CAGR)\n"
            "Dividend income in addition to capital appreciation\n"
            "Full liquidity — buy/sell anytime during market hours\n"
            "Voting rights as shareholder"
        ),
        "section2_label":  "Risk & points",
        "section2_points": (
            "High short-term volatility — values can fall sharply\n"
            "Requires research, analysis, and ongoing monitoring\n"
            "Risk of permanent capital loss if company fails\n"
            "LTCG > ₹1 lakh taxed at 10%; STCG at 15%"
        ),
        "risk_pill_text":  "High risk",
        "risk_pill_level": "high",
        "external_label":  "NSE market info",
        "external_url":    "https://www.nseindia.com",
        "sort_order":      5,
    },
    {
        "name":            "Sovereign Gold Bond (SGB)",
        "slug":            "sovereign-gold-bond",
        "icon_class":      "lni lni-diamond",
        "tagline":         "Invest in gold digitally — no storage hassle.",
        "section1_label":  "Why SGB?",
        "section1_points": (
            "2.5% annual interest paid semi-annually\n"
            "Capital gains tax exempt if held to maturity (8 years)\n"
            "No storage, purity, or making-charge worries\n"
            "Issued and guaranteed by Government of India via RBI"
        ),
        "section2_label":  "Things to note",
        "section2_points": (
            "8-year maturity (exit allowed from 5th year on coupon dates)\n"
            "Price tracks international gold prices — may fall\n"
            "Interest income taxable at slab rate\n"
            "New series issued sporadically — watch for RBI announcements"
        ),
        "risk_pill_text":  "Low to Medium",
        "risk_pill_level": "low",
        "external_label":  "RBI SGB info",
        "external_url":    "https://www.rbi.org.in",
        "sort_order":      6,
    },
    {
        "name":            "Real Estate Investment Trust (REIT)",
        "slug":            "reit",
        "icon_class":      "lni lni-home",
        "tagline":         "Own commercial real estate with ₹300 — no property hassle.",
        "section1_label":  "Why REITs?",
        "section1_points": (
            "Regular dividend income from rental yield (typically 5-8%)\n"
            "Exposure to Grade A commercial properties\n"
            "Listed on stock exchange — liquid investment\n"
            "Lower correlation with equity markets"
        ),
        "section2_label":  "Risk & points",
        "section2_points": (
            "NAV can fluctuate with commercial real estate markets\n"
            "Distribution is not guaranteed\n"
            "Dividend income taxable in hands of investor\n"
            "Limited number of listed REITs in India currently"
        ),
        "risk_pill_text":  "Medium risk",
        "risk_pill_level": "medium",
        "external_label":  "SEBI REIT info",
        "external_url":    "https://www.sebi.gov.in",
        "sort_order":      7,
    },
]

# ── Contact messages ──────────────────────────────────────────────────────

CONTACT_MESSAGES = [
    {
        "name":    "Rahul Agarwal",
        "email":   "rahul.agarwal@gmail.com",
        "subject": "Cannot log in to my account",
        "topic":   "account",
        "message": "Hi, I created an account last week but I can't seem to log in. I tried resetting my password but I'm not receiving the reset email. Please help me recover access to my account.",
        "is_read": True,
        "days_ago": 12,
    },
    {
        "name":    "Sunita Bhatt",
        "email":   "sunita.bhatt89@yahoo.com",
        "subject": "Expense tracking feature suggestion",
        "topic":   "feedback",
        "message": "Hello! I love the expense calculator feature. One suggestion — could you add a feature to set a monthly budget limit per category and alert me when I'm close to exceeding it? That would be super helpful for people like me who overspend on food!",
        "is_read": True,
        "days_ago": 8,
    },
    {
        "name":    "Gaurav Tiwari",
        "email":   "gaurav.tiwari.work@gmail.com",
        "subject": "Incorrect compound interest calculation",
        "topic":   "expenses",
        "message": "I noticed that the compound interest calculator gives a slightly different result when I choose monthly compounding vs quarterly. I cross-checked with a bank's FD calculator and the numbers don't match for monthly. Can you please check the formula?",
        "is_read": False,
        "days_ago": 5,
    },
    {
        "name":    "Anjali Desai",
        "email":   "anjali.desai.finance@outlook.com",
        "subject": "Request: PDF export for expenses",
        "topic":   "feedback",
        "message": "The CSV export is useful, but many people (especially non-technical users) find it easier to work with PDFs. Could you add a PDF export option for monthly expense summaries with a nice visual layout? It would also help share reports with family members.",
        "is_read": False,
        "days_ago": 4,
    },
    {
        "name":    "Nikhil Kumar",
        "email":   "nikhil.kumar22@gmail.com",
        "subject": "Dashboard not loading on mobile",
        "topic":   "account",
        "message": "I'm using Chrome on my Android phone (Samsung Galaxy A52) and when I open the dashboard, the sidebar overlaps the main content area. The calendar tab is completely unusable on mobile. Works fine on laptop. Please fix for mobile users.",
        "is_read": True,
        "days_ago": 7,
    },
    {
        "name":    "Deepa Nambiar",
        "email":   "deepa.nambiar.k@gmail.com",
        "subject": "Adding SIP and EMI tracking",
        "topic":   "investments",
        "message": "Hi Disha Finance team! I love the investment advisor section. One thing I'd really appreciate is a separate SIP tracker where I can add all my SIPs, see their current value, XIRR, and next instalment date. Same for EMIs — a tracker showing outstanding principal, total interest paid, and months remaining.",
        "is_read": False,
        "days_ago": 3,
    },
    {
        "name":    "Ravi Chandrasekaran",
        "email":   "ravi.cs.engineer@gmail.com",
        "subject": "API access for developers",
        "topic":   "general",
        "message": "I'm a developer and I love the concept of Disha Finance. Do you provide an API that I can use to integrate expense tracking into my own budgeting app? If not, is there any plan to provide one in the future? I'd be happy to be an early beta tester.",
        "is_read": True,
        "days_ago": 10,
    },
    {
        "name":    "Preethi Subramaniam",
        "email":   "preethi.s1992@yahoo.com",
        "subject": "How to delete individual expenses?",
        "topic":   "expenses",
        "message": "I accidentally added a duplicate entry in the expense calculator. I saved it and now it shows in my history. How do I delete individual expense entries? I could only find the option to delete my entire account which is too drastic. Please guide.",
        "is_read": True,
        "days_ago": 6,
    },
    {
        "name":    "Manish Chaudhary",
        "email":   "manish.chaudhary.jaipur@gmail.com",
        "subject": "Reminder notifications via WhatsApp",
        "topic":   "feedback",
        "message": "The reminder feature is great but I forget to check the website. Can you add WhatsApp notifications for reminders? I know many services offer this now. Alternatively, even email reminders would be very helpful. Currently the reminders only show on the website.",
        "is_read": False,
        "days_ago": 2,
    },
    {
        "name":    "Lakshmi Prasad",
        "email":   "lakshmiprasad.hyd@gmail.com",
        "subject": "Disha Finance for families – joint accounts?",
        "topic":   "general",
        "message": "My husband and I both want to track our family expenses together. Currently we each have separate accounts. Is there any plan for family / shared accounts where two people can view and add expenses to a common budget? This would be very useful for household financial planning.",
        "is_read": False,
        "days_ago": 1,
    },
    {
        "name":    "Suresh Babu",
        "email":   "suresh.babu.accounts@gmail.com",
        "subject": "Partner with us – financial advisory",
        "topic":   "general",
        "message": "Hello, I am a SEBI-registered investment advisor with 12 years of experience. I came across Disha Finance and I think there could be a good partnership opportunity — I can provide personalised financial planning content for your users. Please reach out to discuss further.",
        "is_read": True,
        "days_ago": 15,
    },
    {
        "name":    "Tanvi Mehrotra",
        "email":   "tanvi.mehrotra.delhi@outlook.com",
        "subject": "Dark mode support?",
        "topic":   "feedback",
        "message": "The current dashboard design is nice but a dark mode option would be amazing! Many finance apps now support it and it is much easier on the eyes at night. Can you please add a toggle for dark/light mode? I usually check my finances before sleeping.",
        "is_read": False,
        "days_ago": 1,
    },
    {
        "name":    "Abhishek Rana",
        "email":   "abhishek.rana.fin@gmail.com",
        "subject": "Data privacy – where is my data stored?",
        "topic":   "general",
        "message": "Before I add more sensitive financial data to Disha Finance, I'd like to know: where is the data stored? Is it in India (data localisation)? What encryption do you use? Is the data shared with third parties? A privacy policy page would help build trust.",
        "is_read": True,
        "days_ago": 9,
    },
    {
        "name":    "Megha Sharma",
        "email":   "megha.sharma.mba@gmail.com",
        "subject": "Internship / career opportunity",
        "topic":   "general",
        "message": "Hi! I am an MBA student specialising in finance from IIM Rohtak. I'd love to intern with Disha Finance in a product or business development role. I have experience in financial modelling and UX research. Could you share details about any internship openings?",
        "is_read": False,
        "days_ago": 4,
    },
    {
        "name":    "Kartik Sharma",
        "email":   "kartik.sharma.ca@gmail.com",
        "subject": "Tax filing integration idea",
        "topic":   "investments",
        "message": "As a CA, I often help clients calculate their capital gains and file ITR. If Disha Finance could export a report in the format required for ITR-2 or ITR-3 (capital gains schedule, income from other sources), it would be a huge value-add for investors. Just a thought!",
        "is_read": True,
        "days_ago": 11,
    },
    {
        "name":    "Pallavi Krishnan",
        "email":   "pallavi.krishnan.blr@yahoo.com",
        "subject": "Wrong amount displayed in overview",
        "topic":   "expenses",
        "message": "The Overview section shows my total expenses for this month as ₹0 even though I have saved multiple expenses this month. The expense calculator page shows the correct data. Seems like a bug in the overview API or the date filtering. Please check.",
        "is_read": False,
        "days_ago": 2,
    },
    {
        "name":    "Vivek Anand",
        "email":   "vivek.anand.startup@gmail.com",
        "subject": "Startup collaboration proposal",
        "topic":   "general",
        "message": "Hi Disha Finance team! I run a fintech startup focused on credit score improvement. I think there's a great opportunity for us to collaborate — your users are budget-conscious and improving their credit score would be the natural next step. Would love to connect for a quick call.",
        "is_read": False,
        "days_ago": 0,
    },
    {
        "name":    "Neha Jain",
        "email":   "neha.jain.teacher@gmail.com",
        "subject": "Loved the Investment Advisor section!",
        "topic":   "investments",
        "message": "I am a school teacher and not very savvy with investments. I found the Investment Advisor section really helpful — it explains each option in simple language. I finally understood the difference between PPF and NPS! Can you also add a section about gold ETFs and sovereign gold bonds? Thank you!",
        "is_read": True,
        "days_ago": 5,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Seed execution
# ─────────────────────────────────────────────────────────────────────────────

def seed_all():
    with app.app_context():

        # ── Wipe and recreate schema ──────────────────────────────────────
        print("⚠   Dropping all tables …")
        db.drop_all()
        print("🔨  Creating tables …")
        db.create_all()
        print()

        # ──────────────────────────────────────────────────────────────────
        # 1. USERS
        # ──────────────────────────────────────────────────────────────────
        print("👤  Seeding users …")

        user_objects = []

        for a in ADMIN_USERS:
            u = User(
                name          = a["name"],
                email         = a["email"],
                phone         = a["phone"],
                password_hash = generate_password_hash("Admin@123"),
                role          = "admin",
                created_at    = days_ago(random.randint(180, 360)),
                last_login_at = a["last_login_at"],
                is_active     = True,
                avatar_filename = "default.jpg",
            )
            user_objects.append(u)

        customer_objects = []
        for c in CUSTOMER_USERS:
            joined = days_ago(random.randint(60, 365))
            u = User(
                name          = c["name"],
                email         = c["email"],
                phone         = c["phone"],
                password_hash = generate_password_hash("User@123"),
                role          = "customer",
                created_at    = joined,
                updated_at    = joined,
                last_login_at = c["last_login_at"],
                is_active     = True,
                avatar_filename = "default.jpg",
            )
            u._profile = c["profile"]   # temporary attr for seeding logic
            user_objects.append(u)
            customer_objects.append(u)

        db.session.add_all(user_objects)
        db.session.commit()
        print(f"    ✓ {len(user_objects)} users ({len([u for u in user_objects if u.role=='admin'])} admins, "
              f"{len(customer_objects)} customers)")

        # ──────────────────────────────────────────────────────────────────
        # 2. EXPENSE CATEGORIES
        # ──────────────────────────────────────────────────────────────────
        print("🏷   Seeding expense categories …")

        cat_map = {}    # name → ExpenseCategory object (for expense lookup)
        default_cat_objects = []
        for name, desc in DEFAULT_CATEGORIES:
            cat = ExpenseCategory(name=name, description=desc, is_default=True, user_id=None)
            default_cat_objects.append(cat)
        db.session.add_all(default_cat_objects)
        db.session.flush()   # get IDs without committing

        for cat in default_cat_objects:
            cat_map[cat.name] = cat

        # Distribute custom categories among customers (not every customer gets one)
        custom_recipients = random.sample(customer_objects, k=min(6, len(customer_objects)))
        custom_cat_objects = []
        random.shuffle(CUSTOM_CATEGORIES)
        for i, (cname, cdesc) in enumerate(CUSTOM_CATEGORIES):
            owner = custom_recipients[i % len(custom_recipients)]
            cat = ExpenseCategory(
                name        = cname,
                description = cdesc,
                is_default  = False,
                user_id     = owner.id,
            )
            custom_cat_objects.append(cat)
            cat_map[cname] = cat

        db.session.add_all(custom_cat_objects)
        db.session.commit()
        print(f"    ✓ {len(default_cat_objects)} default + {len(custom_cat_objects)} custom categories")

        # ──────────────────────────────────────────────────────────────────
        # 3. EXPENSES
        # ──────────────────────────────────────────────────────────────────
        print("💸  Seeding expenses …")

        all_expense_objects = []
        for user in customer_objects:
            profile    = getattr(user, "_profile", "salaried_mid")
            templates  = EXPENSE_TEMPLATES.get(profile, EXPENSE_TEMPLATES["salaried_mid"])

            # Build weighted list from frequency_weight
            weighted   = []
            for tpl in templates:
                cat_name, title, min_a, max_a, weight = tpl
                weighted.extend([(cat_name, title, min_a, max_a)] * weight)

            num_expenses = random.randint(20, 45)
            for _ in range(num_expenses):
                cat_name, title, min_a, max_a = random.choice(weighted)

                # Fall back to Miscellaneous if category not in cat_map
                cat_obj = cat_map.get(cat_name) or cat_map.get("Miscellaneous")

                amount       = dec(round(random.uniform(min_a, max_a), 2))
                # Spread expenses over last 6 months, more recent dates more common
                days_offset  = int(random.triangular(0, 180, 30))
                expense_date = date_ago(days_offset)
                notes_chance = random.random()
                notes        = fake.sentence(nb_words=random.randint(5, 12)) if notes_chance > 0.4 else None

                exp = Expense(
                    user_id      = user.id,
                    category_id  = cat_obj.id,
                    title        = title,
                    amount       = amount,
                    expense_date = expense_date,
                    created_at   = datetime.combine(expense_date, datetime.min.time()) + timedelta(hours=random.randint(7, 22)),
                    notes        = notes,
                )
                all_expense_objects.append(exp)

        db.session.add_all(all_expense_objects)
        db.session.commit()
        print(f"    ✓ {len(all_expense_objects)} expenses across {len(customer_objects)} customers")

        # ──────────────────────────────────────────────────────────────────
        # 4. REMINDERS
        # ──────────────────────────────────────────────────────────────────
        print("🔔  Seeding reminders …")

        all_reminder_objects = []
        for user in customer_objects:
            profile   = getattr(user, "_profile", "salaried_mid")
            templates = REMINDER_TEMPLATES.get(profile, REMINDER_TEMPLATES["salaried_mid"])

            num_reminders = random.randint(4, 8)
            chosen = random.sample(templates, k=min(num_reminders, len(templates)))

            for title, desc, min_days, max_days in chosen:
                days_offset   = random.randint(min_days, max_days)
                reminder_date = days_from_now(days_offset).replace(
                    hour   = random.choice([8, 9, 10, 18, 19, 20, 21]),
                    minute = random.choice([0, 15, 30, 45]),
                    second = 0,
                    microsecond = 0,
                )
                r = Reminder(
                    user_id       = user.id,
                    title         = title,
                    description   = desc,
                    reminder_date = reminder_date,
                    created_at    = days_ago(random.randint(0, 14)),
                )
                all_reminder_objects.append(r)

        db.session.add_all(all_reminder_objects)
        db.session.commit()
        print(f"    ✓ {len(all_reminder_objects)} reminders")

        # ──────────────────────────────────────────────────────────────────
        # 5. CI CALCULATIONS
        # ──────────────────────────────────────────────────────────────────
        print("📈  Seeding compound interest calculations …")

        all_ci_objects = []
        for user in customer_objects:
            profile  = getattr(user, "_profile", "salaried_mid")
            presets  = CI_PRESETS.get(profile, CI_PRESETS["salaried_mid"])

            # Pick 2-5 random presets for this user
            num_calcs = random.randint(2, min(5, len(presets) * 2))
            for _ in range(num_calcs):
                preset = random.choice(presets)

                principal    = dec(round(random.uniform(preset["min_p"], preset["max_p"]), 2))
                rate         = Decimal(str(random.choice(preset["rates"])))
                years        = random.randint(*preset["years_range"])
                n            = random.choice(preset["n_opts"])

                r_float      = float(rate) / 100.0
                maturity_val = float(principal) * ((1 + r_float / n) ** (n * years))
                maturity     = dec(maturity_val)
                interest     = dec(float(maturity) - float(principal))

                ci = CICalculation(
                    user_id        = user.id,
                    principal      = principal,
                    rate           = rate,
                    years          = years,
                    n_compounds    = n,
                    maturity_amount = maturity,
                    total_interest = interest,
                    calculated_at  = days_ago(random.randint(0, 60)),
                )
                all_ci_objects.append(ci)

        db.session.add_all(all_ci_objects)
        db.session.commit()
        print(f"    ✓ {len(all_ci_objects)} CI calculations")

        # ──────────────────────────────────────────────────────────────────
        # 6. INVESTMENT OPTIONS
        # ──────────────────────────────────────────────────────────────────
        print("💡  Seeding investment options …")

        inv_objects = []
        for opt in INVESTMENT_OPTIONS:
            inv = InvestmentOption(**opt)
            inv_objects.append(inv)

        db.session.add_all(inv_objects)
        db.session.commit()
        print(f"    ✓ {len(inv_objects)} investment options")

        # ──────────────────────────────────────────────────────────────────
        # 7. CONTACT MESSAGES
        # ──────────────────────────────────────────────────────────────────
        print("✉️   Seeding contact messages …")

        msg_objects = []
        for m in CONTACT_MESSAGES:
            submitted = datetime.utcnow() - timedelta(days=m["days_ago"], hours=random.randint(0, 23))
            msg = ContactMessage(
                name         = m["name"],
                email        = m["email"],
                subject      = m["subject"],
                topic        = m["topic"],
                message      = m["message"],
                submitted_at = submitted,
                is_read      = m["is_read"],
            )
            msg_objects.append(msg)

        db.session.add_all(msg_objects)
        db.session.commit()
        print(f"    ✓ {len(msg_objects)} contact messages "
              f"({sum(1 for m in CONTACT_MESSAGES if m['is_read'])} read, "
              f"{sum(1 for m in CONTACT_MESSAGES if not m['is_read'])} unread)")

        # ── Final summary ─────────────────────────────────────────────────
        print()
        print("═" * 58)
        print("✅  SEED COMPLETE — summary")
        print("═" * 58)
        print(f"  Users               : {db.session.query(User).count()}")
        print(f"    ↳ admins          : {db.session.query(User).filter_by(role='admin').count()}")
        print(f"    ↳ customers       : {db.session.query(User).filter_by(role='customer').count()}")
        print(f"  Expense categories  : {db.session.query(ExpenseCategory).count()}")
        print(f"    ↳ default         : {db.session.query(ExpenseCategory).filter_by(is_default=True).count()}")
        print(f"    ↳ user-specific   : {db.session.query(ExpenseCategory).filter_by(is_default=False).count()}")
        print(f"  Expenses            : {db.session.query(Expense).count()}")
        print(f"  Reminders           : {db.session.query(Reminder).count()}")
        print(f"  CI calculations     : {db.session.query(CICalculation).count()}")
        print(f"  Investment options  : {db.session.query(InvestmentOption).count()}")
        print(f"  Contact messages    : {db.session.query(ContactMessage).count()}")
        print("═" * 58)
        print()
        print("🔑  Login credentials")
        print("─" * 40)
        print("  Admins    →  password: Admin@123")
        for a in ADMIN_USERS:
            print(f"             {a['email']}")
        print("  Customers →  password: User@123")
        for c in CUSTOMER_USERS:
            print(f"             {c['email']:40s}  ({c['profile']})")
        print()


if __name__ == "__main__":
    seed_all()
