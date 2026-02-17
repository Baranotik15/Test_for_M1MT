"""
Tests for loading Google Sheets.
"""

import pytest
from unittest.mock import patch
import pandas as pd
from utils.google_sheets import load_google_sheet, GoogleSheetsError


def test_load_google_sheet_success():
    """Test successful loading of Google Sheet."""
    mock_df = pd.DataFrame({
        "Дата": ["2026-01-01"],
        "Область": ["Kyiv"],
        "Місто": ["Kyiv"],
        "long": ["30,5"],
        "lat": ["50,5"],
        **{f"Значення {i}": [1] for i in range(1, 11)}
    })

    with patch("pandas.read_csv", return_value=mock_df):
        df = load_google_sheet("test_sheet_id", gid=0)

        assert len(df) == 1
        assert df["long"].dtype == "float32"
        assert df["lat"].dtype == "float32"
        assert df["long"].iloc[0] == 30.5
        assert df["lat"].iloc[0] == 50.5


def test_load_google_sheet_error():
    """Test that loading errors are handled correctly."""
    with patch("pandas.read_csv", side_effect=Exception("Network error")):
        with pytest.raises(GoogleSheetsError):
            load_google_sheet("test_sheet_id", gid=0)
