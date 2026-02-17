import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

ARCGIS_ITEM_ID = os.getenv("item_id", "2250ee027e04401dae8c72e09159af25")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))
VALUE_COLUMNS = [f"Значення {i}" for i in range(1, 11)]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
