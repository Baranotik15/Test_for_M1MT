import os
import pandas as pd
from urllib.parse import urlparse, parse_qs


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
    gid = int(query.get("gid", ["0"])[0])

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


def save_to_csv(df: pd.DataFrame, sheet_id: str) -> str:
    """
    Save the DataFrame to a CSV file in the 'data/' folder.
    File name format: {number_of_existing_files + 1}_expanded_data_{sheet_id}.csv
    Returns the file path.
    """

    folder = "data"
    os.makedirs(folder, exist_ok=True)

    existing_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    file_number = len(existing_files) + 1

    output_file = os.path.join(folder, f"{file_number}_expanded_data_{sheet_id}.csv")
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    return output_file


def main():
    try:
        url_data = parse_google_sheet_url(input("Enter Google Sheet URL: "))
        SHEET_ID, GID = url_data

        df = load_google_sheet(SHEET_ID, GID)
        print("Original table:", len(df))

        df_expanded = expand_dataframe(df)
        print("Expanded table:", len(df_expanded))
        print(df_expanded.head(10))

        csv_file = save_to_csv(df_expanded, SHEET_ID)
        print(f"CSV file saved: {csv_file}")

    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
