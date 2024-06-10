import unittest
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Script import Script
import random

class BasicTestCase(unittest.TestCase):
    def test_basic(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2","userGroup": "Sales"}

        Ignite_Create_Scenario = Script(env,'Ignite_Create_Scenario',scope='Public',parameters=param )
        Ignite_Create_Scenario.execute()

        print(Ignite_Create_Scenario.status)

    def test_multi_execution(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great9","userGroup": "Sales"}

        Ignite_Create_Scenario = Script(env,'Ignite_Create_Scenario',scope='Public',parameters=param )
        Ignite_Create_Scenario.execute()
        Ignite_Create_Scenario.execute()
        print(Ignite_Create_Scenario.status)

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


# resource not available
# invalid initialisation params (Public/Priv/Sausage)
# execution fails
if __name__ == '__main__':
    unittest.main()
