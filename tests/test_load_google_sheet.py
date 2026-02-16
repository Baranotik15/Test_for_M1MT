import pandas as pd
import pytest
import warnings
from unittest.mock import patch
from main import load_google_sheet

@pytest.mark.parametrize(
    "mock_data, expected_lengths, expected_types, expected_values",
    [
        (
            pd.DataFrame({
                "long": ["30,5", "31,6", None],
                "lat": ["50,1", "51,2", "52,3"],
                "Значення 1": [1, None, 3],
                "Значення 2": [None, 2, None],
                "Значення 3": [0, 0, 0],
                "Значення 4": [None, None, None],
                "Значення 5": [None, None, None],
                "Значення 6": [None, None, None],
                "Значення 7": [None, None, None],
                "Значення 8": [None, None, None],
                "Значення 9": [None, None, None],
                "Значення 10": [None, None, None],
            }),
            3,
            {"long": "float32", "lat": "float32", **{f"Значення {i}": "uint16" for i in range(1,11)}},
            {"Значення 1_1": 0, "Значення 2_0": 0}
        )
    ]
)
def test_load_google_sheet_success(mock_data, expected_lengths, expected_types, expected_values):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        with patch("main.pd.read_csv", return_value=mock_data):
            df = load_google_sheet("dummy_sheet_id", gid=0)

    assert len(df) == expected_lengths
    for col, dtype in expected_types.items():
        assert str(df[col].dtype) == dtype
    assert df["Значення 1"].iloc[1] == expected_values["Значення 1_1"]
    assert df["Значення 2"].iloc[0] == expected_values["Значення 2_0"]


@pytest.mark.parametrize(
    "side_effect_exception",
    [
        Exception("Network error")
    ]
)
def test_load_google_sheet_fail(side_effect_exception):
    with patch("main.pd.read_csv", side_effect=side_effect_exception):
        with pytest.raises(ValueError) as excinfo:
            load_google_sheet("dummy_sheet_id", gid=0)
        assert "Failed to load Google Sheet" in str(excinfo.value)
