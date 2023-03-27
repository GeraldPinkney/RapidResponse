# Worksheet.py

import json
import requests

from RapidResponse.RapidResponse.Err import RequestsError

class Worksheet:

    def __init__(self, environment, worksheet: str, workbook: dict, SiteGroup: str, Filter: dict, VariableValues: dict):
        """

        :param environment:
        :param worksheet: DataModel_Summary
        :param workbook: {'Name': 'KXSHelperREST', "Scope": 'Public'}
        :param SiteGroup: "All Sites"
        :param Filter: {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues: {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}
        """
        self.environment = environment
        self.parent_workbook = workbook
        self._site_group = SiteGroup
        self._filter = Filter
        self._variable_values = VariableValues
        self.name = worksheet
        self.columns = []
        self.rows = []

        self._queryID = None
        self.total_row_count = None

    def initialise_for_extract(self):

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

    def retrieve_worksheet_data(self, pagesize=500):
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

class Workbook:
    def __init__(self, Environment, Scenario: dict, Workbook: dict, SiteGroup: str, Filter: dict, VariableValues: dict, WorksheetNames: list):
        """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?

        :param Environment:
        :param Scenario:
        :param Workbook: {"Name": 'workbookname', "Scope": 'Public'}
        :param SiteGroup: "All Sites"
        :param Filter: {"Name": "All Parts","Scope": "Public"}
        :param VariableValues:
        :param WorksheetNames: ["worksheet name1", "worksheet name2"]
        """
        self._scenario = Scenario
        self._workbook = Workbook
        self._site_group = SiteGroup
        self._filter = Filter
        self._variable_values = VariableValues
        self.environment = Environment

        self._worksheets = []
        for name in WorksheetNames:

            self._worksheets.append(Worksheet(self.environment, name, self._workbook, self._site_group, self._filter, self._variable_values))



