# Worksheet.py

import json
import requests
import logging


from RapidResponse.RapidResponse.Err import RequestsError


class Worksheet:
    def __init__(self, environment, worksheet: str, workbook: dict, SiteGroup: str, Filter: dict, VariableValues: dict):
        """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?
        :param environment: Required. contains the env details for worksheet.
        :param worksheet: Required, the worksheets you want to retrieve data from. Example, DataModel_Summary
        :param workbook: Required, The workbook the required data is in. Example, {'Name': 'KXSHelperREST', "Scope": 'Public'}
        :param SiteGroup: Required, the site or site filter to use with the workbook Example, "All Sites"
        :param Filter: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}
        """
        self.environment = environment
        self.parent_workbook = workbook
        self._site_group = SiteGroup
        self._filter = Filter # todo handle these properly. only optional
        self._variable_values = VariableValues # todo handle these properly. only optional
        self.name = worksheet
        # todo add support for filter expression
        # todo add support for hierarchies

        self.columns = []
        self.rows = []

        self._queryID = None
        self.total_row_count = None

    def _initialise_for_extract(self):

        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/data/workbook"

        workbook_parameters = {
            "Workbook": self.parent_workbook, # {'Name': 'KXSHelperREST', "Scope": 'Public'}
            "SiteGroup": self._site_group, # "All Sites"
            "Filter": self._filter, # {"Name": "All Parts", "Scope": "Public"}
            "VariableValues": self._variable_values,
            "WorksheetNames": [self.name]
        }

        payload = json.dumps({
            'Scenario': self.environment.scenarios[0],
            'WorkbookParameters': workbook_parameters
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)

        else:
            raise RequestsError(response.text,
                                " failure during workbook initialise_for_extract, status not 200" )

        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == self.name:
                self._queryID = ws['QueryHandle']['QueryID']
                self.total_row_count = ws.get('TotalRowCount')
                self.columns = ws.get('Columns')
                self.rows = ws.get('Rows') # should be []

    def _retrieve_worksheet_data(self, pagesize=500):
        # add some checking for not null, blah. check pagesize is not insane
        """

        :param pagesize:
        :return: rows[]
        """
        rows = []
        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        burl = self.environment._base_url + "/integration/V1/data/worksheet" + "?queryId=" + self._queryID[1:] + "&workbookName=" + self.parent_workbook['Name'] + "&Scope=" + self.parent_workbook['Scope'] + "&worksheetName=" + self.name

        pages = self.total_row_count//pagesize
        if self.total_row_count % pagesize != 0:
            pages = pages + 1

        for i in range(pages):
            url = burl + "&startRow=" + str(0+(pagesize*i)) + "&pageSize=" + str(pagesize)
            response = requests.request("GET", url, headers=headers) # using GET means you can embed stuff in url, rather than the POST endpoint which needs you to have stuff in payload
            # check valid response
            if response.status_code == 200:
                response_dict = json.loads(response.text)

            else:

                raise RequestsError(response.text,"failure during workbook retrieve_worksheet_data, status not 200" + '\nurl:' + url)

            response_rows = response_dict['Rows']

            for r in response_rows:
                #print(r['Values'])
                rows.append(r['Values'])

            self.rows = rows

        #print(len(rows))
        return rows

    def fetch_data(self):
        try:
            self._initialise_for_extract()
        except:
            print("bail, its a scam!")
        else:
            self._retrieve_worksheet_data()

    def upload(self, *args):
        """
        Sending the request imports the data specified in the Rows field using the worksheet's import rules
        :param args: list [] of records you watn to send. don't just send a single record!! i.e. [0,0]
        :return:
        """
        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/data/workbook/import"

        workbook_parameters = {
            "Workbook": self.parent_workbook, # {'Name': 'KXSHelperREST', "Scope": 'Public'}
            "SiteGroup": self._site_group, # "All Sites"
            "Filter": self._filter, # {"Name": "All Parts", "Scope": "Public"}
            "VariableValues": self._variable_values,
            "WorksheetNames": [self.name]
        }
        rows = []
        for i in args:
            # create inner array (list)
            # arr = [i]
            # arr.append(i)
            # create dict containing single element {"Values": []}
            values = {"Values": i}
            # append to Rows
            rows.append(values)

        payload = json.dumps({
            'Scenario': self.environment.scenarios[0],
            'WorkbookParameters': workbook_parameters,
            'Rows': rows
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response.text,
                                "failure during workbook-worksheet upload, status not 200" + '\nurl:' + url + '\npayload: ' + payload + '\nheaders' + headers)
        # print(response)
        results = response_dict['Results']
        response_readable = 'status: ' + results['Status'] + '\nInsertedRowCount: ' + str(
            results['InsertedRowCount']) + '\nModifiedRowCount: ' + str(
            results['ModifiedRowCount']) + '\nDeleteRowCount: ' + str(
            results['DeleteRowCount']) + '\nErrorRowCount: ' + str(
            results['ErrorRowCount']) + '\nUnchangedRowCount: ' + str(results['UnchangedRowCount'])
        logging.info(response_readable)
        if results['Status'] != 'true':
            print('status not true')
            print(response_readable)
            Exception("eek")
        # todo if Status is failure, do something.

class Workbook:
    def __init__(self, Environment, Scenario: dict, workbook: dict, SiteGroup: str, Filter: dict, VariableValues: dict, WorksheetNames: list):
        """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?

        :param Environment:
        :param Scenario:
        :param workbook: {"Name": 'workbookname', "Scope": 'Public'}
        :param SiteGroup: "All Sites"
        :param Filter: {"Name": "All Parts","Scope": "Public"}
        :param VariableValues:
        :param WorksheetNames: ["worksheet name1", "worksheet name2"]
        """
        self._scenario = Scenario
        self._workbook = workbook
        self._site_group = SiteGroup
        self._filter = Filter
        self._variable_values = VariableValues
        self.environment = Environment

        self._worksheets = []
        for name in WorksheetNames:

            self._worksheets.append(Worksheet(self.environment, name, self._workbook, self._site_group, self._filter, self._variable_values))



