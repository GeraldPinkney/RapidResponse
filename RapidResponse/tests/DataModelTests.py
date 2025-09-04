import unittest

import RapidResponse.DataModel as DM
import RapidResponse.Table as Table


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

    def test_get_field_namespace(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        c = dm._get_table_field('Mfg::Part', 'Name')
        # print(tab.fields)
        self.assertEqual(c.fieldNamespace, 'Mfg')


    def test_get_public_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})

        returned = dm.get_field('Mfg::PartCustomer', 'Part.Site.Value')
        print(returned)
        self.assertEqual(returned,
                         Table.Column(name='Part.Site.Value', datatype='String', key='Y', referencedTable=None,
                                      referencedTableNamespace=None, identification_fields=None,
                                      correspondingField=None, correspondingFieldNamespace=None, fieldNamespace='Mfg'))

    def test_get_nested_table_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        col = dm._get_nested_table_field('Mfg::PartCustomer', 'Part.Name')
        # print(tab.fields)
        self.assertEqual(col.name, 'Part.Name')
        print(col)

    def test_get_more_nested_table_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        col = dm._get_nested_table_field('Mfg::PartCustomer', 'Part.Site.Value')
        # print(tab.fields)
        self.assertEqual(col.name, 'Part.Site.Value')
        print(col)

    def test_get_even_more_nested_table_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        col = dm._get_nested_table_field('Mfg::IndependentDemand', 'Order.Type.ControlSet.Value')
        # print(tab.fields)
        self.assertEqual(col.name, 'Order.Type.ControlSet.Value')
        print(col)

    def test_get_referenced_table(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        tab = dm._get_referenced_table('PartSource', 'TransferPart')
        self.assertEqual(tab, 'Part')

    def test_get_referenced_tableAndNamespace(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        tab = dm._get_referenced_tableAndNamespace('PartSource', 'TransferPart')
        self.assertEqual(tab, 'Mfg::Part')

    def test_get_other_referenced_tableAndNamespace(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        tab = dm._get_referenced_tableAndNamespace('DemandOrder', 'Type')
        self.assertEqual(tab, 'Mfg::DemandType')

    def test_is_reference_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        isRef = dm._is_reference_field('IndependentDemand', 'Order')
        self.assertTrue(isRef)

    def test_is_reference_field_neg(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        isRef = dm._is_reference_field('IndependentDemand', 'Line')
        self.assertFalse(isRef)

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
        valid = dm._validate_fully_qualified_field_name('mfg::Part', 'ReferencePart.ProductHierarchy1.Value')
        self.assertTrue(valid)

    def test_fully_qual_fieldname2(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        valid = dm._validate_fully_qualified_field_name('mfg::IndependentDemand', 'Order.Type.ControlSet.Value')
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

    def test_valid_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        valid = dm.validate_field('SPart', 'ReferencePart.ProductHierarchy1.Value')
        self.assertTrue(valid)

    def test_neg_is_valid_field(self):
        dm = DM.DataModel(None, url='http://localhost/rapidresponse',
                          headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                   'Content-Type': 'application/json'})
        valid = dm._is_valid_field('Part', 'ReferenceParty')
        self.assertFalse(valid)



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

    def test_get_field(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        col = data_model.get_field('Mfg::IndependentDemand', 'Order.Type.ControlSet.Value')
        # print(col)
        self.assertEqual(col, Table.Column(name='Order.Type.ControlSet.Value', datatype='String', key='Y',
                                           referencedTable=None, referencedTableNamespace=None,
                                           identification_fields=None, correspondingField=None,
                                           correspondingFieldNamespace=None, fieldNamespace='Mfg'))

    def test_get_field_not_nested(self):
        data_model = DM.DataModel(
            'C:\\Users\\gpinkney\\OneDrive - Kinaxis\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        col = data_model.get_field('Mfg::IndependentDemand', 'Line')
        # print(col)
        self.assertEqual(col, Table.Column(name='Line', datatype='String', key='Y', referencedTable=None,
                                           referencedTableNamespace=None, identification_fields=None,
                                           correspondingField=None, correspondingFieldNamespace=None,
                                           fieldNamespace='Mfg'))

    def _test_get_field_reference(self):
        data_model = DM.DataModel(None, url='http://localhost/rapidresponse',
                                  headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                           'Content-Type': 'application/json'})
        col = data_model.get_field('Mfg::Customer', 'U_Division')
        # print(col)
        self.assertEqual(col, Table.Column(name='U_Division', datatype='Reference', key='Y', referencedTable=None,
                                           referencedTableNamespace=None, identification_fields=None,
                                           correspondingField=None, correspondingFieldNamespace=None,
                                           fieldNamespace='Mfg'))

    def test_exclude_using_namespace(self):
        data_model = DM.DataModel(None, url='http://localhost/rapidresponse',
                                  headers={'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl',
                                           'Content-Type': 'application/json'}, workbook='KXSHelperREST')
        self.assertIsNotNone(data_model)
        self.assertEqual('System', data_model._excludedNamespacesList[0])
        count = 0
        for f in data_model._fields:
            if f['FieldNameSpace'] == 'System':
                count = count + 1
        self.assertEqual(count, 0)

if __name__ == '__main__':
    unittest.main()
