import logging
import argparse
import sys
from datetime import datetime
from pathlib import Path

import config
from utils.logger import setup_logging
from utils.google_sheets import parse_google_sheet_url, load_google_sheet, GoogleSheetsError
from utils.data_processing import expand_dataframe, validate_dataframe
from utils.arcgis_client import (
    ArcGISClient,
    ArcGISError,
    df_to_features,
    upload_features_batch
)

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Load data from Google Sheets and upload to ArcGIS Feature Layer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --url "https://docs.google.com/spreadsheets/d/SHEET_ID/edit?gid=0"
  python main.py --url "URL" --batch-size 1000 --log-level DEBUG
  python main.py --url "URL" --log-file logs/run.log
        """
    )

    parser.add_argument("--url", type=str, help="Google Sheets URL to load data from")
    parser.add_argument("--item-id", type=str, default=config.ARCGIS_ITEM_ID, help=f"ArcGIS item ID (default: {config.ARCGIS_ITEM_ID})")
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE, help=f"Number of features per batch (default: {config.BATCH_SIZE})")
    parser.add_argument("--log-level", type=str, default=config.LOG_LEVEL, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help=f"Logging level (default: {config.LOG_LEVEL})")
    parser.add_argument("--log-file", type=Path, help="Path to log file (optional)")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress bars")
    parser.add_argument("--show-fields", action="store_true", help="Show ArcGIS layer fields and exit")
    parser.add_argument("--dry-run", action="store_true", help="Process data but don't upload to ArcGIS")

    return parser.parse_args()


def get_google_sheet_url(url_arg: str = None) -> str:
    """Get Google Sheets URL from argument or user input."""
    if url_arg:
        return url_arg

    print("\n" + "=" * 80)
    print("GOOGLE SHEETS URL INPUT")
    print("=" * 80)
    print("Enter the Google Sheets URL in the following format:")
    print("https://docs.google.com/spreadsheets/d/SHEET_ID/edit?gid=0")
    print("=" * 80 + "\n")

    url = input("Google Sheets URL: ").strip()

    if not url:
        logger.error("No URL provided")
        sys.exit(1)

    return url


def main() -> int:
    """Main application entry point."""
    args = parse_arguments()

    log_file = args.log_file or config.LOGS_DIR / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"
    setup_logging(
        log_level=args.log_level,
        log_file=log_file,
        log_format=config.LOG_FORMAT,
        date_format=config.LOG_DATE_FORMAT
    )

    logger.info("=" * 80)
    logger.info("M1MT GIS DEVELOPER TEST TASK - STARTED")
    logger.info("=" * 80)

    try:
        logger.info("Step 1/5: Initializing ArcGIS client")
        client = ArcGISClient()

        logger.info("Step 2/5: Retrieving feature layer")
        layer = client.get_feature_layer(args.item_id)

        if args.show_fields:
            client.print_layer_fields(layer)
            return 0

        logger.info("Step 3/5: Loading data from Google Sheets")
        url = get_google_sheet_url(args.url)
        sheet_id, gid = parse_google_sheet_url(url)

        df = load_google_sheet(sheet_id, gid, config.VALUE_COLUMNS)
        logger.info(f"Loaded {len(df)} rows from Google Sheets")

        required_columns = ["Дата", "Область", "Місто", "long", "lat"] + config.VALUE_COLUMNS
        validate_dataframe(df, required_columns)

        logger.info("Step 4/5: Expanding data using 'unit ladder' rule")
        df_expanded = expand_dataframe(
            df,
            value_columns=config.VALUE_COLUMNS,
            show_progress=not args.no_progress
        )

        if len(df_expanded) == 0:
            logger.warning("No data to upload after expansion (all values are zero)")
            return 0

        logger.info("Step 5/5: Converting to features and uploading to ArcGIS")

        if args.dry_run:
            logger.info("Dry run mode: skipping upload to ArcGIS")
            features = df_to_features(df_expanded)
            logger.info(f"Would upload {len(features)} features")
        else:
            features = df_to_features(df_expanded)

            stats = upload_features_batch(
                layer=layer,
                features=features,
                batch_size=args.batch_size,
                show_progress=not args.no_progress
            )

            print("\n" + "=" * 80)
            print("UPLOAD SUMMARY")
            print("=" * 80)
            print(f"Total features:     {stats['total']}")
            print(f"Successfully added: {stats['success']}")
            print(f"Failed:             {stats['failed']}")
            print(f"Success rate:       {stats['success'] / stats['total'] * 100:.1f}%")
            print("=" * 80 + "\n")

            if stats['failed'] > 0:
                logger.warning(f"{stats['failed']} features failed to upload. Check logs for details.")

        logger.info("=" * 80)
        logger.info("M1MT GIS DEVELOPER TEST TASK - COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return 0

    except GoogleSheetsError as e:
        logger.error(f"Google Sheets error: {e}")
        return 1

    except ArcGISError as e:
        logger.error(f"ArcGIS error: {e}")
        return 2

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return 3

    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 130

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 4


if __name__ == "__main__":
    sys.exit(main())
