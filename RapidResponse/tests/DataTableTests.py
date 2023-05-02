import unittest


import RapidResponse.Table as Table
import RapidResponse.DataModel as DM
from RapidResponse.DataTable import DataTable, DataRow
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Err import DataError



class DataTableTestCase(unittest.TestCase):

    # test various initialisations
    def test_data_table_no_params(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part')

        # test
        self.assertEqual(part._sync, True)
        self.assertEqual(part._table_type, 'Input')
        self.assertEqual(part._key_fields, ['Name', 'Site'])
        self.assertNotEqual(len(part), 0)

    def test_data_table_with_scenario(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part', scenario={"Name": "Integration", "Scope": "Public"})

        # test
        self.assertEqual(part.scenario, {"Name": "Integration", "Scope": "Public"})

    def test_data_table_without_scenario(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part')

        # test
        self.assertEqual(part.scenario, {"Name": "Enterprise Data", "Scope": "Public"})

    def test_data_table_no_refresh(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part', refresh=False)

        # test
        self.assertEqual(len(part), 0)

    # test extend
    def test_data_table_extend(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})

        # execute
        rows = [['GP', '0', '7000vE', '2017-08-31', '1500'],['GP', '1', '7000vE', '2017-08-31', '1500']]
        IndependentDemand.extend(rows)

        self.assertIn(['GP', '1', '7000vE', '2017-08-31', '1500'], IndependentDemand)
        IndependentDemand.del_row(['GP', '0', '7000vE', '2017-08-31', '1500'])
        IndependentDemand.del_row(['GP', '1', '7000vE', '2017-08-31', '1500'])

    # test append
    def test_data_table_append(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})

        # execute
        rows = ['GP', '1', '7000vE', '2017-08-31', '1500']
        IndependentDemand.append(rows)

        self.assertIn(['GP', '1', '7000vE', '2017-08-31', '1500'], IndependentDemand)
        IndependentDemand.del_row(['GP', '1', '7000vE', '2017-08-31', '1500'])

    # test del
    def test_data_table_delete(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})
        rows = [['GP', '0', '7000vE', '2017-08-31', '1500'], ['GP', '1', '7000vE', '2017-08-31', '1500']]
        IndependentDemand.extend(rows)

        # execute
        index = IndependentDemand.indexof(['GP', '1', '7000vE', '2017-08-31', '1500'])
        del IndependentDemand[index]
        self.assertNotIn(['GP', '1', '7000vE', '2017-08-31', '1500'], IndependentDemand)
        index = IndependentDemand.indexof(['GP', '0', '7000vE', '2017-08-31', '1500'])
        del IndependentDemand[index]
        self.assertNotIn(['GP', '0', '7000vE', '2017-08-31', '1500'], IndependentDemand)

    # test del_row
        # setup
        env = Environment(sample_configuration)
        cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})
        rows = [['GP', '0', '7000vE', '2017-08-31', '1500'], ['GP', '1', '7000vE', '2017-08-31', '1500']]
        IndependentDemand.extend(rows)

        # execute
        self.assertIn(['GP', '1', '7000vE', '2017-08-31', '1500'], IndependentDemand)
        IndependentDemand.del_row(['GP', '0', '7000vE', '2017-08-31', '1500'])
        IndependentDemand.del_row(['GP', '1', '7000vE', '2017-08-31', '1500'])

    # test update of attribute of individual record

    # test slicing

    # test bool

    # test indexof

    # test contains


class DataRowTestCase(unittest.TestCase):
    def test_row_init(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, refresh=False)
        # execute
        rec = DataRow(['GP', '0', '7000vE', '2017-08-31', '1500'], IndependentDemand)
        print(rec)

    def test_row_length_mismatch(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, refresh=False)
        rows = [['GP', '0', '7000vE', '2017-08-31', '1500'], ['GP', '1', '7000vE', '2017-08-31', '1500']]

        # execute
        with self.assertRaises(DataError):
            dr = DataRow(['GP', '0', '7000vE', '2017-08-31'], IndependentDemand)



if __name__ == '__main__':
    unittest.main()
