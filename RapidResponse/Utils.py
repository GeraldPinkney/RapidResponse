#Utils.py


SCOPE_PUBLIC = 'Public'
SCOPE_PRIVATE = 'Private'
VALID_SCOPES = {SCOPE_PUBLIC, SCOPE_PRIVATE}

TABLE_TYPE_INPUT = 'Input'
TABLE_TYPE_CALC = 'Calculated'
VALID_TABLE_TYPES = {TABLE_TYPE_INPUT, TABLE_TYPE_CALC}
TABLE_TYPE = Literal['Input', 'Calculated']

WORKBOOK_URL = "/integration/V1/data/workbook"
BULK_URL = "/integration/V1/bulk"
WORKSHEET_URL = "/integration/V1/data/worksheet"
SCRIPT_URL = "/integration/V1/script"