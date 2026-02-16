import dotenv
import pandas as pd
from os import getenv
from urllib.parse import urlparse, parse_qs
from arcgis.gis import GIS
from arcgis.features import Feature


dotenv.load_dotenv()


def parse_google_sheet_url(url: str) -> tuple[str, int]:
    """
    Parse Google Sheets URL and return (sheet_id, gid).

    Example URL:
    https://docs.google.com/spreadsheets/d/12846JbH2PwR0wN8eLVnosg4xujw-04gKyyD6RuElc-4/edit?gid=0#gid=0
    Returns: ("12846JbH2PwR0wN8eLVnosg4xujw-04gKyyD6RuElc-4", 0)
    """
    parsed = urlparse(url)
    path_parts = parsed.path.split('/')

    try:
        sheet_id_index = path_parts.index("d") + 1
        sheet_id = path_parts[sheet_id_index]
    except (ValueError, IndexError):
        raise ValueError("Invalid Google Sheets URL: cannot find sheet ID")

    query = parse_qs(parsed.query)
    fragment = parse_qs(parsed.fragment)

    gid = int(
        query.get("gid", fragment.get("gid", ["0"]))[0]
    )

    return sheet_id, gid


def load_google_sheet(sheet_id: str, gid: int = 0) -> pd.DataFrame:
    """
    Load a Google Sheet by sheet ID and GID and return a prepared DataFrame.

    Converts 'long' and 'lat' columns to float32.
    Converts 'Значення 1-10' columns to uint16, filling NaN with 0.
    Raises ValueError if the sheet cannot be loaded.
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
    except Exception as e:
        raise ValueError(f"Failed to load Google Sheet. Check the URL or your internet connection.\nError: {e}")

    df['long'] = pd.to_numeric(df['long'].str.replace(',', '.'), errors='coerce').astype("float32")
    df['lat'] = pd.to_numeric(df['lat'].str.replace(',', '.'), errors='coerce').astype("float32")

    for i in range(1, 11):
        col = f'Значення {i}'
        df[col] = df[col].fillna(0).astype("uint16")

    return df


def expand_row(row: pd.Series) -> list:
    """
    Expand a single row into multiple rows according to the "unit ladder" rule.
    Returns a list of new rows (as Series).
    """
    value_cols = [f'Значення {i}' for i in range(1, 11)]
    values = row[value_cols].values
    max_val = values.max()
    if max_val == 0:
        return []
    new_rows = []
    for i in range(1, max_val + 1):
        new_row = row.copy()
        for j, val in enumerate(values):
            new_row[value_cols[j]] = 1 if val >= i else 0
        new_rows.append(new_row)
    return new_rows


def expand_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply expand_row to all rows of the DataFrame and return the expanded DataFrame.
    """
    expanded_rows = []
    for idx, row in df.iterrows():
        new_rows = expand_row(row)
        expanded_rows.extend(new_rows)
    return pd.DataFrame(expanded_rows)


def df_to_features(df: pd.DataFrame) -> list:
    """
    Convert a DataFrame to a list of ArcGIS Feature objects.

    Each row becomes a Feature with attributes mapped to the feature layer
    and geometry set from 'long' and 'lat'.

    Args:
        df (pd.DataFrame): DataFrame with columns 'Дата', 'Область', 'Місто',
                           'Значення 1'..'Значення 10', 'long', 'lat'.

    Returns:
        List[Feature]: List of Features ready for adding to a Feature Layer.
    """
    features = []

    for _, row in df.iterrows():
        if pd.isna(row["long"]) or pd.isna(row["lat"]):
            continue

        attr = {
            "date": str(row["Дата"]),
            "region": str(row["Область"]),
            "city": str(row["Місто"]),
            "value_1": int(row["Значення 1"]),
            "value_2": int(row["Значення 2"]),
            "value_3": int(row["Значення 3"]),
            "value_4": int(row["Значення 4"]),
            "value_5": int(row["Значення 5"]),
            "value_6": int(row["Значення 6"]),
            "value_7": int(row["Значення 7"]),
            "value_8": int(row["Значення 8"]),
            "value_9": int(row["Значення 9"]),
            "value_10": int(row["Значення 10"]),
            "long": float(row["long"]),
            "lat": float(row["lat"])
        }

        geom = {
            "x": float(row["long"]),
            "y": float(row["lat"]),
            "spatialReference": {"wkid": 4326}
        }

        features.append(Feature(attributes=attr, geometry=geom))

    return features


def main():
    try:
        url_data = parse_google_sheet_url(input("Enter Google Sheet URL: "))
        SHEET_ID, GID = url_data

        df = load_google_sheet(SHEET_ID, GID)
        print("Original table:", len(df))

        df_expanded = expand_dataframe(df)
        print("Expanded table:", len(df_expanded))
        print(df_expanded.head(10))

        item_id = getenv("item_id")
        gis = GIS()
        item = gis.content.get(item_id)
        layer = item.layers[0]

        fields = layer.properties.fields

        # ПОЛЯ В ЗАДАНИИ НЕ СООТВЕТСВУЮТ РЕАЛЬНЫМ ЗНАЧЕНИЯМ ПРОШУ ОБРАТИТЬ ВНИМАНЕ !!!
        print("\n--- ПРОВЕРКА ПОЛЕЙ СЛОЯ ---")
        for f in fields:
            print(f"System Name: '{f.name}' | Type: {f.type} | Alias: {f.alias}")
        print("---------------------------\n")

        features = df_to_features(df_expanded)
        batch_size = 500

        print("Starting batch processing...")
        for i in range(0, len(features), batch_size):
            try:
                layer.edit_features(adds=features[i:i + batch_size])
                print(f"Added features {i} to {i + len(features[i:i + batch_size])}")
            except Exception as e:
                print(f"Failed to add features {i}-{i + batch_size}: {e}")

    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
