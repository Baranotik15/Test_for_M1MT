import logging
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


def expand_row(row: pd.Series, value_columns: Optional[list[str]] = None) -> list[pd.Series]:
    """Expand row according to unit ladder rule."""
    if value_columns is None:
        value_columns = [f'Значення {i}' for i in range(1, 11)]

    values = row[value_columns].values
    max_val = values.max()

    if max_val == 0:
        return []

    new_rows = []
    for i in range(1, max_val + 1):
        new_row = row.copy()
        for j, val in enumerate(values):
            new_row[value_columns[j]] = 1 if val >= i else 0
        new_rows.append(new_row)

    return new_rows


def expand_dataframe(
    df: pd.DataFrame,
    value_columns: Optional[list[str]] = None,
    show_progress: bool = True
) -> pd.DataFrame:
    """Apply expand_row to all DataFrame rows."""
    if value_columns is None:
        value_columns = [f'Значення {i}' for i in range(1, 11)]

    expanded_rows = []
    iterator = df.iterrows()

    if show_progress:
        try:
            from tqdm import tqdm
            iterator = tqdm(df.iterrows(), total=len(df), desc="Expanding", unit="row")
        except ImportError:
            pass

    for _, row in iterator:
        expanded_rows.extend(expand_row(row, value_columns))

    result_df = pd.DataFrame(expanded_rows).reset_index(drop=True)
    logger.info(f"Expanded {len(df)} → {len(result_df)} rows")

    return result_df


def validate_dataframe(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """Validate DataFrame has all required columns."""
    missing = set(required_columns) - set(df.columns)
    if missing:
        error_msg = f"Missing columns: {missing}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    return True
