import json
import os
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_mock_data(file_name: str) -> Any:
    """Load and return JSON data from src/app/data/<file_name>.

    Raises FileNotFoundError if the file does not exist and json.JSONDecodeError
    if the file cannot be parsed as JSON.
    """
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Mock data file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)

