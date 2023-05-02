import unittest


import RapidResponse.Table as Table
import RapidResponse.DataModel as DM
from RapidResponse.DataTable import DataTable, DataRow
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Err import DataError


class TableTestCase(unittest.TestCase):

    def test_table_repr(self):
        part = Table.Table('Part', 'Mfg', 'input', 'Y')
        # part_str = part.__str__()
        # print(part)
        self.assertEqual("Table(name='Mfg::Part', fields=[], type='input', keyed='Y', identification fields=None)",
                         part.__str__())

    def test_add_col(self):
        part = Table.Table('Part', 'Mfg', 'input', 'Y')
        col1 = Table.Column('Column1', 'string', 'N')
        col2 = Table.Column('Column2', 'string', 'N')
        part.add_fields(col1, col2)
        # print(part)
        self.assertEqual(
            "Table(name='Mfg::Part', fields=[Column(name='Column1', datatype='string', key='N', referencedTable=None, referencedTableNamespace=None, correspondingField=None, correspondingFieldNamespace=None), Column(name='Column2', datatype='string', key='N', referencedTable=None, referencedTableNamespace=None, correspondingField=None, correspondingFieldNamespace=None)], type='input', keyed='Y', identification fields=None)",
            part.__str__())

    def test_remove_col(self):
        part = Table.Table('Part', 'Mfg', 'input', 'Y')
        col1 = Table.Column('Column1', 'string', 'N')
        col2 = Table.Column('Column2', 'string', 'N')
        part.add_fields(col1, col2)
        part.remove_fields(col1)
        # print(part)

    def test_table_equality(self):
        part = Table.Table('Part', 'Mfg', 'input', 'Y')
        part2 = Table.Table('Part', 'Mfg', 'input', 'Y')
        self.assertEqual(part, part2)


if __name__ == '__main__':
    unittest.main()
