import json
import unittest
from unittest.mock import patch, AsyncMock
from RapidResponse.DataTable import DataTable, DataRow, Column
from RapidResponse.Environment import Environment
# from samples import sample_configuration, local_sample_bootstrap
from RapidResponse.tests.resources.samples import sample_configuration, local_sample_bootstrap
from RapidResponse.Err import DataError
import time


def print_recs(list_of_stuff):
    print('new page')
    time.sleep(10)
    for i in list_of_stuff:
        print(i)

class DataTableTestCase(unittest.TestCase):

    # test various initialisations
    def test_data_table_no_params_small(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part')

        # test
        self.assertEqual(part._sync, True)
        self.assertEqual(part._table_type, 'Input')
        self.assertEqual(part._key_fields, ['Name', 'Site.Value'])
        self.assertNotEqual(len(part), 0)

    def test_data_table_with_scenario(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part', scenario={"Name": "Integration", "Scope": "Public"})

        # test
        self.assertEqual(part.scenario, {"Name": "Integration", "Scope": "Public"})

    def test_data_table_explode_col_single_key(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env, 'Mfg::Part', scenario={"Name": "Integration", "Scope": "Public"}, refresh=False)
        c = Column(name='Order.Site', datatype='Reference', key='Y', referencedTable='Site',
                   referencedTableNamespace='Core', identification_fields=None, correspondingField=None,
                   correspondingFieldNamespace=None)
        # test
        print(part.explode_reference_field(c))
        self.assertEqual(part.explode_reference_field(c), [
            Column(name='Order.Site.Value', datatype='String', key='Y', referencedTable=None,
                   referencedTableNamespace=None, identification_fields=None, correspondingField=None,
                   correspondingFieldNamespace=None)])

    def test_data_table_explode_col_multi_key(self):
        # setup
        env = Environment(sample_configuration)
        ForecastDetail = DataTable(env, 'Mfg::ForecastDetail', scenario={"Name": "Integration", "Scope": "Public"},
                                   refresh=False)
        c = Column(name='Header', datatype='Reference', key='Y', referencedTable='HistoricalDemandHeader',
                   referencedTableNamespace='Mfg', identification_fields=None, correspondingField=None,
                   correspondingFieldNamespace=None)

        # test
        response = ForecastDetail.explode_reference_field(c)
        print(response)
        self.assertEqual([Column(name='Header.Category.Value', datatype='String', key='Y', referencedTable='',
                                 referencedTableNamespace='', identification_fields=None, correspondingField=None,
                                 correspondingFieldNamespace=None),
                          Column(name='Header.PartCustomer.Customer.Id', datatype='String', key='Y',
                                 referencedTable=None, referencedTableNamespace=None, identification_fields=None,
                                 correspondingField=None, correspondingFieldNamespace=None),
                          Column(name='Header.PartCustomer.Customer.Site.Value', datatype='String', key='Y',
                                 referencedTable='', referencedTableNamespace='', identification_fields=None,
                                 correspondingField=None, correspondingFieldNamespace=None),
                          Column(name='Header.PartCustomer.Part.Name', datatype='String', key='Y', referencedTable=None,
                                 referencedTableNamespace=None, identification_fields=None, correspondingField=None,
                                 correspondingFieldNamespace=None),
                          Column(name='Header.PartCustomer.Part.Site.Value', datatype='String', key='Y',
                                 referencedTable='', referencedTableNamespace='', identification_fields=None,
                                 correspondingField=None, correspondingFieldNamespace=None)], response)

    def test_data_table_explode_col_not_key(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env, 'Mfg::Part', scenario={"Name": "Integration", "Scope": "Public"}, refresh=False)
        c = Column(name='Order.Site', datatype='Reference', key='N', referencedTable='Site',
                   referencedTableNamespace='Core', identification_fields=None, correspondingField=None,
                   correspondingFieldNamespace=None)
        # test
        resp = part.explode_reference_field(c)[0]
        # print(part.explode_reference_field(c))
        self.assertEqual(Column(name='Order.Site.Value', datatype='String', key='Y', referencedTable=None,
                                referencedTableNamespace=None, identification_fields=None, correspondingField=None,
                                correspondingFieldNamespace=None), resp)

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

    def test_data_table_no_refresh_async(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env, 'Mfg::Part', refresh=False)

        # test
        self.assertEqual(len(part), 0)
        part.RefreshData_async()
        self.assertNotEqual(len(part), 0)

    def test_data_table_refresh_async(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env, 'Mfg::Part')

        # test
        self.assertNotEqual(len(part), 0)
        print(part[0:10])

    def test_data_table_refresh_async_bootstrap(self):
        # setup
        env = Environment(local_sample_bootstrap)
        part = DataTable(env, 'Mfg::Part')

        # test
        self.assertNotEqual(len(part), 0)

    def test_data_table_refresh_with_funct(self):
        # setup

        env = Environment(sample_configuration)
        part = DataTable(env, 'Mfg::Part', refresh=False)

        # test
        self.assertEqual(len(part), 0)
        part.RefreshData(data_range=1000, action_on_page=print_recs)
        self.assertNotEqual(len(part), 0)

    def test_data_table_no_refresh_properties(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part', refresh=False)

        # test
        self.assertEqual(len(part), 0)
        part._create_export()
        self.assertNotEqual(part._total_row_count, 0)
        part._session.close()

    def test_diff_col_order(self):
        self.assertTrue(1 == 2, '')
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site', 'Order.Type', 'Line', 'Part.Name', 'Part.Site', 'DueDate',
                'Order.Type.ControlSet.Value', 'Quantity']

    def test_table_with_custom_cols_namespace_attr(self):
        env = Environment(local_sample_bootstrap)
        cols = ['Id', 'TestInt1', 'TestString1', 'U_Division', 'SubRegion', 'Country']
        customer = DataTable(env, 'Mfg::Customer', cols, scenario={"Name": "Integration", "Scope": "Public"},
                             sync=False)
        self.assertTrue(customer.get_field('TestInt1').fieldNamespace == 'User')

    def test_namespaceExpectedNone(self):
        env = Environment(local_sample_bootstrap)
        c = Column(name='U_Division', datatype='Str', key='N')
        cols = ['Id', 'TestInt1', 'TestString1', 'U_Division', 'SubRegion', 'Country.Id']
        customer = DataTable(env, 'Mfg::Customer', cols, scenario={"Name": "Integration", "Scope": "Public"})
        self.assertIsNone(customer.columns[customer.columns.index(c)].fieldNamespace)

    def test_namespaceExpected(self):
        env = Environment(local_sample_bootstrap)
        c = Column(name='U_Division.U_Value', datatype='Str', key='N')
        cols = ['Id', 'TestInt1', 'TestString1', 'U_Division.U_Value', 'SubRegion', 'Country.Id']
        customer = DataTable(env, 'Mfg::Customer', cols, scenario={"Name": "Integration", "Scope": "Public"})
        self.assertEqual(customer.columns[customer.columns.index(c)].fieldNamespace, 'User')

    def test_table_with_custom_cols_namespace_ref2(self):
        env = Environment(local_sample_bootstrap)
        cols = ['Id', 'TestInt1', 'TestString1', 'U_Division', 'SubRegion.Id', 'Country']
        customer = DataTable(env, 'Mfg::Customer', cols, scenario={"Name": "Integration", "Scope": "Public"})
        self.assertTrue(customer.get_field('SubRegion.Id').fieldNamespace == 'Solutions')

    def test_table_with_custom_cols(self):
        env = Environment(local_sample_bootstrap)
        cols = ['Id', 'TestInt1', 'TestString1', 'U_Division', 'SubRegion', 'Country']
        customer = DataTable(env, 'Mfg::Customer', cols, scenario={"Name": "Integration", "Scope": "Public"})

        self.assertIsNotNone(customer)

    def test_table_custom_cols_append(self):
        # setup
        env = Environment(local_sample_bootstrap)
        cols = ['Id', 'TestInt1', 'TestString1', 'U_Division.U_Value', 'SubRegion.Id', 'Country.Id', 'Site.Value']
        customer = DataTable(env, 'Mfg::Customer', cols, scenario={"Name": "Integration", "Scope": "Public"})
        #print(customer)
        rec = ['Berlin', '', '', '', '', '', '030']
        # execute
        customer.append(rec)
        self.assertIn(['Berlin', '', '', '', '', '', '030'], customer)
        # teardown
        customer.del_row(rec)

    def test_table_custom_cols_append_DataError(self):
        # setup
        env = Environment(local_sample_bootstrap)
        cols = ['Id', 'TestInt1', 'TestString1', 'U_Division.U_Value', 'SubRegion.Id', 'Country', 'Site.Value']
        customer = DataTable(env, 'Mfg::Customer', cols, scenario={"Name": "Integration", "Scope": "Public"})
        rec = ['Paris', '', '', '', '', '', '030']

        # execute
        with self.assertRaises(DataError) as err:
            customer.append(rec)
        self.assertNotIn(['Paris', '', '', '', '', '', '030'], customer)

        # teardown


    # test extend
    def test_data_table_extend_with_rows(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site', 'Order.Type.ControlSet.Value', 'Order.Type', 'Line', 'Part.Name', 'Part.Site',
                'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})

        # execute
        rows = [
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '010', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'],
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '100', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500']]
        IndependentDemand.extend(rows)

        self.assertIn(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '010', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'], IndependentDemand)
        IndependentDemand.del_row(rows[0])
        IndependentDemand.del_row(rows[1])

    def test_data_table_extend_with_data_table_rows(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site', 'Order.Type.ControlSet.Value', 'Order.Type', 'Line', 'Part.Name', 'Part.Site',
                'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})

        # execute
        rows = [
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '010', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'],
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '100', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500']]
        IndependentDemand.extend(rows)

        self.assertIn(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '010', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'], IndependentDemand)
        IndependentDemand.del_row(rows[0])
        IndependentDemand.del_row(rows[1])

    # test append
    def test_data_table_append(self):
        # setup
        env = Environment(local_sample_bootstrap)
        cols = ['Order.Id', 'Order.Site', 'Order.Type.ControlSet.Value', 'Order.Type', 'Line', 'Part.Name', 'Part.Site',
                'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})

        # execute
        rows = ['RKS-GSMa', 'SOPDC-NorthAmerica', 'Default', 'SOPDemandMgmt', '013', 'GSM-850A', 'SOPDC-NorthAmerica',
                '2017-08-31', '1500']
        IndependentDemand.append(rows)

        self.assertIn(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '013', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'], IndependentDemand)
        IndependentDemand.del_row(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '013', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'])

    # test del
    def test_data_table_delete(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site', 'Order.Type.ControlSet.Value', 'Order.Type', 'Line', 'Part.Name', 'Part.Site',
                'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})
        rows = [
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '01', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'],
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '10', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500']]
        IndependentDemand.extend(rows)

        # execute
        index = IndependentDemand.indexof(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '01', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'])
        del IndependentDemand[index]
        self.assertNotIn(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '01', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'], IndependentDemand)
        index = IndependentDemand.indexof(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '10', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'])
        del IndependentDemand[index]
        self.assertNotIn(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '10', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'], IndependentDemand)

    # test del_row
    def test_data_table_row_delete(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site', 'Order.Type.ControlSet.Value', 'Order.Type', 'Line', 'Part.Name', 'Part.Site',
                'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})
        rows = [
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '01', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'],
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '10', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500']]
        IndependentDemand.extend(rows)

        # execute
        self.assertIn(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '01', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'], IndependentDemand)
        IndependentDemand.del_row(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '01', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'])
        IndependentDemand.del_row(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '10', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1500'])

    def test_data_table_col_set(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site.Value', 'Order.Type.ControlSet.Value', 'Order.Type', 'Line', 'Part.Name',
                'Part.Site.Value',
                'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols,
                                      scenario={"Name": "Integration", "Scope": "Public"})

    # test update of attribute of individual record
    def test_data_table_col_update(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site.Value', 'Order.Type.ControlSet.Value', 'Order.Type', 'Line', 'Part.Name',
                'Part.Site.Value',
                'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, scenario={"Name": "Integration", "Scope": "Public"})
        rows = ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '06', 'GSM-850A',
                'SOPDC-NorthAmerica', '2017-08-31', '1500']
        IndependentDemand.append(rows)
        self.assertIn(rows, IndependentDemand)

        # execute
        rec = IndependentDemand[IndependentDemand.indexof(rows)]
        rec[7] = '1502'
        self.assertIn(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '06', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1502'], IndependentDemand)

        # teardown
        IndependentDemand.del_row(
            ['RKS-GSMa', 'SOPDC-NorthAmerica', 'SOPDemandMgmt', 'DCConsensus', '06', 'GSM-850A', 'SOPDC-NorthAmerica',
             '2017-08-31', '1502'])

    # test slicing

    # test bool

    # test indexof

    # test contains

class TestCalcOptimalPagesize(unittest.TestCase):
    def setUp(self):
        # Create a mock DataTable object with some columns for testing
        env = Environment(sample_configuration)
        self.data_table = DataTable(env,'Mfg::Part', refresh=False)
        self.data_table.columns = [
            Column('Column1', 'String', 'N', None),
            Column('Column2', 'String', 'N', None),
            Column('Column3', 'String', 'N', None),
            Column('Column4', 'String', 'N', None)
        ]

    def test_calc_optimal_pagesize_with_string_columns(self):
        # Test the calculation of optimal page size with string columns
        #self.data_table.columns[0].datatype = 'String'
        #self.data_table.columns[3].datatype = 'String'
        pagesize = self.data_table._calc_optimal_pagesize()
        self.assertEqual(pagesize, 320000)  # Expected page size based on string columns

    def test_calc_optimal_pagesize_with_datetime_column(self):
        # Test the calculation of optimal page size with a datetime column
        self.data_table.columns[1] = Column('Column2', 'DateTime', 'N', None)
        pagesize = self.data_table._calc_optimal_pagesize()
        self.assertEqual(pagesize, 327500)  # Expected page size based on datetime column

    def test_calc_optimal_pagesize_with_integer_column(self):
        # Test the calculation of optimal page size with an integer column
        self.data_table.columns[2] = Column('Column3', 'Integer', 'N', None)
        pagesize = self.data_table._calc_optimal_pagesize()
        self.assertEqual(pagesize, 342500)  # Expected page size based on integer column

    def test_calc_optimal_pagesize_with_unknown_datatype(self):
        # Test the calculation of optimal page size with an unknown datatype
        self.data_table.columns[0] = Column('Column1', 'Sausage', 'N', None)
        pagesize = self.data_table._calc_optimal_pagesize()
        self.assertEqual(pagesize, 340000)  # Default page size when datatype is unknown

'''
class TestRefreshDataAsync(unittest.IsolatedAsyncioTestCase):
    async def test_refresh_data_async_with_no_data_range(self):
        # Test refreshing data asynchronously without specifying a data range
        mock_environment = Environment(sample_configuration)
        mock_data_table = DataTable(mock_environment, 'Mfg::Part')
        mock_data_table._create_export = AsyncMock()
        mock_data_table._get_export_results_async = AsyncMock(return_value=[])

        await mock_data_table.RefreshData_async()

        mock_data_table._create_export.assert_called_once()
        mock_data_table._get_export_results_async.assert_called_once_with(
            mock_data_table.client, 0, 5000, mock_environment.limit
        )

    async def test_refresh_data_async_with_data_range(self):
        # Test refreshing data asynchronously with a specified data range
        mock_environment = Environment()
        mock_data_table = DataTable(mock_environment)
        mock_data_table._create_export = AsyncMock()
        mock_data_table._get_export_results_async = AsyncMock(return_value=[])

        await mock_data_table.RefreshData_async(data_range=10000)

        mock_data_table._create_export.assert_called_once()
        mock_data_table._get_export_results_async.assert_called_once_with(
            mock_data_table.client, 0, 10000, mock_environment.limit
        )
'''

class DataRowTestCase(unittest.TestCase):
    def test_row_init(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site.Value', 'Order.Customer.Id', 'Order.Type.Value', 'Order.Type.ControlSet.Value',
                'Line', 'Part.Name', 'Part.Site.Value', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, refresh=False)
        # execute
        rec = DataRow(
            ['GP', 'DC-NorthAmerica', 'FC102', 'DCActual', 'Default', '1', 'CDMA-C333', 'DC-NorthAmerica', '2017-06-15',
             '140'], IndependentDemand)
        #print(rec)
        self.assertIsNotNone(rec)

    def test_row_init_with_refresh(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site.Value', 'Order.Customer.Id', 'Order.Type.Value', 'Order.Type.ControlSet.Value',
                'Line', 'Part.Name', 'Part.Site.Value', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, refresh=True)
        # execute
        rec = DataRow(
            ['GP', 'DC-NorthAmerica', 'FC102', 'DCActual', 'Default', '1', 'CDMA-C333', 'DC-NorthAmerica', '2017-06-15',
             '140'], IndependentDemand)
        #print(rec)
        self.assertIsNotNone(rec)

    def test_row_length_mismatch(self):
        # setup
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site', 'Order.Type', 'Line', 'Part.Name','Part.Site', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, refresh=False)
        rows = [['GP','SOPDC-NorthAmerica','DCConsensus', '0', '7000vE','SOPDC-NorthAmerica', '2017-08-31', '1500'], ['GP','SOPDC-NorthAmerica','DCConsensus', '1', '7000vE','SOPDC-NorthAmerica', '2017-08-31']]

        # execute
        with self.assertRaises(DataError):
            dr = DataRow(['GP','SOPDC-NorthAmerica','DCConsensus' '0', '7000vE', '2017-08-31', '1500'], IndependentDemand)

    def test_dynamic_attribute_access(self):
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site.Value', 'Order.Customer.Id', 'Order.Type.Value', 'Order.Type.ControlSet.Value',
                'Line', 'Part.Name', 'Part.Site.Value', 'DueDate', 'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, refresh=False)
        # execute
        rec = DataRow(
            ['GP', 'DC-NorthAmerica', 'FC102', 'DCActual', 'Default', '1', 'CDMA-C333', 'DC-NorthAmerica', '2017-06-15',
             '140'], IndependentDemand)
        self.assertEqual(rec.Line, str(1))

    def test_dynamic_attribute_access_dot(self):
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site.Value', 'Order.Customer.Id', 'Order.Type.Value', 'Order.Type.ControlSet.Value',
                'Line', 'Part.Name', 'Part.Site.Value', 'DueDate',
                'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, refresh=False)
        # execute
        rec = DataRow(
            ['GP', 'DC-NorthAmerica', 'FC102', 'DCActual', 'Default', '1', 'CDMA-C333', 'DC-NorthAmerica', '2017-06-15',
             '140'], IndependentDemand)
        self.assertEqual(rec.Order_Type_Value, 'DCActual')

    def test_datarow_json_serialisable(self):
        env = Environment(sample_configuration)
        cols = ['Order.Id', 'Order.Site.Value', 'Order.Customer.Id', 'Order.Type.Value', 'Order.Type.ControlSet.Value',
                'Line', 'Part.Name', 'Part.Site.Value', 'DueDate',
                'Quantity']
        IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols, refresh=False)
        # execute
        rec = DataRow(
            ['GP', 'DC-NorthAmerica', 'FC102', 'DCActual', 'Default', '1', 'CDMA-C333', 'DC-NorthAmerica', '2017-06-15',
             '140'], IndependentDemand)
        #data = [{"Values": i} for i in rec]
        payload = json.dumps({
            'Scenario': {"Name": "Enterprise Data", "Scope": "Public"},
            'Table': {'Namespace': IndependentDemand._table_namespace,'Name': IndependentDemand._table_name},
            'Fields': [f.name for f in IndependentDemand.columns],
            'Rows': [{"Values": rec.data}]
        })
        #print(data)
        out = json.loads(payload)
        # print(out)
        self.assertIsNotNone(out)
        #self.assertEqual(rec.Order_Type, 'DCActual')

if __name__ == '__main__':
    unittest.main()
