#Utils.py
from typing import Literal

SCOPE_PUBLIC = 'Public'
SCOPE_PRIVATE = 'Private'
VALID_SCOPES = {SCOPE_PUBLIC, SCOPE_PRIVATE}

TABLE_TYPE_INPUT = 'Input'
TABLE_TYPE_CALC = 'Calculated'
VALID_TABLE_TYPES = {TABLE_TYPE_INPUT, TABLE_TYPE_CALC}
TABLE_TYPE = Literal['Input', 'Calculated']

WORKBOOK_URL = "/integration/V1/data/workbook"
WORKSHEET_URL = "/integration/V1/data/worksheet"

BULK_URL = "/integration/V1/bulk"

SCRIPT_URL = "/integration/V1/script"

ENTERPRISE_DATA_SCENARIO = {"Name": "Enterprise Data", "Scope": SCOPE_PUBLIC}
ALL_SITES = 'All Sites'
ALL_PARTS = dict({"Name": "All Parts", "Scope": SCOPE_PUBLIC})
