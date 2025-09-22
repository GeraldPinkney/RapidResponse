import unittest

import RapidResponse.DataModel


class TableTestCase(unittest.TestCase):

    def test_table_repr(self):
        part = RapidResponse.DataModel.Table('Part', 'Mfg', 'input', 'Y')
        # part_str = part.__str__()
        # print(part)
        self.assertEqual("Table(name='Mfg::Part', fields=[], type='input', keyed='Y', identification fields=None)",
                         part.__str__())

    def test_add_cols(self):
        part = RapidResponse.DataModel.Table('Part', 'Mfg', 'input', 'Y')
        col1 = RapidResponse.DataModel.Column('Column1', 'string', 'N')
        col2 = RapidResponse.DataModel.Column('Column2', 'string', 'N')
        part.add_fields([col1, col2])
        # print(part)
        self.assertEqual(
            "Table(name='Mfg::Part', fields=[Column(name='Column1', datatype='string', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None, fieldNamespace=None), Column(name='Column2', datatype='string', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None, fieldNamespace=None)], type='input', keyed='Y', identification fields=None)",
            part.__str__())

    def test_add_col(self):
        part = RapidResponse.DataModel.Table('Part', 'Mfg', 'input', 'Y')
        col1 = RapidResponse.DataModel.Column('Column1', 'string', 'N')
        col2 = RapidResponse.DataModel.Column('Column2', 'string', 'N')
        part._add_field(col1)
        # print(part)
        self.assertEqual(
            "Table(name='Mfg::Part', fields=[Column(name='Column1', datatype='string', key='N', referencedTable=None, referencedTableNamespace=None, identification_fields=None, correspondingField=None, correspondingFieldNamespace=None, fieldNamespace=None)], type='input', keyed='Y', identification fields=None)",
            part.__str__())

    def test_remove_col(self):
        part = RapidResponse.DataModel.Table('Part', 'Mfg', 'input', 'Y')
        col1 = RapidResponse.DataModel.Column('Column1', 'string', 'N')
        col2 = RapidResponse.DataModel.Column('Column2', 'string', 'N')
        part.add_fields([col1, col2])
        part.remove_fields(col1)
        # print(part)

    def test_table_equality(self):
        part = RapidResponse.DataModel.Table('Part', 'Mfg', 'input', 'Y')
        part2 = RapidResponse.DataModel.Table('Part', 'Mfg', 'input', 'Y')
        self.assertEqual(part, part2)

    def test_get_field(self):
        part = RapidResponse.DataModel.Table('Part', 'Mfg', 'input', 'Y')
        col1 = RapidResponse.DataModel.Column('Column1', 'string', 'N')
        col2 = RapidResponse.DataModel.Column('Column2', 'string', 'N')
        part.add_fields([col1, col2])
        self.assertEqual(part.get_field('Column1'), RapidResponse.DataModel.Column('Column1', 'string', 'N'))


if __name__ == '__main__':
    unittest.main()
