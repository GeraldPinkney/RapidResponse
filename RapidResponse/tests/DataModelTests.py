import unittest


import RapidResponse.Table as Table
import RapidResponse.DataModel as DM
from RapidResponse.DataTable import DataTable, DataRow
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Err import DataError


class DataModelTestCase(unittest.TestCase):

    def test_table_data_model(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse')
        data_model.load_table_data_from_file(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel\\Tables.tab')
        col1 = Table.Column('Column1', 'string', 'N')
        col2 = Table.Column('Column2', 'string', 'N')
        for i in data_model.tables:
            #        i.add_fields(col1,col2)
            self.assertEqual(type(i), type(Table.Table('Part', 'Mfg')))

    def test_get_table_from_data_model(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        tab = data_model.get_table('Part', 'Mfg')
        tab1 = Table.Table(name='Part', namespace='Mfg')
        self.assertEqual(tab, tab1)


if __name__ == '__main__':
    unittest.main()
