"""
Tests for data expansion using the "unit ladder" rule.
"""

import pandas as pd
import pytest
from utils.data_processing import expand_row, expand_dataframe


@pytest.mark.parametrize(
    "row_data, expected_length, expected_first, expected_last",
    [
        (
            pd.Series({f"Значення {i}": 0 for i in range(1, 11)}),
            0,
            None,
            None
        ),
        (
            pd.Series({
                "Значення 1": 2,
                "Значення 2": 1,
                "Значення 3": 0,
                "Значення 4": 0,
                "Значення 5": 0,
                "Значення 6": 0,
                "Значення 7": 0,
                "Значення 8": 0,
                "Значення 9": 0,
                "Значення 10": 0
            }),
            2,
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ),
        (
            pd.Series({
                "Значення 1": 5,
                "Значення 2": 3,
                "Значення 3": 0,
                "Значення 4": 0,
                "Значення 5": 0,
                "Значення 6": 0,
                "Значення 7": 0,
                "Значення 8": 0,
                "Значення 9": 0,
                "Значення 10": 0
            }),
            5,
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        )
    ]
)
def test_expand_row(row_data, expected_length, expected_first, expected_last):
    """Test that a single row is expanded correctly."""
    value_cols = [f'Значення {i}' for i in range(1, 11)]
    result = expand_row(row_data, value_cols)

    assert len(result) == expected_length

    if expected_length > 0:
        first_row = result[0][value_cols].tolist()
        last_row = result[-1][value_cols].tolist()
        assert first_row == expected_first
        assert last_row == expected_last


@pytest.mark.parametrize(
    "df_data, expected_length",
    [
        (
            pd.DataFrame([
                {f"Значення {i}": 2 if i == 1 else 1 for i in range(1, 11)},
                {f"Значення {i}": 1 if i == 2 else 0 for i in range(1, 11)}
            ]),
            3
        ),
        (
            pd.DataFrame([
                {f"Значення {i}": 0 for i in range(1, 11)}
            ]),
            0
        )
    ]
)
def test_expand_dataframe(df_data, expected_length):
    """Test that a DataFrame is expanded correctly."""
    value_cols = [f'Значення {i}' for i in range(1, 11)]
    result = expand_dataframe(df_data, value_cols, show_progress=False)
    assert len(result) == expected_length
