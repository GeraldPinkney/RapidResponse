import unittest

import RapidResponse.RapidResponse.Table
import RapidResponse.RapidResponse.Table as Table
import RapidResponse.RapidResponse.DataModel as DM


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
            print(i)

    def test_get_table_from_data_model(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel')
        tab = data_model.get_table('Part', 'Mfg')
        tab1 = Table.Table(name='Part', namespace='Mfg')
        self.assertEqual(tab, tab1)


class DataTableTestCase(unittest.TestCase):
    pass


class EnvironmentTestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
