import unittest

from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Worksheet import Worksheet, Workbook, WorksheetRow




class WorksheetTestCase(unittest.TestCase):


    # env = Environment(sample_configuration)
    def test_worksheet_init(self):
        variable_values = {
            "DataModel_IsHidden": "No",
            "DataModel_IsReadOnly": "All",
            "DataModel_IsIncludeDataTypeSet": "N",
            "FilterType": "All"
        }

        ws = Worksheet(environment=Environment(sample_configuration), worksheet="DataModel_Summary",
                       workbook={'Name': 'KXSHelperREST', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues=variable_values)

        #ws._create_export()
        self.assertEqual(ws.name, 'DataModel_Summary')
        #self.assertIsNotNone(ws._queryID,"QueryID not set correctly")
        self.assertIsNotNone(ws.total_row_count, "total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")

    def test_worksheet_retrieve(self):
        variable_values = {
            "DataModel_IsHidden": "No",
            "DataModel_IsReadOnly": "All",
            "DataModel_IsIncludeDataTypeSet": "N",
            "FilterType": "All"
        }

        ws = Worksheet(environment=Environment(sample_configuration), worksheet="DataModel_Summary",
                       workbook={'Name': 'KXSHelperREST', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues=variable_values)

        #ws._create_export()
        #ws._get_export_results()
        self.assertNotEqual(len(ws.rows), 0, 'fail')

    def test_ws_simple(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="OnHand",
                       workbook={'Name': '.Input Tables', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"})
        #self.assertIsNotNone(ws._queryID, "QueryID not set correctly")
        self.assertIsNotNone(ws.total_row_count, "total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")

    def test_ws_append(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
                       workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
                       scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
        #self.assertIsNotNone(ws._queryID, "QueryID not set correctly")
        self.assertIsNotNone(ws.total_row_count, "total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")
        rec = ['102-CDMAc', '1234', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual',
               'DC-NorthAmerica']
        ws.append(rec)

    def test_ws_extend(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
                       workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
                       scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})

        self.assertIsNotNone(ws.total_row_count, "total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")
        recs = [['102-CDMAc', '1234', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual',
               'DC-NorthAmerica'],['102-CDMAc', '12345', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual',
               'DC-NorthAmerica']]
        ws.extend(recs)
# todo test private resource, test diff parameters provided, test multiple worksheets
# chagne value in place
# self.rows[0][0] = xx
    # test slicing

    # test bool

    # test indexof

    # test contains

class WorksheetRowTestCase(unittest.TestCase):
    pass


class WorkbookTestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
