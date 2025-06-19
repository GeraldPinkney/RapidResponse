import unittest


import RapidResponse.Table as Table
import RapidResponse.DataModel as DM
from RapidResponse.DataTable import DataTable, DataRow
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Err import DataError


class DataModel_init_TestCase(unittest.TestCase):

    def test_local_dm_tab(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        data_model._load_table_data_from_file(
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel\\Tables.tab')
        for i in data_model.tables:
            self.assertEqual(type(i), type(Table.Table('Part', 'Mfg')))

    def test_local_dm_tab_contains(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        data_model._load_table_data_from_file(
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel\\Tables.tab')
        self.assertIn(Table.Table('Part', 'Mfg'), data_model.tables, 'screwed')

    def test_local_dm_field(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        data_model._load_field_data_from_file(
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel\\Fields.tab')
        test_field = {'Table': 'BillOfMaterial', 'Namespace': 'Mfg', '': '', 'Field': 'Scrap', 'FieldNameSpace': 'Mfg',
                      'Key': 'N',
                      'Type': 'Quantity', 'Calculated': 'Input', 'Default Value': '1', 'referencedTable': '',
                      'Related Namespace': '', 'Corresponding Field': '', 'Corresponding Namespace': '',
                      'Record Deleted': 'Delete record', 'Record Table': 'Y', 'Record Field': 'Y', 'license': None}
        self.assertIn(test_field, data_model._fields, 'screwed')

    def test_from_pkg_rsc(self):
        data_model = DM.DataModel()
        self.assertIn(Table.Table('Part', 'Mfg'), data_model.tables, 'screwed')

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
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')

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
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        tab = data_model.get_table('Part', 'Mfg')
        tab1 = Table.Table(name='Part', namespace='Mfg')
        self.assertEqual(tab, tab1)

if __name__ == '__main__':
    unittest.main()
