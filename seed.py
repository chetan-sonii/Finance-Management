# seed_reminders.py
"""
Seed the database with some sample reminders for testing the Calendar tab.

- Creates multiple reminders for user_id=14 (different days + same day).
- Also creates a few reminders for other users (1, 2, 3) so the calendar
  is more realistic.
"""

from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models import Reminder, User


def main():
    app = create_app()

    with app.app_context():
        # --- sanity check: does user 14 exist? ---
        user14 = User.query.get(14)
        if not user14:
            print("❗ user_id=14 not found. Adjust IDs in this script if needed.")
            return

        print("✔ Found user 14:", user14.email)

        # OPTIONAL: clear existing reminders to avoid duplicates
        # Comment this out if you don't want to wipe old data.
        #
        # Reminder.query.delete()
        # db.session.commit()

        base = datetime(2025, 12, 1, 18, 0)  # 1 Dec 2025, 6 PM

        def dt(days_offset: int, hour: int = 18, minute: int = 0):
            """Helper: base date + offset, with given time."""
            return base + timedelta(days=days_offset, hours=hour - 18, minutes=minute)

        samples = [
            # ---- Mostly user 14 ----
            {
                "user_id": 14,
                "title": "WiFi bill",
                "description": "JioFiber – monthly internet bill",
                "reminder_date": dt(3, 20),  # 4 Dec 2025, 8 PM
            },
            {
                "user_id": 14,
                "title": "Credit card payment",
                "description": "HDFC credit card – last date",
                "reminder_date": dt(7, 19),  # 8 Dec 2025, 7 PM
            },
            {
                "user_id": 14,
                "title": "SIP – Nifty 50 Index",
                "description": "Monthly SIP auto-debit",
                "reminder_date": dt(7, 9),  # same date as CC payment, different time
            },
            {
                "user_id": 14,
                "title": "Electricity bill",
                "description": "CSPDCL – light bill",
                "reminder_date": dt(10, 18),  # 11 Dec 2025, 6 PM
            },
            {
                "user_id": 14,
                "title": "Netflix subscription",
                "description": "UPI auto-pay",
                "reminder_date": dt(10, 21),  # same day as electricity, later
            },
            {
                "user_id": 14,
                "title": "Room rent",
                "description": "Monthly house rent payment",
                "reminder_date": dt(0, 9),  # 1 Dec 2025, 9 AM
            },
            {
                "user_id": 14,
                "title": "Laptop EMI",
                "description": "Axis Bank EMI – don’t miss!",
                "reminder_date": dt(15, 8),  # 16 Dec 2025, 8 AM
            },
            {
                "user_id": 14,
                "title": "College fee",
                "description": "Semester fee – pay online",
                "reminder_date": dt(20, 10),  # 21 Dec 2025, 10 AM
            },

            # ---- Other users, so calendar has more data ----
            {
                "user_id": 1,
                "title": "User1 – SIP",
                "description": "Equity mutual fund SIP",
                "reminder_date": dt(5, 7),
            },
            {
                "user_id": 1,
                "title": "User1 – Bike insurance",
                "description": "Renew policy before expiry",
                "reminder_date": dt(18, 18),
            },
            {
                "user_id": 2,
                "title": "User2 – WiFi bill",
                "description": "Broadband monthly payment",
                "reminder_date": dt(3, 19),
            },
            {
                "user_id": 2,
                "title": "User2 – Credit card bill",
                "description": "Payment via netbanking",
                "reminder_date": dt(7, 20),
            },
            {
                "user_id": 3,
                "title": "User3 – EMI – Car",
                "description": "Bank EMI auto-debit",
                "reminder_date": dt(10, 9),
            },
            {
                "user_id": 3,
                "title": "User3 – Electricity",
                "description": "State electricity board",
                "reminder_date": dt(12, 18),
            },
            {
                "user_id": 3,
                "title": "User3 – OTT bundle",
                "description": "Prime + Netflix + Disney+",
                "reminder_date": dt(20, 21),
            },
        ]

        reminder_objects = []
        for item in samples:
            r = Reminder(
                user_id=item["user_id"],
                title=item["title"],
                description=item["description"],
                reminder_date=item["reminder_date"],
            )
            reminder_objects.append(r)

        db.session.add_all(reminder_objects)
        db.session.commit()

        print(f"✅ Seeded {len(reminder_objects)} reminders.")


if __name__ == "__main__":
    main()
