import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from src._logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
env_path = Path(__file__).parent / "env.example"

if not env_path.exists():
    raise FileNotFoundError(f"env.example file not found at {env_path}")

load_dotenv(dotenv_path=env_path)

# Required configuration
API_BASE_URL = os.getenv("API_BASE_URL")
SANDBOX_API_BASE_URL = os.getenv("TOCHKA_SANDBOX_API_BASE_URL")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
USE_SANDBOX = os.getenv("TOCHKA_USE_SANDBOX", "false").lower() == "true"
API_TOKEN = os.getenv("ACCESS_TOKEN")

# Validation
required_vars = {
    "API_BASE_URL": API_BASE_URL,
    "TOCHKA_SANDBOX_API_BASE_URL": SANDBOX_API_BASE_URL,
    "ACCOUNT_ID": ACCOUNT_ID,
    "API_TOKEN": API_TOKEN
}

missing = [name for name, value in required_vars.items() if not value]
if missing:
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


class StatementAPI:
    """Class for handling bank statement operations."""

    def __init__(self, api_version: str = "v2"):
        self.api_version = api_version
        self.base_url = SANDBOX_API_BASE_URL if USE_SANDBOX else API_BASE_URL

    def _build_url(self) -> str:
        """Construct the full API URL for statements endpoint."""
        endpoint = f"/open-banking/{self.api_version}/statements"
        return f"{self.base_url.rstrip('/')}{endpoint}"

    def _get_statement_url(self, statement_id: str) -> str:
        """Construct URL to fetch a specific statement by ID."""
        return f"{self.base_url.rstrip('/')}/open-banking/{self.api_version}/accounts/{ACCOUNT_ID}/statements/{statement_id}"

    @staticmethod
    def _get_headers() -> Dict[str, str]:
        """Get default request headers."""
        return {
            "Authorization": f"Bearer {API_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _make_post_request(self, payload: Dict[str, Any], timeout: int = 30) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Make a POST API request and handle common errors."""
        url = self._build_url()
        headers = self._get_headers()

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" | Response: {e.response.text}"
            logger.error(f"API request failed: {error_msg}")
            return None, error_msg

    def get_statement(self, statement_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific bank statement by ID."""
        url = self._get_statement_url(statement_id)
        headers = self._get_headers()

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" | Response: {e.response.text}"
            logger.error(f"API request failed: {error_msg}")
            return None

    def check_statement_status(self, statement_id: str) -> Optional[str]:
        """
        Check the status of the statement via GET request.
        """
        statement = self.get_statement(statement_id)
        if not statement:
            return None
        return statement.get("status")

    def request_statement(self, from_date: str, to_date: str, statement_format: str = "json") -> Optional[Dict[str, Any]]:
        """
        Request a new bank statement.
        """
        payload = {
            "account_id": ACCOUNT_ID,
            "from_date": from_date,
            "to_date": to_date,
            "format": statement_format
        }

        logger.info(f"Requesting statement for account {ACCOUNT_ID} from {from_date} to {to_date}")

        response, error = self._make_post_request(payload)
        if error:
            return None

        return response
