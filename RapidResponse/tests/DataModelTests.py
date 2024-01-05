import unittest


import RapidResponse.Table as Table
import RapidResponse.DataModel as DM
from RapidResponse.DataTable import DataTable, DataRow
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Err import DataError


class DataModel_init_TestCase(unittest.TestCase):

    def test_local_dm(self):
        data_model = DM.DataModel('C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        data_model._load_table_data_from_file(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel\\Tables.tab')
        col1 = Table.Column('Column1', 'string', 'N')
        col2 = Table.Column('Column2', 'string', 'N')
        for i in data_model.tables:
            #        i.add_fields(col1,col2)
            self.assertEqual(type(i), type(Table.Table('Part', 'Mfg')))

    def test_workbook_dm(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl', 'Content-Type': 'application/json'})
        tab = dm.get_table('Part', 'Mfg')
        tab1 = Table.Table(name='Part', namespace='Mfg')
        self.assertEqual(tab, tab1)

    def test_default_dm(self):
        dm = DM.DataModel()
        tab = dm.get_table('Part', 'Mfg')
        tab1 = Table.Table(name='Part', namespace='Mfg')
        self.assertEqual(tab, tab1)

    def test_default_column_assignment(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')

    def test_fully_qual_fieldname(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        valid = dm._validate_fully_qualified_field_name('mfg::part', 'ReferencePart.ProductHierarchy1.Value')
        self.assertTrue(valid)

    def test_neg_fully_qual_fieldname(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        valid = dm._validate_fully_qualified_field_name('mfg::part', 'ReferencePart.ProductHierarchy1.Fake')
        self.assertFalse(valid)

    def test_is_valid_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        valid = dm._is_valid_field('Part', 'ReferencePart')
        self.assertTrue(valid)

    def test_neg_is_valid_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        valid = dm._is_valid_field('Part', 'ReferenceParty')
        self.assertFalse(valid)

    def test_get_ref_tab(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        tab = dm._get_referenced_table('PartSource', 'TransferPart')
        self.assertEqual(tab, 'Part')

    def test_val_error_get_ref_tab(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        with self.assertRaises(ValueError):
            tab = dm._get_referenced_table('PartSource', 'TransferPart.ReferencePart')


class DataModelWBKTestCase(unittest.TestCase):

    def test_get_table_from_data_model(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        tab = data_model.get_table('Part', 'Mfg')
        tab1 = Table.Table(name='Part', namespace='Mfg')
        self.assertEqual(tab, tab1)

if __name__ == '__main__':
    unittest.main()
