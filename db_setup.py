import random
from datetime import date, datetime, timedelta
import mysql.connector
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User, ExpenseCategory, Expense, Reminder, CICalculation, PageContent

# -------------------------------
# MySQL CONFIG - CHANGE PASSWORD
# -------------------------------
DB_HOST = "localhost"
DB_PORT = 3307
DB_USER = "chetan"
DB_PASSWORD = "Chetan_123"  # <----- CHANGE THIS
DB_NAME = "disha_finance"


# --------------------------------------------------
# (1) CREATE DATABASE IF NOT EXISTS
# --------------------------------------------------
def create_database_if_not_exists():
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE DATABASE IF NOT EXISTS {DB_NAME}
        CHARACTER SET utf8mb4 
        COLLATE utf8mb4_unicode_ci;
    """)
    cursor.close()
    conn.close()
    print(f"✔ Database '{DB_NAME}' created/verified.")


# --------------------------------------------------
# (2) SEED ADMINS, CUSTOMERS, CATEGORIES, SAMPLE DATA
# --------------------------------------------------
def seed_data():

    # If any user already exists → skip seeding
    if User.query.count() > 0:
        print("✔ Users already exist — skipping seed.")
        return

    # -------------------------
    # CREATE 3 ADMIN USERS
    # -------------------------
    admin_data = [
        ("Admin One", "admin1@disha.com", "9991112222"),
        ("Admin Two", "admin2@disha.com", "9991113333"),
        ("Admin Three", "admin3@disha.com", "9991114444"),
    ]

    admins = []
    for name, email, phone in admin_data:
        admins.append(User(
            name=name,
            email=email,
            phone=phone,
            role="admin",
            password_hash=generate_password_hash("admin123")
        ))

    db.session.add_all(admins)
    db.session.commit()
    print("✔ 3 admin users added.")

    # -------------------------
    # CREATE 10 CUSTOMER USERS
    # -------------------------

    customer_data = [
        ("Amit Sharma", "amit@example.com", "9876500010"),
        ("Neha Verma", "neha@example.com", "9876500020"),
        ("Rohit Singh", "rohit@example.com", "9876500030"),
        ("Priya Desai", "priya@example.com", "9876500040"),
        ("Karan Patel", "karan@example.com", "9876500050"),
        ("Sara Khan", "sara@example.com", "9876500060"),
        ("Harsh Mehta", "harsh@example.com", "9876500070"),
        ("Divya Rao", "divya@example.com", "9876500080"),
        ("Vikas Yadav", "vikas@example.com", "9876500090"),
        ("Meera Joshi", "meera@example.com", "9876500100"),
    ]

    customers = []
    for name, email, phone in customer_data:
        customers.append(User(
            name=name,
            email=email,
            phone=phone,
            role="customer",
            password_hash=generate_password_hash("customer123")
        ))

    db.session.add_all(customers)
    db.session.commit()
    print("✔ 10 customer users added.")

    # -------------------------
    # DEFAULT EXPENSE CATEGORIES
    # -------------------------
    categories = [
        ExpenseCategory(name="Rent", description="Monthly rent", is_default=True),
        ExpenseCategory(name="Food", description="Groceries & eating out", is_default=True),
        ExpenseCategory(name="Transport", description="Fuel, bus, cab", is_default=True),
        ExpenseCategory(name="Bills", description="Electricity, internet, phone", is_default=True),
        ExpenseCategory(name="Shopping", description="Clothes, accessories", is_default=True),
        ExpenseCategory(name="Entertainment", description="Movies, outings", is_default=True),
    ]

    db.session.add_all(categories)
    db.session.commit()
    print("✔ Expense categories added.")

    # -------------------------
    # RANDOM EXPENSES FOR EACH CUSTOMER
    # -------------------------
    all_categories = ExpenseCategory.query.all()

    for user in customers:
        for _ in range(random.randint(3, 7)):  # 3 to 7 rows per user
            cat = random.choice(all_categories)
            amount = random.randint(200, 8000)
            days_ago = random.randint(1, 60)

            expense = Expense(
                user_id=user.id,
                category_id=cat.id,
                title=f"{cat.name} Expense",
                amount=amount,
                expense_date=date.today() - timedelta(days=days_ago),
                notes=f"Auto generated sample for {user.name}"
            )
            db.session.add(expense)

    db.session.commit()
    print("✔ Random expenses added for customers.")

    # -------------------------
    # RANDOM REMINDERS
    # -------------------------
    for user in customers:
        for _ in range(random.randint(1, 3)):
            reminder_date = date.today() + timedelta(days=random.randint(1, 30))

            reminder = Reminder(
                user_id=user.id,
                reminder_title="Payment Reminder",
                reminder_date=reminder_date,
                note=f"Auto reminder for {user.name}"
            )
            db.session.add(reminder)

    db.session.commit()
    print("✔ Random reminders added.")

    # -------------------------
    # CMS PAGE CONTENT (Home, About, Contact)
    # -------------------------
    cms_entries = [
        PageContent(page_slug="home", section_name="hero_title", content="Welcome to Disha Finance"),
        PageContent(page_slug="home", section_name="hero_subtitle",
                    content="Smart tools to manage expenses, investments & reminders."),
        PageContent(page_slug="about", section_name="intro",
                    content="Disha Finance is a personal finance manager built for students."),
        PageContent(page_slug="contact", section_name="info",
                    content="Contact us at support@disha.com"),
    ]

    db.session.add_all(cms_entries)
    db.session.commit()
    print("✔ CMS content added.")

    print("🎉 DATABASE SEEDING COMPLETE!")


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------
def main():
    create_database_if_not_exists()

    app = create_app()
    with app.app_context():
        db.create_all()
        print("✔ All tables created.")
        seed_data()


if __name__ == "__main__":
    main()
