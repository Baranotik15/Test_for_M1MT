import logging
from urllib.parse import urlparse, parse_qs
import pandas as pd

logger = logging.getLogger(__name__)


class GoogleSheetsError(Exception):
    pass


def parse_google_sheet_url(url: str) -> tuple[str, int]:
    """Parse Google Sheets URL and extract sheet ID and GID."""
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        sheet_id = path_parts[path_parts.index("d") + 1]
    except (ValueError, IndexError) as e:
        error_msg = f"Invalid Google Sheets URL: {url}"
        logger.error(error_msg)
        raise GoogleSheetsError(error_msg) from e

    query = parse_qs(parsed.query)
    fragment = parse_qs(parsed.fragment)
    gid = int(query.get("gid", fragment.get("gid", ["0"]))[0])

    return sheet_id, gid


def load_google_sheet(
    sheet_id: str,
    gid: int = 0,
    value_columns: list[str] = None
) -> pd.DataFrame:
    """Load Google Sheet and return prepared DataFrame."""
    if value_columns is None:
        value_columns = [f'Значення {i}' for i in range(1, 11)]

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    try:
        df = pd.read_csv(url)
        logger.info(f"Loaded {len(df)} rows")
    except Exception as e:
        error_msg = f"Failed to load Google Sheet: {e}"
        logger.error(error_msg)
        raise GoogleSheetsError(error_msg) from e

    df['long'] = pd.to_numeric(df['long'].str.replace(',', '.'), errors='coerce').astype("float32")
    df['lat'] = pd.to_numeric(df['lat'].str.replace(',', '.'), errors='coerce').astype("float32")

    for col in value_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype("uint16")

    return df
