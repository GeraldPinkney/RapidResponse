import unittest

from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Worksheet import Worksheet, Workbook, WorksheetRow, Cell


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
        self.assertIsNotNone(ws.total_row_count, "_total_row_count not set correctly")
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

    def test_worksheet_retrieve_with_amp(self):
        variable_values = {
            "DemandShipment": "Actual",
            "SupplyShipment": "All",
            "DemandForecast": "All",
            "SupplyForecast": "All",
            "InventoryPlan": "All"
        }
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Supply and Demand (Units)",
                       workbook={'Name': 'S&OP Plan Review', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues=variable_values)
        self.assertNotEqual(len(ws.rows), 0, 'fail')

    def test_ws_simple(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="OnHand",
                       workbook={'Name': '.Input Tables', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"})
        #self.assertIsNotNone(ws._queryID, "QueryID not set correctly")
        self.assertIsNotNone(ws.total_row_count, "_total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")

    def test_ws_refresh_False(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="OnHand",
                       workbook={'Name': '.Input Tables', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, refresh=False)
        self.assertEqual(len(ws), 0)

    def test_ws_append(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
                       workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
                       scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
        #self.assertIsNotNone(ws._queryID, "QueryID not set correctly")
        self.assertIsNotNone(ws.total_row_count, "_total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")
        rec = ['102-CDMAc', '1234', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual',
               'DC-NorthAmerica']
        ws.append(rec)

    def test_ws_extend(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
        workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
        scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
        Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})

        self.assertIsNotNone(ws.total_row_count, "_total_row_count not set correctly")
        self.assertNotEqual(len(ws.columns), 0, "cols not set")
        recs = [['102-CDMAc', '1234', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual',
               'DC-NorthAmerica'],['102-CDMAc', '12345', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual',
               'DC-NorthAmerica']]
        ws.extend(recs)

    def test_ws_slice(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
                       workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
                       scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
        #self.assertIsNotNone(ws._queryID, "QueryID not set correctly")
        self.assertIsNotNone(ws[0:10], "slice count not zero")
# todo test private resource, test diff parameters provided, test multiple worksheets
# chagne value in place
# self.rows[0][0] = xx
    def test_ws_setitem(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
                       workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
                       scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
        rec = ws[0]
        rec[5] = '07-06-20'

    def test_ws_change(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="OnHand",
                       workbook={'Name': '.Input Tables', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"})
        #self.assertIsNotNone(ws._queryID, "QueryID not set correctly")

    def test_ws_simple_bool(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="OnHand",
                       workbook={'Name': '.Input Tables', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"})
        #self.assertIsNotNone(ws._queryID, "QueryID not set correctly")
        self.assertTrue(ws)

    def test_ws_simple_bool_f(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="OnHand",
                       workbook={'Name': '.Input Tables', "Scope": 'Public'}, scenario=None, SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"}, refresh=False)
        #self.assertIsNotNone(ws._queryID, "QueryID not set correctly")
        self.assertFalse(bool(ws))
    # test indexof

    # test contains


class WorksheetRowTestCase(unittest.TestCase):
    def test_wsr_init(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
        workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
        scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
        Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
        wsr = WorksheetRow(['102-CDMAc', '1234', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual','DC-NorthAmerica'], ws)
        self.assertNotEqual(len(wsr), 0)

    def test_wsr_init_get_index(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
        workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
        scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
        Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
        self.assertIsNotNone(ws[0])
        self.assertIsNotNone(ws[0][0])
        self.assertIsNotNone(ws[0][5])
        #self.assertNotEqual(len(wsr), 0)

    def test_wsr_dynamic_attr_access(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
        workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
        scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
        Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
        wsr = WorksheetRow(['102-CDMAc', '1234', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual','DC-NorthAmerica'], ws)
        self.assertEqual(wsr.OrderId, '102-CDMAc')

    def test_wsr_set_item(self):
        ws = Worksheet(environment=Environment(sample_configuration), worksheet="Actual Orders",
        workbook={'Name': 'Orders by Customer', "Scope": 'Public'},
        scenario={"Name": "Integration", "Scope": "Public"}, SiteGroup="All Sites",
        Filter={"Name": "All Parts", "Scope": "Public"}, VariableValues={"customer": "ebikes.com"})
        wsr = WorksheetRow(['102-CDMAc', 'GP1234', 'DC-NorthAmerica', 'FC102', 'CDMA-C333', '01-01-20', '140', 'DCActual','DC-NorthAmerica'], ws)
        wsr[1] = 'GP1234567'

class WorkbookTestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
