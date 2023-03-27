import unittest

import RapidResponse.RapidResponse.Table
import RapidResponse.RapidResponse.DataModel as DM
from RapidResponse.RapidResponse.Environment import Environment, sample_configuration
from RapidResponse.RapidResponse.Err import DataError
from RapidResponse.RapidResponse.Worksheet import Workbook, Worksheet


# class MyTestCase(unittest.TestCase):
#    def test_something(self):
#        self.assertEqual(True, False)  # add assertion here


class WorksheetTestCase(unittest.TestCase):
    """

        :param Environment:
        :param Scenario:
        :param Workbook: {"Name": 'workbookname', "Scope": 'Public'}
        :param SiteGroup: "All Sites"
        :param Filter: {"Name": "All Parts","Scope": "Public"}
        :param VariableValues:
        :param WorksheetNames: ["worksheet name1", "worksheet name2"]
    """

    # env = Environment(sample_configuration)
    def test_worksheet_init(self):
        variable_values = {
            "DataModel_IsHidden": "No",
            "DataModel_IsReadOnly": "All",
            "DataModel_IsIncludeDataTypeSet": "N",
            "FilterType": "All"
        }

        ws = Worksheet(environment=Environment(sample_configuration),
                       workbook={'Name': 'KXSHelperREST', "Scope": 'Public'},
                       SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"},
                       VariableValues=variable_values,
                       worksheet="DataModel_Summary"
                       )

        ws.initialise_for_extract()
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

        ws = Worksheet(environment=Environment(sample_configuration),
                       workbook={'Name': 'KXSHelperREST', "Scope": 'Public'},
                       SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"},
                       VariableValues=variable_values,
                       worksheet="DataModel_Summary"
                       )

        ws.initialise_for_extract()
        ws.retrieve_worksheet_data()
        print(ws.rows)


if __name__ == '__main__':
    unittest.main()
