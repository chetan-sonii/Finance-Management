from app import create_app
from app.extensions import db
from app.models import InvestmentOption

app = create_app()

def seed_investments():
    print(">>> Seeding investment options...")

    investments = [
        {
            "name": "Gold Investment",
            "slug": "gold",
            "icon_class": "lni lni-diamond",
            "tagline": "A traditional hedge against inflation",
            "section1_label": "Why consider gold?",
            "section1_points": "Preserves value during inflation\nActs as a safe haven asset\nHighly liquid investment",
            "section2_label": "Risks & points to note",
            "section2_points": "No regular income\nPrices can fluctuate short-term\nStorage costs for physical gold",
            "risk_pill_text": "Medium risk",
            "risk_pill_level": "medium",
            "external_label": "View gold prices",
            "external_url": "https://www.mcxindia.com/market-data",
            "sort_order": 1,
        },
        {
            "name": "Fixed Deposit (FD)",
            "slug": "fixed-deposit",
            "icon_class": "lni lni-bank",
            "tagline": "Safe and stable returns from banks",
            "section1_label": "How it works",
            "section1_points": "Invest a lump sum\nEarn fixed interest\nCapital protected",
            "section2_label": "Limitations",
            "section2_points": "Lower returns\nInterest taxed\nPoor inflation beating",
            "risk_pill_text": "Low risk",
            "risk_pill_level": "low",
            "external_label": "Compare FD rates",
            "external_url": "https://www.bankbazaar.com/fixed-deposit.html",
            "sort_order": 2,
        },
        {
            "name": "Mutual Funds",
            "slug": "mutual-funds",
            "icon_class": "lni lni-stats-up",
            "tagline": "Professionally managed market investments",
            "section1_label": "Why invest in mutual funds?",
            "section1_points": "Diversified portfolio\nManaged by experts\nSuitable for long-term goals",
            "section2_label": "Risks",
            "section2_points": "Market-linked returns\nExpense ratios\nRequires patience",
            "risk_pill_text": "Medium risk",
            "risk_pill_level": "medium",
            "external_label": "Explore mutual funds",
            "external_url": "https://www.moneycontrol.com/mutual-funds/",
            "sort_order": 3,
        },
        {
            "name": "Systematic Investment Plan (SIP)",
            "slug": "sip",
            "icon_class": "lni lni-reload",
            "tagline": "Invest small amounts regularly",
            "section1_label": "How SIP helps",
            "section1_points": "Disciplined investing\nRupee cost averaging\nFlexible amounts",
            "section2_label": "Things to remember",
            "section2_points": "Market fluctuations\nNeeds consistency\nLong-term commitment",
            "risk_pill_text": "Medium risk",
            "risk_pill_level": "medium",
            "external_label": "SIP calculator",
            "external_url": "https://groww.in/calculators/sip-calculator",
            "sort_order": 4,
        },
        {
            "name": "Stocks / Equity",
            "slug": "stocks",
            "icon_class": "lni lni-bar-chart",
            "tagline": "Direct ownership in companies",
            "section1_label": "Benefits",
            "section1_points": "High growth potential\nDividends\nOwnership rights",
            "section2_label": "Risks involved",
            "section2_points": "High volatility\nRequires research\nEmotional discipline needed",
            "risk_pill_text": "High risk",
            "risk_pill_level": "high",
            "external_label": "Visit NSE",
            "external_url": "https://www.nseindia.com/",
            "sort_order": 5,
        },
        {
            "name": "Real Estate",
            "slug": "real-estate",
            "icon_class": "lni lni-home",
            "tagline": "Property-based long-term investment",
            "section1_label": "Why real estate?",
            "section1_points": "Rental income\nAsset appreciation\nPhysical ownership",
            "section2_label": "Challenges",
            "section2_points": "High capital needed\nLow liquidity\nLegal issues",
            "risk_pill_text": "Medium–High risk",
            "risk_pill_level": "high",
            "external_label": "Property listings",
            "external_url": "https://www.99acres.com/",
            "sort_order": 6,
        },
        {
            "name": "Public Provident Fund (PPF)",
            "slug": "ppf",
            "icon_class": "lni lni-shield",
            "tagline": "Government-backed tax-saving scheme",
            "section1_label": "Key features",
            "section1_points": "15-year lock-in\nTax-free returns\nSafe investment",
            "section2_label": "Limitations",
            "section2_points": "Long lock-in\nAnnual deposit limit\nLower liquidity",
            "risk_pill_text": "Low risk",
            "risk_pill_level": "low",
            "external_label": "PPF details",
            "external_url": "https://www.incometaxindia.gov.in/",
            "sort_order": 7,
        },
        {
            "name": "National Pension Scheme (NPS)",
            "slug": "nps",
            "icon_class": "lni lni-investment",
            "tagline": "Retirement-focused investment plan",
            "section1_label": "Why NPS?",
            "section1_points": "Tax benefits\nMarket-linked growth\nRetirement corpus",
            "section2_label": "Considerations",
            "section2_points": "Partial lock-in\nMarket exposure\nWithdrawal rules",
            "risk_pill_text": "Medium risk",
            "risk_pill_level": "medium",
            "external_label": "NPS portal",
            "external_url": "https://www.npscra.nsdl.co.in/",
            "sort_order": 8,
        },
        {
            "name": "Cryptocurrency",
            "slug": "cryptocurrency",
            "icon_class": "lni lni-bitcoin",
            "tagline": "Digital assets with high volatility",
            "section1_label": "Why people invest",
            "section1_points": "Decentralized\nHigh return potential\nGlobal access",
            "section2_label": "Major risks",
            "section2_points": "Extreme volatility\nRegulatory uncertainty\nSecurity risks",
            "risk_pill_text": "Very high risk",
            "risk_pill_level": "high",
            "external_label": "Learn about crypto",
            "external_url": "https://coinmarketcap.com/",
            "sort_order": 9,
        },
        {
            "name": "Exchange Traded Funds (ETF)",
            "slug": "etf",
            "icon_class": "lni lni-layers",
            "tagline": "Index-based low-cost investment",
            "section1_label": "ETF advantages",
            "section1_points": "Low expense ratio\nDiversification\nEasy trading",
            "section2_label": "Limitations",
            "section2_points": "Market risk\nTracking error\nRequires demat account",
            "risk_pill_text": "Medium risk",
            "risk_pill_level": "medium",
            "external_label": "ETF list",
            "external_url": "https://www.nseindia.com/market-data/exchange-traded-funds-etf",
            "sort_order": 10,
        },
    ]

    for data in investments:
        exists = InvestmentOption.query.filter_by(slug=data["slug"]).first()
        if not exists:
            db.session.add(InvestmentOption(**data))

    db.session.commit()
    print("✔ Investment options seeded successfully")


if __name__ == "__main__":
    with app.app_context():
        seed_investments()
