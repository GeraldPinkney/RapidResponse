import unittest
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Script import Script
import random

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

class BasicScriptTest(unittest.TestCase):
    def test_basic(self):
        env = Environment(sample_configuration)
        param = {"newScenario": "Good2Great2","userGroup": "Sales"}

        Ignite_Create_Scenario = Script(env,'Ignite_Create_Scenario',scope='Public',parameters=param )
        Ignite_Create_Scenario.execute()


# resource not available
# invalid initialisation params (Public/Priv/Sausage)
# execution fails
if __name__ == '__main__':
    unittest.main()
