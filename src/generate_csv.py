import csv
import pandas as pd
from typing import Dict, Any


def create_transactions_csv(statement_data: Dict[str, Any], output_file: str) -> bool:
    if not statement_data or not statement_data.get("transactions"):
        return False

    transactions = statement_data["transactions"]
    required_fields = {"id", "amount", "currency", "date", "counterparty"}

    csv_rows = []
    for tx in transactions:
        if not required_fields.issubset(tx.keys()):
            continue

        try:
            row = {
                "transaction_id": tx["id"],
                "amount": tx["amount"],
                "currency": tx["currency"],
                "date": tx["date"],
                "counterparty": (
                    tx["counterparty"]["name"]
                    if isinstance(tx["counterparty"], dict)
                    else tx["counterparty"]
                ),
                "transaction_description": tx.get("description", ""),
                "transaction_direction": (
                    "кредит" if float(tx["amount"]) >= 0 else "дебет"
                ),
            }
            csv_rows.append(row)
        except (KeyError, ValueError, AttributeError) as e:
            continue

    if not csv_rows:
        return False

    try:
        df = pd.DataFrame(csv_rows)
        df.to_csv(output_file, index=False, encoding="utf-8")
        return True
    except Exception as e:
        try:
            with open(output_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=df.columns)
                writer.writeheader()
                writer.writerows(csv_rows)
            return True
        except IOError as e:
            return False
