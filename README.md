# M1MT GIS Developer Test Task

Load data from Google Sheets, transform using "unit ladder" rule, upload to ArcGIS Feature Layer.

## Quick Start

```bash
git clone https://github.com/Baranotik15/Test_for_M1MT.git
cd Test_for_M1MT
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

Create `.env`:
```dotenv
item_id=2250ee027e04401dae8c72e09159af25
```

Run:
```bash
python main.py --url "YOUR_GOOGLE_SHEETS_URL"
```

## Commands

```bash
python main.py --help         # All options
python main.py --show-fields  # Display layer fields
python main.py --dry-run      # Test without upload
pytest -v                     # Run tests
```

## Unit Ladder Rule

Input: `Value 1 = 3, Value 2 = 2` → Output: 3 rows

| Value 1 | Value 2 |
|---------|---------|
| 1       | 1       |
| 1       | 1       |
| 1       | 0       |

## Structure

```
├── main.py       # Entry point
├── config.py     # Configuration
├── utils/        # Core modules
└── tests/        # Tests
```

## Field Mapping

| Google Sheets | ArcGIS |
|---------------|--------|
| Дата | date |
| Область | region |
| Місто | city |
| Значення 1-10 | value_1..10 |
| long, lat | geometry |
