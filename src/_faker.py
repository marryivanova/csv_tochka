from faker import Faker
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


def generate_fake_transactions(num: int = 10) -> List[Dict[str, Any]]:
    """
    Generates a list of fake bank transactions.
    """
    fake = Faker("en_US")
    currencies = ["RUB", "USD", "EUR", "CNY"]

    counterparty_types = {
        "retail": [
            "LLC Flowers",
            "Ivanov Enterprise",
            "Lukoil Gas Station",
            "Pyaterochka Store",
        ],
        "banking": ["Sberbank", "Tinkoff Bank", "VTB Bank"],
        "tech": ["Amazon Inc", "Google LLC", "Apple Inc", "Yandex LLC"],
        "services": ["Netflix", "Spotify", "Microsoft Azure"],
    }

    descriptions = {
        "payment": ["Service payment", "Invoice payment", "Service subscription"],
        "transfer": ["Personal transfer", "International transfer", "Account transfer"],
        "deposit": ["Account top-up", "Refund", "Salary deposit"],
        "withdrawal": ["Fee charge", "Fine payment", "Cash withdrawal"],
    }

    transactions = []
    for _ in range(num):
        amount = round(random.uniform(-150000, 150000), 2)
        counterparty_category = random.choice(list(counterparty_types.keys()))
        description_category = (
            "deposit"
            if amount > 0
            else random.choice(["payment", "transfer", "withdrawal"])
        )

        transaction = {
            "transaction_id": fake.unique.bothify(text="TR#########"),
            "amount": amount,
            "currency": random.choice(currencies),
            "date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime(
                "%Y-%m-%d"
            ),
            "counterparty": random.choice(counterparty_types[counterparty_category]),
            "transaction_description": random.choice(
                descriptions[description_category]
            ),
            "transaction_direction": "credit" if amount >= 0 else "debit",
            "account_number": fake.iban(),
            "location": fake.city() if random.random() > 0.5 else None,
        }
        transactions.append(transaction)

    return transactions
