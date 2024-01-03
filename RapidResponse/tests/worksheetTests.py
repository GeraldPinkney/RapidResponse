import unittest

from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Worksheet import Worksheet, Workbook, WorksheetRow


# class MyTestCase(unittest.TestCase):
#    def test_something(self):
#        self.assertEqual(True, False)  # add assertion here


class WorksheetTestCase(unittest.TestCase):


    # env = Environment(sample_configuration)
    def test_worksheet_init(self):
        variable_values = {
            "DataModel_IsHidden": "No",
            "DataModel_IsReadOnly": "All",
            "DataModel_IsIncludeDataTypeSet": "N",
            "FilterType": "All"
        }

        ws = Worksheet(environment=Environment(sample_configuration), scenario=None, worksheet="DataModel_Summary",
                       workbook={'Name': 'KXSHelperREST', "Scope": 'Public'}, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues=variable_values)

        ws._initialise_for_extract()
        self.assertEqual(ws.name, 'DataModel_Summary')
        self.assertIsNotNone(ws._queryID,"QueryID not set correctly")
        self.assertIsNotNone(ws.total_row_count, "total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")

    def test_worksheet_retrieve(self):
        variable_values = {
            "DataModel_IsHidden": "No",
            "DataModel_IsReadOnly": "All",
            "DataModel_IsIncludeDataTypeSet": "N",
            "FilterType": "All"
        }

        ws = Worksheet(environment=Environment(sample_configuration), scenario=None, worksheet="DataModel_Summary",
                       workbook={'Name': 'KXSHelperREST', "Scope": 'Public'}, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues=variable_values)

        ws._initialise_for_extract()
        ws._retrieve_worksheet_data()
        print(ws.rows)

    def test_ws_simple(self):
        ws = Worksheet(environment=Environment(sample_configuration), scenario=None, worksheet="OnHand",
                       workbook={'Name': '.Input Tables', "Scope": 'Public'}, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"})
        self.assertIsNotNone(ws._queryID, "QueryID not set correctly")
        self.assertIsNotNone(ws.total_row_count, "total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")

# todo test private resource, test diff parameters provided, test multiple worksheets

if __name__ == '__main__':
    unittest.main()
