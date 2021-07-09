import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

CSV_FILE_PATH = DATA_DIR / "FCDO_Geographical_Names_Index-2021-3-31.csv"

COUNTRY_CODE_MAP = {}
with open(CSV_FILE_PATH) as csv_file:
    reader = csv.reader(csv_file)
    for code, name, _, _ in reader:
        COUNTRY_CODE_MAP[code] = name


def get_country_name_from_code(code):
    return COUNTRY_CODE_MAP[code]
