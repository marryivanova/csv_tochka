import pytest
import pandas as pd
from datetime import datetime

from src._faker import generate_fake_transactions
from src.generate_csv import create_transactions_csv


# Test data generation
class TestGenerateFakeTransactions:
    def test_returns_list(self):
        transactions = generate_fake_transactions()
        assert isinstance(transactions, list)

    def test_correct_number_of_transactions(self):
        for num in [1, 5, 10]:
            transactions = generate_fake_transactions(num)
            assert len(transactions) == num

    def test_transaction_structure(self):
        transactions = generate_fake_transactions(1)
        transaction = transactions[0]

        required_keys = {
            "transaction_id",
            "amount",
            "currency",
            "date",
            "counterparty",
            "transaction_description",
            "transaction_direction",
            "account_number",
            "location",
        }
        assert set(transaction.keys()) >= required_keys

    def test_amount_ranges(self):
        transactions = generate_fake_transactions(100)
        amounts = [t["amount"] for t in transactions]
        assert all(-150000 <= amt <= 150000 for amt in amounts)

    def test_date_format(self):
        transactions = generate_fake_transactions(5)
        for t in transactions:
            datetime.strptime(t["date"], "%Y-%m-%d")

    def test_direction_calculation(self):
        transactions = generate_fake_transactions(10)
        for t in transactions:
            expected_dir = "credit" if t["amount"] >= 0 else "debit"
            assert t["transaction_direction"] == expected_dir


# Test CSV creation
class TestCreateTransactionsCSV:
    @pytest.fixture
    def sample_data(self):
        return {
            "transactions": [
                {
                    "id": "TX123",
                    "amount": 100.0,
                    "currency": "USD",
                    "date": "2023-01-01",
                    "counterparty": "Test Corp",
                    "description": "Test payment",
                },
                {
                    "id": "TX124",
                    "amount": -50.0,
                    "currency": "EUR",
                    "date": "2023-01-02",
                    "counterparty": {"name": "Test LLC"},
                    "description": "Test withdrawal",
                },
            ]
        }

    def test_successful_creation(self, sample_data, tmp_path):
        output_file = tmp_path / "test_transactions.csv"
        result = create_transactions_csv(sample_data, str(output_file))

        assert result is True
        assert output_file.exists()

        df = pd.read_csv(output_file)
        assert len(df) == 2
        assert set(df.columns) == {
            "transaction_id",
            "amount",
            "currency",
            "date",
            "counterparty",
            "transaction_description",
            "transaction_direction",
        }

    def test_empty_data(self, tmp_path):
        output_file = tmp_path / "empty.csv"
        assert create_transactions_csv(None, str(output_file)) is False
        assert create_transactions_csv({}, str(output_file)) is False
        assert create_transactions_csv({"transactions": []}, str(output_file)) is False

    def test_missing_fields(self, tmp_path):
        output_file = tmp_path / "missing.csv"
        bad_data = {
            "transactions": [
                {"id": "TX125", "amount": 100},
                {"currency": "USD", "date": "2023-01-01"},
            ]
        }

        assert create_transactions_csv(bad_data, str(output_file)) is False

    def test_invalid_amounts(self, tmp_path):
        output_file = tmp_path / "invalid.csv"
        test_data = {
            "transactions": [
                {
                    "id": "TX126",
                    "amount": "not_a_number",
                    "currency": "USD",
                    "date": "2023-01-01",
                    "counterparty": "Test Inc",
                }
            ]
        }

        assert create_transactions_csv(test_data, str(output_file)) is False
