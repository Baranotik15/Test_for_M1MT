import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from main import df_to_features


@pytest.mark.parametrize(
    "df_data, expected_features",
    [
        (
            pd.DataFrame([
                {
                    "Дата": "2026-02-16",
                    "Область": "Kyiv",
                    "Місто": "Kyiv",
                    "Значення 1": 1,
                    "Значення 2": 0,
                    "Значення 3": 2,
                    "Значення 4": 0,
                    "Значення 5": 0,
                    "Значення 6": 0,
                    "Значення 7": 0,
                    "Значення 8": 0,
                    "Значення 9": 0,
                    "Значення 10": 0,
                    "long": 30.5,
                    "lat": 50.5
                },
                {
                    "Дата": "2026-02-17",
                    "Область": "Lviv",
                    "Місто": "Lviv",
                    "Значення 1": 0,
                    "Значення 2": 1,
                    "Значення 3": 0,
                    "Значення 4": 0,
                    "Значення 5": 0,
                    "Значення 6": 0,
                    "Значення 7": 0,
                    "Значення 8": 0,
                    "Значення 9": 0,
                    "Значення 10": 0,
                    "long": None,
                    "lat": 49.8
                }
            ]),
            [
                {
                    "attributes": {
                        "date": "2026-02-16",
                        "region": "Kyiv",
                        "city": "Kyiv",
                        "value_1": 1,
                        "value_2": 0,
                        "value_3": 2,
                        "value_4": 0,
                        "value_5": 0,
                        "value_6": 0,
                        "value_7": 0,
                        "value_8": 0,
                        "value_9": 0,
                        "value_10": 0,
                        "long": 30.5,
                        "lat": 50.5
                    },
                    "geometry": {
                        "x": 30.5,
                        "y": 50.5,
                        "spatialReference": {"wkid": 4326}
                    }
                }
            ]
        )
    ]
)
def test_df_to_features(df_data, expected_features):
    mock_feature = MagicMock()
    with patch("main.Feature", return_value=mock_feature) as MockFeature:
        features = df_to_features(df_data)
        assert len(features) == len(expected_features)
        for expected_call in expected_features:
            MockFeature.assert_any_call(
                attributes=expected_call["attributes"],
                geometry=expected_call["geometry"]
            )
