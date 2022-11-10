import unittest

import RapidResponse.RapidResponse.Table
import RapidResponse.RapidResponse.Table as Table
import RapidResponse.RapidResponse.DataModel as DM
from RapidResponse.RapidResponse.DataTable import DataTable
from RapidResponse.RapidResponse.Environment import Environment
from RapidResponse.RapidResponse.Environment import sample_configuration

class TableTestCase(unittest.TestCase):

    def test_table_repr(self):
        part = Table.Table('Part', 'Mfg', 'input', 'Y')
        # part_str = part.__str__()
        # print(part)
        self.assertEqual("Table(name='Mfg::Part', fields=[], type='input', keyed='Y', identification fields=None)",
                         part.__str__())

    def test_add_col(self):
        part = Table.Table('Part', 'Mfg', 'input', 'Y')
        col1 = RapidResponse.RapidResponse.Table.Column('Column1', 'string', 'N')
        col2 = RapidResponse.RapidResponse.Table.Column('Column2', 'string', 'N')
        part.add_fields(col1, col2)
        # print(part)
        self.assertEqual(
            "Table(name='Mfg::Part', fields=[Column(name='Column1', datatype='string', key='N'), Column(name='Column2', datatype='string', key='N')], type='input', keyed='Y', identification fields=None)",
            part.__str__())

    def test_remove_col(self):
        part = Table.Table('Part', 'Mfg', 'input', 'Y')
        col1 = RapidResponse.RapidResponse.Table.Column('Column1', 'string', 'N')
        col2 = RapidResponse.RapidResponse.Table.Column('Column2', 'string', 'N')
        part.add_fields(col1, col2)
        part.remove_fields(col1)
        # print(part)

    def test_table_equality(self):
        part = Table.Table('Part', 'Mfg', 'input', 'Y')
        part2 = Table.Table('Part', 'Mfg', 'input', 'Y')
        self.assertEqual(part, part2)


class DataModelTestCase(unittest.TestCase):

    def test_table_data_model(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel')
        data_model.load_table_data_from_file(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel\\Tables.tab')
        col1 = RapidResponse.RapidResponse.Table.Column('Column1', 'string', 'N')
        col2 = RapidResponse.RapidResponse.Table.Column('Column2', 'string', 'N')
        for i in data_model._tables:
            #        i.add_fields(col1,col2)
            self.assertEqual(type(i), type(Table.Table('Part', 'Mfg')))

    def test_get_table_from_data_model(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel')
        tab = data_model.get_table('Part', 'Mfg')
        tab1 = Table.Table(name='Part', namespace='Mfg')
        self.assertEqual(tab, tab1)


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

    def test_data_table_no_refresh(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part', refresh=False)

        # test
        self.assertEquals(len(part), 0)

    # test append
    def test_data_table_append(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols)

        # execute
        rows = [['GP', '0', '7000vE', '2017-08-31', '1500'],['GP', '1', '7000vE', '2017-08-31', '1500']]
        IndependentDemand.extend(rows)

        self.assertIn(['GP', '1', '7000vE', '2017-08-31', '1500'], IndependentDemand)
        IndependentDemand.del_row(['GP', '0', '7000vE', '2017-08-31', '1500'])
        IndependentDemand.del_row(['GP', '1', '7000vE', '2017-08-31', '1500'])
    # test extend

    # test del

    # test del_row

    # test update of attribute of individual record

    # test slicing

    # test bool

    # test indexof

    # test contains



class EnvironmentTestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
