# Worksheet.py

import json
import requests
import logging

from RapidResponse.Err import RequestsError, DataError
from RapidResponse.Environment import Environment


class Cell:
    pass
    # value, datatype, columnId


class Worksheet:
    """
    https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?

    :param scenario:
    :param environment: Required. contains the env details for worksheet.
    :param worksheet: Required, the worksheets you want to retrieve data from. Example, DataModel_Summary
    :param workbook: Required, The workbook the required data is in. Example, {'Name': 'KXSHelperREST', "Scope": 'Public'}
    :param SiteGroup: Required, the site or site filter to use with the workbook Example, "All Sites"
    :param Filter: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
    :param VariableValues: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}
    """

    def __init__(self, environment, scenario, worksheet: str, workbook: dict, SiteGroup: str, Filter: dict = None,
                 VariableValues: dict = None):
        """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?

        :param scenario:
        :param environment: Required. contains the env details for worksheet.
        :param worksheet: Required, the worksheets you want to retrieve data from. Example, DataModel_Summary
        :param workbook: Required, The workbook the required data is in. Example, {'Name': 'KXSHelperREST', "Scope": 'Public'}
        :param SiteGroup: Required, the site or site filter to use with the workbook Example, "All Sites"
        :param Filter: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}
        """
        self.logger = logging.getLogger('RapidPy.wb.ws')
        # validations
        # environment
        if not isinstance(environment, Environment):
            raise TypeError("The parameter environment type must be Environment.")
        if not environment:
            raise ValueError("The parameter environment must not be empty.")
        self.environment = environment

        # worksheet
        if not isinstance(worksheet, str):
            raise TypeError("The parameter worksheet type must be str.")
        if not worksheet:
            raise ValueError("The parameter worksheet must not be empty.")
        self._name = worksheet

        # workbook
        if not isinstance(workbook, dict):
            raise TypeError("The parameter workbook type must be dict.")
        if not workbook:
            raise ValueError("The parameter workbook must not be empty.")
        wb_keys = workbook.keys()
        if len(wb_keys) != 2:
            raise ValueError("The parameter workbook must contain only Name and Scope.")
        if 'Name' not in wb_keys:
            raise ValueError("The parameter workbook must contain Name.")
        if 'Scope' not in wb_keys:
            raise ValueError("The parameter workbook must contain Scope.")
        self._parent_workbook = workbook

        # sitegroup
        if not isinstance(SiteGroup, str):
            raise TypeError("The parameter SiteGroup type must be str.")
        if not SiteGroup:
            raise ValueError("The parameter SiteGroup must not be empty.")
        self._site_group = SiteGroup

        # scenario
        if scenario:
            if not isinstance(scenario, dict):
                raise TypeError("The parameter scenario type must be dict.")
            scenario_keys = scenario.keys()
            if len(scenario_keys) != 2:
                raise ValueError("The parameter scenario must contain only Name and Scope.")
            if 'Name' not in scenario_keys:
                raise ValueError("The parameter scenario must contain Name.")
            if 'Scope' not in scenario_keys:
                raise ValueError("The parameter scenario must contain Scope.")
            self._scenario = scenario
        else:
            self._scenario = self.environment.scenarios[0]

        self._filter = Filter
        self._variable_values = VariableValues

        # todo add support for filter expression
        # todo add support for hierarchies

        self.columns = []
        self.rows = []

        self._queryID = None
        self.total_row_count = None

        # initialise for extract to get colum lists and total row count
        self._initialise_for_extract()

    @property
    def name(self):
        return self._name

    @property
    def parent_workbook(self):
        return self._parent_workbook

    @property
    def parent_workbook_name(self):
        return self._parent_workbook['Name']

    @property
    def parent_workbook_scope(self):
        return self._parent_workbook['Scope']

    def __len__(self):
        return len(self.rows)

    def __bool__(self):
        if len(self) > 0:
            return True
        else:
            return False

    def __getitem__(self, position):
        return self.rows[position]

    def __contains__(self, item):
        # get key fields for table. then check if that value is present
        if item in self.rows:
            return True
        else:
            return False

    def __repr__(self):
        return f'Worksheet(environment={self.environment!r},worksheet={self.name!r},workbook={self.parent_workbook!r},SiteGroup={self._site_group!r},Filter={self._filter!r},VariableValues={self._variable_values!r}) '

    def __str__(self):
        # return self and first 5 rows
        response = f'Worksheet: {self.name!r}, Scope: {self.parent_workbook_scope!r} '
        if len(self.rows) > 5:
            for i in range(0, 5):
                response = response + 'rownum: ' + str(i) + ' ' + str(self.rows[i]) + '\n'
            response = response + '...'
        return response

    def _initialise_for_extract(self):
        """

        :return: response_dict
        """
        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/data/workbook"

        workbook_parameters = {
            "Workbook": self.parent_workbook,  # {'Name': 'KXSHelperREST', "Scope": 'Public'}
            "SiteGroup": self._site_group,  # "All Sites"
            # "Filter": self._filter, # {"Name": "All Parts", "Scope": "Public"}
            # "VariableValues": self._variable_values,
            "WorksheetNames": [self.name]
        }
        # add optional parameters if they were provided
        if self._filter:
            workbook_parameters['Filter'] = self._filter
        if self._variable_values:
            workbook_parameters['VariableValues'] = self._variable_values

        payload = json.dumps({
            'Scenario': self._scenario,
            'WorkbookParameters': workbook_parameters
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)

        else:
            self.logger.error(payload)
            self.logger.error(url)
            raise RequestsError(response.text,
                                " failure during workbook initialise_for_extract, status not 200")

        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == self.name:
                self._queryID = ws['QueryHandle']['QueryID']
                self.total_row_count = ws.get('TotalRowCount')
                self.columns = ws.get('Columns')
                self.rows = ws.get('Rows')  # should be []
        return response_dict

    def _retrieve_worksheet_data(self, pagesize=500):
        # add some checking for not null, blah. check pagesize is not insane
        """

        :param pagesize:
        :return: rows[]
        """
        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        burl = self.environment._base_url + "/integration/V1/data/worksheet" + "?queryId=" + self._queryID[1:] + "&workbookName=" + self.parent_workbook['Name'] + "&Scope=" + self.parent_workbook['Scope'] + "&worksheetName=" + self.name

        pages = self.total_row_count // pagesize
        if self.total_row_count % pagesize != 0:
            pages = pages + 1

        for i in range(pages):
            url = burl + "&startRow=" + str(0 + (pagesize * i)) + "&pageSize=" + str(pagesize)
            response = requests.request("GET", url,
                                        headers=headers)  # using GET means you can embed stuff in url, rather than the POST endpoint which needs you to have stuff in payload
            # check valid response
            if response.status_code == 200:
                response_dict = json.loads(response.text)

            else:

                raise RequestsError(response.text,
                                    "failure during workbook retrieve_worksheet_data, status not 200" + '\nurl:' + url)

            # response_rows = response_dict['Rows']
            # for r in response_rows:
            #    # print(r['Values'])
            #    rows.append()
            # self.rows = rows
            for r in response_dict["Rows"]:
                # returned = rec.split('\t')
                self.rows.append(WorksheetRow(r['Values'], self))

        # print(len(rows))
        return self.rows

    def fetch_data(self):
        try:
            self._initialise_for_extract()
        except:
            self.logger.error("bail, its a scam!")
        else:
            return self._retrieve_worksheet_data()

    def upload(self, *args):
        """
        Sending the request imports the data specified in the Rows field using the worksheet's import rules

        :param args: list [] of records you want to send. don't just send a single record!! i.e. [0,0]
        :return: results from request
        """
        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/data/workbook/import"

        workbook_parameters = {
            "Workbook": self.parent_workbook,  # {'Name': 'KXSHelperREST', "Scope": 'Public'}
            "SiteGroup": self._site_group,  # "All Sites"
            "Filter": self._filter,  # {"Name": "All Parts", "Scope": "Public"}
            "VariableValues": self._variable_values,
            "WorksheetNames": [self.name]
        }
        # add optional parameters if they were provided
        if self._filter:
            workbook_parameters['Filter'] = self._filter
        if self._variable_values:
            workbook_parameters['VariableValues'] = self._variable_values

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
            'Scenario': self._scenario,
            'WorkbookParameters': workbook_parameters,
            'Rows': rows
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            self.logger.info(response_dict)
            results = response_dict['Worksheets'][
                0]  # this only supports single worksheet, so no idea why its an array.
            response_readable = 'status: ' + str(response_dict['Success']) + \
                                '\nWorksheetName: ' + str(results['WorksheetName']) + \
                                '\nImportedRowCount: ' + str(results['ImportedRowCount']) + \
                                '\nInsertedRowCount: ' + str(results['InsertedRowCount']) + \
                                '\nModifiedRowCount: ' + str(results['ModifiedRowCount']) + \
                                '\nDeletedRowCount: ' + str(results['DeletedRowCount']) + \
                                '\nErrorRowCount: ' + str(results['ErrorRowCount']) + \
                                '\nErrors: ' + str(results['Errors'])
            self.logger.info(response_readable)
        else:
            raise RequestsError(response.text,
                                "failure during workbook-worksheet upload, status not 200" + '\nurl:' + url)
        # print(response)
        return results


class Workbook:
    """
    https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?\n
    :param environment: Required. contains the env details for worksheet.\n
    :param Scenario: Optional \n
    :param workbook: Required, The workbook the required data is in. Example,{"Name": 'workbookname', "Scope": 'Public'}
    :param SiteGroup: Required, the site or site filter to use with the workbook Example, "All Sites"
    :param WorksheetNames: Required, the worksheets you want to retrieve data from ["worksheet name1", "worksheet name2"]
    :param Filter: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
    :param VariableValues: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}


    """

    def __init__(self, environment, Scenario: dict, workbook: dict, SiteGroup: str, WorksheetNames: list,
                 Filter: dict = None, VariableValues: dict = None):
        """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?

        :param environment: Required. contains the env details for worksheet.
        :param Scenario:
        :param workbook: Required, The workbook the required data is in. Example,{"Name": 'workbookname', "Scope": 'Public'}
        :param SiteGroup: Required, the site or site filter to use with the workbook Example, "All Sites"
        :param WorksheetNames: Required, the worksheets you want to retrieve data from ["worksheet name1", "worksheet name2"]
        :param Filter: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}


        """
        self.logger = logging.getLogger('RapidPy.wb')
        if not isinstance(environment, Environment):
            raise TypeError("The parameter environment type must be Environment.")
        if not environment:
            raise ValueError("The parameter environment must not be empty.")
        self.environment = environment

        if Scenario:
            if not isinstance(Scenario, dict):
                raise TypeError("The parameter scenario type must be dict.")
            scenario_keys = Scenario.keys()
            if len(scenario_keys) != 2:
                raise ValueError("The parameter scenario must contain only Name and Scope.")
            if 'Name' not in scenario_keys:
                raise ValueError("The parameter scenario must contain Name.")
            if 'Scope' not in scenario_keys:
                raise ValueError("The parameter scenario must contain Scope.")
            self._scenario = Scenario
        else:
            self._scenario = self.environment.scenarios[0]

        if not isinstance(workbook, dict):
            raise TypeError("The parameter workbook type must be dict.")
        if not workbook:
            raise ValueError("The parameter workbook must not be empty.")

        wb_keys = workbook.keys()
        if len(wb_keys) != 2:
            raise ValueError("The parameter workbook must contain only Name and Scope.")
        if 'Name' not in wb_keys:
            raise ValueError("The parameter workbook must contain Name.")
        if 'Scope' not in wb_keys:
            raise ValueError("The parameter workbook must contain Scope.")
        self._workbook = workbook

        if not isinstance(SiteGroup, str):
            raise TypeError("The parameter SiteGroup type must be str.")
        if not SiteGroup:
            raise ValueError("The parameter SiteGroup must not be empty.")
        self._site_group = SiteGroup

        self._filter = Filter
        self._variable_values = VariableValues

        self.worksheets = []
        for name in WorksheetNames:
            self.worksheets.append(
                Worksheet(self.environment, self._scenario, name, self._workbook, self._site_group, self._filter,
                          self._variable_values))

        # todo add __methods__

    def __str__(self):
        return f'Name: {self.name!r}, Scope: {self.workbook_scope!r} '

    def refresh(self):
        # populate all child worksheets with data
        for ws in self.worksheets:
            try:
                ws.fetch_data()
            except:
                self.logger.error('something went wrong with ' + ws.name)

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, new_filter):
        if not isinstance(new_filter, dict):
            raise TypeError("filter must be dict.")
        if not new_filter:
            raise ValueError("filter must not be empty.")

        filt_keys = new_filter.keys()
        if len(filt_keys) != 2:
            raise ValueError("filter must contain only Name and Scope.")
        if 'Name' not in filt_keys:
            raise ValueError("filter must contain Name.")
        if 'Scope' not in filt_keys:
            raise ValueError("filter must contain Scope.")
        self._filter = new_filter

    @property
    def name(self):
        return self._workbook['Name']

    @property
    def workbook_scope(self):
        return self._workbook['Scope']

    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, new_scenario):
        if not isinstance(new_scenario, dict):
            raise TypeError("The parameter scenario type must be dict.")
        scenario_keys = new_scenario.keys()
        if len(scenario_keys) != 2:
            raise ValueError("The parameter scenario must contain only Name and Scope.")
        if 'Name' not in scenario_keys:
            raise ValueError("The parameter scenario must contain Name.")
        if 'Scope' not in scenario_keys:
            raise ValueError("The parameter scenario must contain Scope.")
        self._scenario = new_scenario

    @property
    def site_group(self):
        return self._site_group

    @site_group.setter
    def site_group(self, new_site_group):
        self._site_group = new_site_group

    def __len__(self):
        return len(self.worksheets)

    def __getitem__(self, position):
        return self.worksheets[position]

    # todo make sure these actually work

    def indexof(self, rec):
        return self.worksheets.index(rec)

    def __contains__(self, item):
        # get key fields for table. then check if that value is present
        if item in self.worksheets:
            return True
        else:
            return False


class WorksheetRow(list):
    def __init__(self, iterable, worksheet: Worksheet):
        # initialises a new instance WorksheetRow(['GP', '0', '7000vE', '2017-08-31'], WorksheetName)

        # grab the necessary info from owning table
        self._worksheet = worksheet

        # perform validations
        if not isinstance(worksheet, Worksheet):
            raise TypeError("The parameter worksheet type must be Worksheet.")
        if len(iterable) == len(self._worksheet.columns):
            super().__init__(str(item) for item in iterable)
        else:
            raise DataError(str(iterable), 'mismatch in length of worksheet columns ' + str(
                len(self._worksheet.columns)) + ' and row: ' + str(len(iterable)))

    @property
    def columns(self):
        return self._worksheet.columns

    def __setitem__(self, index, item):
        # assign a new value using the item’s index, like a_list[index] = item
        # super().__setitem__(index, str(item))
        raise NotImplementedError

    def insert(self, index, item):
        # allows you to insert a new item at a given position in the underlying list using the index.
        raise NotImplementedError

    def append(self, item):
        # adds a single new item at the end of the underlying list
        raise NotImplementedError

    def extend(self, other):
        # adds a series of items to the end of the list.
        raise NotImplementedError

    def __add__(self, other):
        raise NotImplementedError

    def __radd__(self, other):
        raise NotImplementedError

    def __iadd__(self, other):
        raise NotImplementedError

    def join(self, separator=" "):
        # concatenates all the list’s items in a single string
        return separator.join(str(item) for item in self)

    def map(self, action):
        # yields new items that result from applying an action() callable to each item in the underlying list
        return type(self)(action(item) for item in self)

    def filter(self, predicate):
        # yields all the items that return True when calling predicate() on them
        return type(self)(item for item in self if predicate(item))

    def for_each(self, func):
        # calls func() on every item in the underlying list to generate some side effect.
        for item in self:
            func(item)
