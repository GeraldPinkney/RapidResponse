import importlib.resources
import json

import requests

import RapidResponse
from RapidResponse.DataModel import Column, Table
from RapidResponse.DataTable import DataTable
from RapidResponse.Environment import Environment
from RapidResponse.Resource import Workbook
from samples import sample_configuration, local_sample_bootstrap


def new_field_validate():
    env = Environment(local_sample_bootstrap)
    print(env.data_model._get_field_namespace('Mfg::Part', 'Name'))

def _load_from_package_resources():
    if importlib.resources.files('RapidResponse.data').joinpath('Tables.tab').is_file():
        print('found')
    else:
        print('not found')
        for entry in importlib.resources.files('RapidResponse.data').iterdir():
            print(entry.name)

    #ref = importlib.resources.files('RapidResponse.data' )/ 'Tables.tab'
    #with importlib.resources.as_file(ref) as path:
    #    print(type(path))

def test_pkg():
    _load_from_package_resources()
    pass

if __name__ == '__main__':
    _load_from_package_resources()
    #new_field_validate()


def stuff():
    print(RapidResponse.__version__)
    env = Environment(sample_configuration)

    print(env.get_table('Part', 'Mfg'))

    # print IndependentDemand fields
    Indy = env.get_table('IndependentDemand', 'Mfg')
    for f in Indy._table_fields:
        print(f)

    # print with subset of cols
    cols = ['Order', 'Line', 'Part', 'DueDate', 'Quantity']
    IndependentDemand = DataTable(env, 'Mfg::IndependentDemand', cols)
    for i in IndependentDemand[0:5]:
        print(i)

    part = DataTable(env, 'Mfg::Part', scenario={'Name': 'Integration', 'Scope': 'Public'})
    part.RefreshData()
    print(len(part))
    print(part)

    row0 = ['GP1-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor',
            '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1',
            'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '',
            'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']

    if row0 in part:
        part.del_row(row0)
    row1 = ['GP2-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor',
            '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1',
            'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '',
            'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0']
    if row1 in part:
        del part[part.indexof(row1)]

    rows = [row0, row1]
    part.extend(rows)
    print(len(part))

    for r in rows:
        part.del_row(r)

    part.append(['GP2-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor',
                 '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1',
                 'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '',
                 'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0'])

    index = part.indexof(
        ['GP2-8C3', 'Europe', 'B', '0', '1', '', '0', '0', '0', 'EU', '0', '-1', '', '', '0', 'AC Compressor',
         '', '0', '', 'Off', '0', '0.2', '0', '0', '0', '0', 'Ignore', '', '', '-1', '0', '', '', '0', '0', '1',
         'EU', 'DefaultMonth', '0', 'Automotive', 'Vehicle', 'Passenger', '0', '0053H-8C3', '0', '',
         'FixedLeadTimeSoft', '0', 'Ongoing', '0', '0', '0', '-1', 'Buy', 'EA', '0'])
    part[index][2] = 'C'

    part = Table('Part', 'Mfg', 'input', 'Y')
    col1 = Column('Column1', 'string', 'N')
    col2 = Column('Column2', 'string', 'N')
    part.add_fields(col1, col2)
    print(part.__str__())

    variable_values = {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All", "DataModel_IsIncludeDataTypeSet": "N",
                       "FilterType": "All"}

    wb = Workbook(environment=Environment(sample_configuration),
                  Scenario={"Name": 'Enterprise Data', "Scope": "Public"},
                  workbook={"Name": 'KXSHelperREST', "Scope": 'Public'},
                  SiteGroup="All Sites",
                  Filter={"Name": "All Parts", "Scope": "Public"},
                  VariableValues=variable_values,
                  WorksheetNames=["DataModel_Summary", "DataModel_Fields"]
                  )
    wb.RefreshData()
    for x in wb.worksheets:
        print(x)
        xRows = x.RefreshData()
        print(xRows)

    wb_ords = Workbook(environment=Environment(sample_configuration),
                       Scenario={"Name": "Integration", "Scope": "Public"},
                       workbook={"Name": 'Orders by Customer', "Scope": 'Public'},
                       SiteGroup="All Sites",
                       Filter={"Name": "All Parts", "Scope": "Public"},
                       VariableValues={"customer": "PCW"},
                       WorksheetNames=["Actual Orders"]
                       )
    ws = wb_ords.worksheets[0]
    ws.upload(["ordnum0", "1", "Kanata", "KNX", "7000vE", "", "130", "Default", "Kanata"],
              ["ordnum1", "1", "Kanata", "KNX", "7000vE", "", "130", "Default", "Kanata"])

    mea_dev = {'url': 'https://na1.kinaxis.net/mrad02_dev01', 'data_model_bootstrap': 'KXSHelperREST',
               'auth_type': 'basic',
               'username': 'RestAPI', 'password': 'WebAccess2021#'}
    mea_qa = {'url': 'https://na1.kinaxis.net/MRAT04_QA001', 'data_model_bootstrap': 'KXSHelperREST',
              'auth_type': 'basic',
              'username': 'RestAPI', 'password': 'WebAccess2021#'}

    mea_env = Environment(mea_dev)
    int_wb = {"Name": "[EU] Integration", "Scope": 'Public'}
    integration_workbook = Workbook(environment=mea_env, Scenario={'Name': 'Enterprise Data', 'Scope': 'Public'},
                                    workbook=int_wb, SiteGroup="All Sites", WorksheetNames=['RRSite'],
                                    Filter={"Name": "All Parts", "Scope": "Public"})
    RRSite = integration_workbook.worksheets[0]

    list_of_tables = ['Mfg::Part', 'Mfg::IndependentDemand', 'Mfg::Customer']
    for t in list_of_tables:
        print(DataTable(env, t))

    list_of_worksheets = ['worksheet1', 'worksheet2', 'worksheet3']

    print(list((filter(lambda x: x['Table'] == 'Part' and x['Field'] == 'Site', env.data_model._fields))))


def create_scenario(name, parent):
    env = Environment(sample_configuration)
    url = "http://localhost/rapidresponse/integration/V1/script/Public/Ignite_Create_Scenario"
    payload = json.dumps({
        "parentScenario": {'Name': 'Baseline', 'Scope': 'Public'},
        "newScenario": "Good2Great",
        "permenantScenario": "Y",
        "updateAutomatically": "Y",
        "userGroup": "Data Administrators"
    })
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic Z3BpbmtuZXlfd3M6MUwwdmVSQHBpZFJlc3BvbnNl'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def execute_script():

    url = "{{url}}/integration/V1/script/Public/Ignite_Create_Scenario"

    payload = "{\r\n    \"newScenario\": \"Good2Great2\",\r\n    \"userGroup\": \"Sales\"\r\n}"
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def export_pkg():
    import requests
    import base64
    url = "http://localhost/rapidresponse/integration/V1/applications/test_20240612/export"

    concat_user_pass = 'gpinkney_ws_migration' + ":" + '1L0veR@pidResponse'
    user_pass_bytes = concat_user_pass.encode('ascii')
    base64_bytes = base64.b64encode(user_pass_bytes)
    b64_authentication = base64_bytes.decode('ascii')
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ' + str(b64_authentication)
    }

    response = requests.request("GET", url, headers=headers)

    file = open("test_20240612.kpk", "wb")
    file.write(response.content)
    file.close() # yes, I could have done this with a context manager... whatevs


bel_bootstrap = {'url': 'https://eu21.kinaxis.net/BELD02_DEV01/', 'data_model_bootstrap': 'KXSHelperREST',
                 'auth_type': 'basic', 'username': 'IntegrationUser', 'password': 'Welcome1!'}


class dataTabNonAsync:
    def _create_export(self, session=None):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/bulkread_rest.htm?
        if session is None:
            session = self._session

        if self._filter:
            query_filter = self.filter
        else:
            query_filter = ''

        payload = json.dumps({
            "Scenario": self.scenario,
            "Table": {'Namespace': self._table_namespace, 'Name': self._table_name},
            "Fields": [f.name for f in self.columns],
            "Filter": query_filter
        })

        req = requests.Request("POST", self.environment.bulk_export_url , headers=self.environment.global_headers, data=payload)
        prepped = req.prepare()
        response = session.send(prepped)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            self._format_export_response(response_dict)
        else:
            raise RequestsError(response, f"error during POST to: {self.environment.bulk_export_url}", payload)

    def _get_export_results(self, session, startRow: int = 0, pageSize: int = 5000):
        if session is None:
            session = self._session
        # using slicing on the query handle to strip off the #
        url = self.environment.bulk_export_url + "/" + self._exportID[1:] + "?startRow=" + str(startRow) + "&pageSize=" + str(pageSize) + "&delimiter=%09" + "&finishExport=false"

        req = requests.Request("GET", url, headers=self.environment.global_headers)
        prepped = req.prepare()
        response = session.send(prepped)

        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {url}", None)

        # data returned with tab delimiter %09. split results.
        rows = [DataRow(rec.split('\t'), self) for rec in response_dict["Rows"]]
        return rows

    def RefreshData(self, data_range: int = 100_000, action_on_page=None):
        """
        Function that sequentially reads pages of response data from table read. will apply the action_on_page function to the returned data
        :param data_range: integer, requested page size. note, this is not the page size you'll get, but is adjusted by pagesizefactor
        :param action_on_page: function, function passed to RefreshData that is applied to each returned page
        :return: None
        """

        s = self._session
        self.environment.refresh_auth()
        s.headers=self.environment.global_headers

        self._create_export(s)
        self._table_data.clear()
        calc_data_range = self._calc_optimal_pagesize(data_range)
        for i in range(0, self._total_row_count, calc_data_range):
            page_response = self._get_export_results(s, i, calc_data_range)
            self._table_data.extend(page_response)
            if action_on_page is None:
                pass
            else:
                action_on_page(page_response)
        self._exportID = None
        s.close()

    def _test_data_table_refresh_with_funct(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env, 'Mfg::Part', refresh=False)
        # test
        self.assertEqual(len(part), 0)
        part.RefreshData(data_range=1000, action_on_page=print_recs)
        self.assertNotEqual(len(part), 0)

    def _test_data_table_no_refresh_properties(self):
        # setup
        env = Environment(sample_configuration)
        part = DataTable(env,'Mfg::Part', refresh=False)
        # test
        self.assertEqual(len(part), 0)
        part._create_export()
        self.assertNotEqual(part._total_row_count, 0)
        part._session.close()