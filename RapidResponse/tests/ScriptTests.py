import unittest

from RapidResponse.Environment import Environment
from RapidResponse.Resource import Script
from samples import sample_configuration, local_sample_bootstrap


class BasicTestCase(unittest.TestCase):
    def test_basic(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2","userGroup": "Sales"}

        Ignite_Create_Scenario = Script(env,'Ignite_Create_Scenario',scope='Public',parameters=param )
        Ignite_Create_Scenario.execute()

        # print(Ignite_Create_Scenario.status)

    def test_multi_execution(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great9","userGroup": "Sales"}

        Ignite_Create_Scenario = Script(env,'Ignite_Create_Scenario',scope='Public',parameters=param )
        Ignite_Create_Scenario.execute()
        Ignite_Create_Scenario.execute()
        #print(Ignite_Create_Scenario.status)

class StatusScriptTest(unittest.TestCase):

    def test_view_status_success(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2","userGroup": "Sales"}

        Ignite_Create_Scenario = Script(env,'Ignite_Create_Scenario',scope='Public',parameters=param )
        Ignite_Create_Scenario.execute()
        Ignite_Create_Scenario.close()
        #print(Ignite_Create_Scenario.status)

    def test_view_status_error(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2","userGroup": "Sales"}

        Ignite_Create_Scenario = Script(env,'Ignite_Create_Scenario',scope='Public',parameters=param )
        Ignite_Create_Scenario.execute()
        Ignite_Create_Scenario.close()
        #print(Ignite_Create_Scenario.status)

    def test_view_status_not_run(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2", "userGroup": "Sales"}

        Ignite_Create_Scenario = Script(env, 'Ignite_Create_Scenario', scope='Public', parameters=param)
        #Ignite_Create_Scenario.execute()
        #print(Ignite_Create_Scenario.status)

class ParamsScriptTest(unittest.TestCase):
    def test_params_add(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2", "userGroup": "Sales"}
        Ignite_Create_Scenario = Script(env, 'Ignite_Create_Scenario', scope='Public', parameters=param)
        Ignite_Create_Scenario.parameters.update({'name':'value'})
        self.assertEqual(Ignite_Create_Scenario.parameters.get("name"), 'value')

    def test_params_remove(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2", "userGroup": "Sales"}
        Ignite_Create_Scenario = Script(env, 'Ignite_Create_Scenario', scope='Public', parameters=param)
        del Ignite_Create_Scenario.parameters['newScenario']
        self.assertNotIn('newScenario', Ignite_Create_Scenario.parameters)

    def test_params_update(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2", "userGroup": "Sales"}
        Ignite_Create_Scenario = Script(env, 'Ignite_Create_Scenario', scope='Public', parameters=param)
        Ignite_Create_Scenario.parameters.update({'newScenario': 'Good2GreatZZZ'})
        self.assertEqual(Ignite_Create_Scenario.parameters.get("newScenario"), 'Good2GreatZZZ')

    def test_fetch_result_variables(self):
        env = Environment(local_sample_bootstrap)
        param = {"SharedWorkbookName": "S&OP Finance Operating Plan", "IsIncludeHiddenWorksheet": False,
                 "loggingLevel": "2"}
        GPGetWorkbookVariables = Script(env, 'GP.GetWorkbook.Variables', scope='Public', parameters=param)
        GPGetWorkbookVariables.execute()
        # print(GPGetWorkbookVariables)
        # print(GPGetWorkbookVariables.console)
        # print(GPGetWorkbookVariables.value)
        # Ignite_Create_Scenario.parameters.update({'newScenario': 'Good2GreatZZZ'})
        self.assertIsNotNone(GPGetWorkbookVariables.value)

    def test_fetch_results_worksheets(self):
        env = Environment(local_sample_bootstrap)
        param = {"SharedWorkbookName": "GP Data Validation", "IsIncludeHiddenWorksheet": False, "loggingLevel": "2"}
        GPGetWorkbookVariables = Script(env, 'GP.GetWorkbook.Worksheets', scope='Public', parameters=param)
        GPGetWorkbookVariables.execute()
        # print(GPGetWorkbookVariables)
        # print(GPGetWorkbookVariables.console)
        # print(GPGetWorkbookVariables.value)
        # Ignite_Create_Scenario.parameters.update({'newScenario': 'Good2GreatZZZ'})
        self.assertEqual(
            '"Summary By Site", "Summary By Part Type", "Allocation", "BillOfMaterial", "BOMAlternate", "Batch", "Calendar", "CalendarDate", "Constraint", "Constraint Available", "CurrencyConversionActuals", "CurrencyConversionForecast", "Customer", "DemandOrder", "ForecastDetail", "Historical Demand Actual", "Historical Supply Actual", "IndependentDemand", "OnHand", "Part", "Part Source", "PartSolution", "Part UOM Conversion", "ScheduledReceipt", "Site", "Source", "SourceConstraint", "SupplyOrder", "Supplier", "PartCustomer", "ReferencePart", "Region", "RegionGroup", "Part Validation", "Part Validation - Details", "PartSource Validation", "PartSource Validation - Details", "Source Validation", "Bill Of Material Validation", "Calendar Validation", "CCF Validation", "CCA Validation", "UnitOfMeasure Validation", "IndependentDemand Validation", "ScheduledReceipt Validation", "OnHand Validation", "Constraints", "ConstraintsMDM", "ConstraintAvailable", "Part Sources"',
            GPGetWorkbookVariables.value)


# resource not available
# invalid initialisation params (Public/Priv/Sausage)
# execution fails
if __name__ == '__main__':
    unittest.main()
