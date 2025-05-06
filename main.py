import os
from pathlib import Path
from dotenv import load_dotenv

from src._logger import get_logger
from src.bank_statement import StatementAPI
from src.generate_csv import create_transactions_csv

logger = get_logger(__name__)

env_path = Path(__file__).parent / "env.example"
load_dotenv(dotenv_path=env_path)


class StatementProcessor:
    """Class for processing bank statements."""

    def __init__(self, api_version: str = "v1.0"):
        self.api = StatementAPI(api_version=api_version)
        self.output_file = os.getenv("OUTPUT_CSV_FILE")

    def _validate_output_file(self) -> bool:
        """Check if output file path is specified."""
        if not self.output_file:
            logger.warning("OUTPUT_CSV_FILE is not specified in the env.example file.")
            return False
        return True

    def process_statement(self, statement_id: str) -> bool:
        """
        Process a bank statement by downloading and saving to CSV.
        """
        if not self._validate_output_file():
            return False

        statement = self.api.get_statement(statement_id)
        if not statement:
            logger.error(f"Failed to retrieve statement {statement_id}")
            return False

        try:
            create_transactions_csv(statement, self.output_file)
            logger.info(f"Successfully processed statement {statement_id} to {self.output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create CSV for statement {statement_id}: {str(e)}")
            return False


def main():
    """Main entry point for the script."""
    processor = StatementProcessor(api_version="v2.0")
    statement_id = input("Enter the statement ID: ")

    status = processor.api.check_statement_status(statement_id)
    logger.info(f"Statement {statement_id} status: {status}")

    success = processor.process_statement(statement_id)

    if not success:
        logger.error("Statement processing failed")
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
