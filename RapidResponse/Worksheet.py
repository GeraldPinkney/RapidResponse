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
                 VariableValues: dict = None, sync: bool = True, refresh: bool = True):
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
        self._logger = logging.getLogger('RapidPy.wb.ws')
        # validations
        # environment
        if not isinstance(environment, Environment):
            raise TypeError("The parameter environment type must be Environment.")
        if not environment:
            raise ValueError("The parameter environment must not be empty.")
        self.environment = environment

        # worksheet
        #if not isinstance(worksheet, str):
        #    raise TypeError("The parameter worksheet type must be str.")
        if not worksheet:
            raise ValueError("The parameter worksheet must not be empty.")
        self._name = str(worksheet)

        # workbook
        #if not isinstance(workbook, dict):
        #    raise TypeError("The parameter workbook type must be dict.")
        #if not workbook:
        #    raise ValueError("The parameter workbook must not be empty.")
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
        self._sync = bool(sync)
        self._refresh = bool(refresh)

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
        # todo add support for hierarchies

        self.columns = []
        self.rows = []

        self._queryID = None
        self.total_row_count = None

        self.RefreshData()

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

    def _create_export(self, session):
        """

        :return: response_dict
        """
        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/data/workbook"

        workbook_parameters = {
            "Workbook": self.parent_workbook,  # {'Name': 'KXSHelperREST', "Scope": 'Public'}
            "SiteGroup": self._site_group,  # "All Sites"
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

        req = requests.Request("POST", url, headers=headers, data=payload)
        prepped = req.prepare()
        response = session.send(prepped)

        # print(response.text)
        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            self._logger.error(payload)
            self._logger.error(url)
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

    def _get_export_results(self, session, startRow: int = 0, pageSize: int = 500):
        # add some checking for not null, blah. check pagesize is not insane
        """

        :param session:
        :param startRow:
        :param pageSize:
        :return: rows[]
        """
        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/data/worksheet" + "?queryId=" + self._queryID[
                                                                                            1:] + "&workbookName=" + \
              self.parent_workbook['Name'] + "&Scope=" + self.parent_workbook[
                  'Scope'] + "&worksheetName=" + self.name + "&startRow=" + str(
            startRow) + "&pageSize=" + str(pageSize)

        req = requests.Request("GET", url, headers=headers)
        prepped = req.prepare()
        response = session.send(prepped)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response.text,
                                "failure during workbook retrieve_worksheet_data, status not 200" + '\nurl:' + url)

        rows = []
        for rec in response_dict["Rows"]:
            rows.append(WorksheetRow(rec['Values'], self))
        return rows

    def RefreshData(self, data_range: int = 50000):
        s = requests.Session()
        self.environment.refresh_auth()
        try:
            self._create_export(s)
        except TypeError:
            raise RequestsError(msg='likely due to invalid worksheetname')
        except:
            self._logger.error("bail, its a scam!")
            raise RequestsError(msg='Error during create export')
        else:
            self.rows.clear()
            for i in range(0, self.total_row_count, data_range):
                self.rows.extend(self._get_export_results(s, i, data_range))
        finally:
            self._queryID = None
            s.close()

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

        rows = [{"Values": i} for i in args]
        #for i in args:
        #    values = {"Values": i}
        #    rows.append(values)

        payload = json.dumps({
            'Scenario': self._scenario,
            'WorkbookParameters': workbook_parameters,
            'Rows': rows
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            self._logger.error(payload)
            raise RequestsError(response.text,
                                f"failure during workbook-worksheet upload, status {response.status_code} \nurl: {url}")

        results = response_dict['Worksheets'][0]  # this only supports single worksheet, so no idea why its an array.
        response_readable = 'status: ' + str(response_dict['Success']) + \
                            '\nWorksheetName: ' + str(results['WorksheetName']) + \
                            '\nImportedRowCount: ' + str(results['ImportedRowCount']) + \
                            '\nInsertedRowCount: ' + str(results['InsertedRowCount']) + \
                            '\nModifiedRowCount: ' + str(results['ModifiedRowCount']) + \
                            '\nDeletedRowCount: ' + str(results['DeletedRowCount']) + \
                            '\nErrorRowCount: ' + str(results['ErrorRowCount']) + \
                            '\nErrors: ' + str(results['Errors'])

        if response_dict['Success'] and results['ErrorRowCount'] <= 0:
            self._logger.info(response_readable)
            self._logger.info(response_dict)
        elif response_dict['Success'] and results['ErrorRowCount'] > 0:
            self._logger.warning(response_readable)
            self._logger.warning(response_dict)
            self._logger.warning(payload)
            raise RequestsError(response.text,
                                f"partial failure during worksheet upload. ErrorCount: {results['ErrorRowCount']}")
        else:
            self._logger.error(response_readable)
            self._logger.error(response_dict)
            self._logger.error(payload)
            raise RequestsError(response.text, f"failure during worksheet upload")
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
            #if not isinstance(Scenario, dict):
            #    raise TypeError("The parameter scenario type must be dict.")
            scenario_keys = Scenario.keys()
            #if len(scenario_keys) != 2:
            #    raise ValueError("The parameter scenario must contain only Name and Scope.")
            if 'Name' not in scenario_keys:
                raise ValueError("The parameter scenario must contain Name.")
            if 'Scope' not in scenario_keys:
                raise ValueError("The parameter scenario must contain Scope.")
            self._scenario = Scenario
        else:
            self._scenario = self.environment.scenarios[0]

        #if not isinstance(workbook, dict):
        #    raise TypeError("The parameter workbook type must be dict.")
        if not workbook:
            raise ValueError("The parameter workbook must not be empty.")

        wb_keys = workbook.keys()
        #if len(wb_keys) != 2:
        #    raise ValueError("The parameter workbook must contain only Name and Scope.")
        if 'Name' not in wb_keys:
            raise ValueError("The parameter workbook must contain Name.")
        if 'Scope' not in wb_keys:
            raise ValueError("The parameter workbook must contain Scope.")
        self._workbook = workbook

        if not isinstance(SiteGroup, str):
            raise TypeError("The parameter SiteGroup type must be str.")
        if not SiteGroup:
            #raise ValueError("The parameter SiteGroup must not be empty.")
            self._site_group = 'All Sites'
        else:
            self._site_group = SiteGroup

        if not Filter:
            self._filter = dict({"Name": "All Parts", "Scope": "Public"})
        else:
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
                ws.RefreshData()
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
        #if not isinstance(new_scenario, dict):
        #    raise TypeError("The parameter scenario type must be dict.")
        scenario_keys = new_scenario.keys()
        if len(scenario_keys) != 2:
            raise ValueError("The parameter scenario must contain only Name and Scope.")
        if 'Name' not in scenario_keys:
            raise ValueError("The parameter scenario must contain Name.")
        if 'Scope' not in scenario_keys:
            raise ValueError("The parameter scenario must contain Scope.")
        self._scenario = new_scenario

    @property
    def environment(self):
        return self.environment



    @property
    def site_group(self):
        return self._site_group

    @site_group.setter
    def site_group(self, new_site_group):
        self._site_group = str(new_site_group)

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
        if not isinstance(worksheet, Worksheet):
            raise TypeError("The parameter worksheet type must be Worksheet.")
        # grab the necessary info from owning table
        self._worksheet = worksheet

        # perform validations
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
