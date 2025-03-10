# Worksheet.py
import asyncio
import json
from collections import UserList

import httpx
import requests
import logging
import re
from datetime import date
from RapidResponse.Err import RequestsError, DataError
from RapidResponse.Environment import Environment
from RapidResponse.Utils import SCOPE_PUBLIC, VALID_SCOPES


class AbstractWorkBook:
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
    # WORKBOOK_URL = "/integration/V1/data/workbook"
    '''SCOPE_PUBLIC = 'Public'
    SCOPE_PRIVATE = 'Private'
    VALID_SCOPES = {SCOPE_PUBLIC, SCOPE_PRIVATE}'''
    ALL_SITES = 'All Sites'

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
        self._logger = logging.getLogger('RapidPy.wb.wb')
        self.worksheets = list()
        self._scenario = dict()
        self._environment = None
        self._workbook = dict()
        self._site_group = None
        self._filter = None
        self._variable_values = None


    def __str__(self):
        return f'Name: {self.name!r}, Scope: {self.workbook_scope!r} '

    def refresh(self):
        # populate all child worksheets with data
        pass

    @property
    def environment(self):
        return self._environment

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, new_filter):
        s = new_filter['Scope'] if new_filter['Scope'] in VALID_SCOPES else SCOPE_PUBLIC
        n = new_filter['Name']

        self._filter = dict(Name=n, Scope=s)
        for ws in self.worksheets:
            ws.filter = self.filter

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
        self._scenario = dict(Name=new_scenario['Name'], Scope=new_scenario['Scope'])
        for ws in self.worksheets:
            ws.scenario = self.scenario

    @property
    def site_group(self):
        return self._site_group

    @site_group.setter
    def site_group(self, new_site_group):
        self._site_group = str(new_site_group)
        for ws in self.worksheets:
            ws.site_group = self.site_group

    def __len__(self):
        return len(self.worksheets)

    def __getitem__(self, position):
        return self.worksheets[position]

    def indexof(self, rec):
        return self.worksheets.index(rec)

    def __contains__(self, item):
        # get key fields for table. then check if that value is present
        if item in self.worksheets:
            return True
        else:
            return False


class Workbook(AbstractWorkBook):
    """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?\n
        :param environment: Required. contains the env details for worksheet.\n
        :param Scenario: Optional dict {"Name": "Enterprise Data", "Scope": "Public"}\n
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
        :param Scenario: dict {"Name": "Enterprise Data", "Scope": "Public"}
        :param workbook: Required, The workbook the required data is in. Example,{"Name": 'workbookname', "Scope": 'Public'}
        :param SiteGroup: Required, the site or site filter to use with the workbook Example, "All Sites"
        :param WorksheetNames: Required, the worksheets you want to retrieve data from ["worksheet name1", "worksheet name2"]
        :param Filter: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}


        """
        super().__init__(environment, Scenario, workbook, SiteGroup, WorksheetNames, Filter, VariableValues)

        # validations
        if not isinstance(environment, Environment):
            raise TypeError("The parameter environment type must be Environment.")
        if not environment:
            raise ValueError("The parameter environment must not be empty.")

        # assign env
        self._environment = environment

        if Scenario:
            self._scenario = dict(Name=Scenario['Name'], Scope=Scenario['Scope'])
        else:
            self._scenario = self.environment.scenarios[0]

        self._workbook = dict(Name=workbook['Name'], Scope=workbook['Scope'])

        if not SiteGroup:
            self._site_group = self.ALL_SITES
        else:
            self._site_group = str(SiteGroup)

        if not Filter:
            self._filter = dict({"Name": "All Parts", "Scope": SCOPE_PUBLIC})
        else:
            self._filter = dict(Name=Filter['Name'], Scope=Filter['Scope'])

        self._variable_values = dict(VariableValues)

        self.worksheets = [
            Worksheet(self.environment, name, self._workbook, self._scenario, self._site_group, self._filter,
                      self._variable_values) for name in WorksheetNames]

    def refresh(self):
        # populate all child worksheets with data
        for ws in self.worksheets:
            try:
                ws.RefreshData_async()
            except:
                self._logger.error('something went wrong with ' + ws.name)
                raise


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
    :param sync: boolean control whether any updates are pushed back to RR
    :param refresh: boolean refresh row data on initialisation
    """
    #WORKSHEET_URL = "/integration/V1/data/worksheet"
    '''SCOPE_PUBLIC = 'Public'
    SCOPE_PRIVATE = 'Private'
    VALID_SCOPES = {SCOPE_PUBLIC, SCOPE_PRIVATE}'''

    def __init__(self, environment, worksheet: str, workbook: dict, scenario=None, SiteGroup: str = None,
                 Filter: dict = None, VariableValues: dict = None, sync: bool = True, refresh: bool = True):
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
        '''if not isinstance(workbook, dict):
            raise TypeError("The parameter workbook type must be dict.")
        if not workbook:
            raise ValueError("The parameter workbook must not be empty.")
        wb_keys = workbook.keys()
        if len(wb_keys) != 2:
            raise ValueError("The parameter workbook must contain only Name and Scope.")
        if 'Name' not in wb_keys:
            raise ValueError("The parameter workbook must contain Name.")
        if 'Scope' not in wb_keys:
            raise ValueError("The parameter workbook must contain Scope.")'''
        self._parent_workbook = dict({"Name": workbook['Name'], "Scope": workbook['Scope']})

        self._sync = bool(sync)
        self._refresh = bool(refresh)

        # scenario
        if scenario:
            '''if not isinstance(scenario, dict):
                raise TypeError("The parameter scenario type must be dict.")
            scenario_keys = scenario.keys()
            if len(scenario_keys) != 2:
                raise ValueError("The parameter scenario must contain only Name and Scope.")
            if 'Name' not in scenario_keys:
                raise ValueError("The parameter scenario must contain Name.")
            if 'Scope' not in scenario_keys:
                raise ValueError("The parameter scenario must contain Scope.")'''
            self._scenario = dict({"Name": scenario['Name'], "Scope": scenario['Scope']})
        else:
            self._scenario = self.environment.scenarios[0]

        # sitegroup
        #if not isinstance(SiteGroup, str):
        #    raise TypeError("The parameter SiteGroup type must be str.")
        if not SiteGroup:
            # raise ValueError("The parameter SiteGroup must not be empty.")
            self._site_group = 'All Sites'
        else:
            self._site_group = str(SiteGroup)

        if not Filter:
            self._filter = dict({"Name": "All Parts", "Scope": SCOPE_PUBLIC})
        else:
            self._filter = Filter
        self._variable_values = VariableValues

        self.columns = list()
        self.rows = list()

        self._queryID = None
        self.total_row_count = 0

        if self._refresh:
            # self.RefreshData()
            self.RefreshData_async()

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

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, new_filter):
        '''if not isinstance(new_filter, dict):
            raise TypeError("filter must be dict.")
        if not new_filter:
            raise ValueError("filter must not be empty.")

        filt_keys = new_filter.keys()
        if len(filt_keys) != 2:
            raise ValueError("filter must contain only Name and Scope.")
        if 'Name' not in filt_keys:
            raise ValueError("filter must contain Name.")
        if 'Scope' not in filt_keys:
            raise ValueError("filter must contain Scope.")'''
        self._filter = dict({"Name": new_filter['Name'], "Scope": new_filter['Scope']})

    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, new_scenario):
        #if not isinstance(new_scenario, dict):
        #    raise TypeError("The parameter scenario type must be dict.")
        #scenario_keys = new_scenario.keys()
        #if len(scenario_keys) != 2:
        #    raise ValueError("The parameter scenario must contain only Name and Scope.")
        #if 'Name' not in scenario_keys:
        #    raise ValueError("The parameter scenario must contain Name.")
        #if 'Scope' not in scenario_keys:
        #    raise ValueError("The parameter scenario must contain Scope.")
        self._scenario = dict({"Name": new_scenario['Name'], "Scope": new_scenario['Scope']})

    @property
    def sync(self):
        return self._sync

    @property
    def site_group(self):
        return self._site_group

    @site_group.setter
    def site_group(self, new_site_group):
        self._site_group = str(new_site_group)

    def __len__(self):
        return len(self.rows)

    def __bool__(self):
        if len(self.rows) > 0:
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
        response = f'Worksheet: {self.name!r}, Scope: {self.parent_workbook_scope!r} \n'
        if len(self.rows) > 5:
            for i in range(0, 5):
                response = response + 'rownum: ' + str(i) + ' ' + str(self.rows[i]) + '\n'
            response = response + '...'
        return response

    def __setitem__(self, key, value):
        if not isinstance(value, WorksheetRow):
            self.rows[key] = WorksheetRow(value, self)
        else:
            self.rows[key] = value
        if self._sync:
            self.environment.refresh_auth()
            self.upload(self.rows[key])

    def add_row(self, rec):
        #s = requests.Session()
        self.environment.refresh_auth()
        self.upload(rec)

    def add_rows(self, rows: list):
        self.environment.refresh_auth()
        for i in range(0, len(rows), 500_000):
            self.upload(*rows)

    def append(self, values):
        # adds a single new item at the end of the underlying list
        if self._sync:
            self.add_row(values)

        if not isinstance(values, WorksheetRow):
            self.rows.append(WorksheetRow(values, self))
        else:
            self.rows.append(values)
        self.total_row_count = len(self.rows)

    def extend(self, *args):
        if self._sync:
            self.add_rows(*args)

        if isinstance(*args, type(WorksheetRow)):
            self.rows.extend(*args)
        else:
            self.rows.extend([WorksheetRow(item, self) for item in args[0]])
        self.total_row_count = len(self.rows)

    def _create_export(self, session):
        """
        :param session:
        :return: response_dict
        """
        #headers = self.environment.global_headers
        #headers['Content-Type'] = 'application/json'
        #url = self.environment.workbook_url

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

        req = requests.Request("POST", self.environment.workbook_url, headers=self.environment.global_headers, data=payload)
        prepped = req.prepare()
        response = session.send(prepped)

        # print(response.text)
        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            self._logger.error(payload)
            self._logger.error(self.environment.workbook_url)
            raise RequestsError(response,
                                f"failure during POST workbook initialise_for_extract to: {self.environment.global_headers}", payload)

        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == self.name:
                self._queryID = ws['QueryHandle']['QueryID']
                self.total_row_count = ws.get('TotalRowCount')
                self.columns = ws.get('Columns')
                #self.rows = ws.get('Rows')  # should be []
        return response_dict

    def _get_export_results(self, session, startRow: int = 0, pageSize: int = 5000):
        # add some checking for not null, blah. check pagesize is not insane
        """

        :param session:
        :param startRow:
        :param pageSize:
        :return: rows[]
        """
        #print(f'start: {startRow}, pagesize: {pageSize}')
        #headers = self.environment.global_headers
        #headers['Content-Type'] = 'application/json'
        url = self.environment.worksheet_url + "?queryId=" + self._queryID[1:] + "&workbookName=" + self.parent_workbook['Name'].replace('&', '%26').replace(' ','%20') + "&Scope=" + self.parent_workbook['Scope'] + "&worksheetName=" + self.name.replace('&', '%26').replace(' ','%20') + "&startRow=" + str(startRow) + "&pageSize=" + str(pageSize)

        req = requests.Request("GET", url, headers=self.environment.global_headers)
        prepped = req.prepare()
        response = session.send(prepped)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response,
                                f"failure during GET workbook retrieve_worksheet_data to: {url}", None)

        rows = [WorksheetRow(rec['Values'], self) for rec in response_dict["Rows"]]
        return rows

    def RefreshData(self, data_range: int = 5000):
        s = requests.Session()
        self.environment.refresh_auth()
        try:
            self._create_export(s)
        except TypeError:
            raise RequestsError(None, msg='likely due to invalid worksheetname')
        else:
            self.rows.clear()
            for i in range(0, self.total_row_count, data_range):
                self.rows.extend(self._get_export_results(s, i, data_range))
        finally:
            self._queryID = None
            s.close()

    async def _get_export_results_async(self, client, startRow: int = 0, pageSize: int = 5000):
        url = self.environment.worksheet_url + "?queryId=" + self._queryID[1:] + "&workbookName=" + self.parent_workbook['Name'].replace('&', '%26').replace(' ','%20') + "&Scope=" + self.parent_workbook['Scope'] + "&worksheetName=" + self.name.replace('&', '%26').replace(' ','%20') + "&startRow=" + str(startRow) + "&pageSize=" + str(pageSize)
        #print(f'start: {startRow}, pagesize: {pageSize}')
        #headers = self.environment.global_headers

        response = await client.get(url=url, headers=self.environment.global_headers)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during GET to: {url}", None)
        rows = [WorksheetRow(rec['Values'], self) for rec in response_dict["Rows"]]
        return rows

    async def _main_get_export_results_async(self, data_range):

        client = httpx.AsyncClient()
        #for i in range(0, self._total_row_count - data_range, data_range):
        #    print(f'i: {i}, range: {data_range}, time: {datetime.now()}')
        #    tasks.append(asyncio.Task(self._get_export_results_async(client, i, data_range)))
        tasks = [asyncio.Task(self._get_export_results_async(client, i, data_range)) for i in range(0, self.total_row_count - data_range, data_range)]
        for coroutine in asyncio.as_completed(tasks):
            self.rows.extend(await coroutine)

        remaining_records = self.total_row_count % data_range
        if remaining_records > 0:
            await asyncio.sleep(1)
            self.rows.extend(await self._get_export_results_async(client, self.total_row_count - remaining_records, data_range))
        await client.aclose()

    def RefreshData_async(self, data_range: int = 5000):

        self.environment.refresh_auth()
        # initialise_for_extract query
        s = requests.Session()
        try:
            self._create_export(s)
            s.close()
        except TypeError:
            raise RequestsError(None, msg='likely due to invalid worksheetname')
        else:
            self.rows.clear()
            asyncio.run(self._main_get_export_results_async(data_range))
        finally:
            self._queryID = None
            #s.close()

    def upload(self, *args):
        """
        Sending the request imports the data specified in the Rows field using the worksheet's import rules

        :param args: list [] of records you want to send. don't just send a single record!! i.e. [0,0]
        :return: results from request
        """
        #headers = self.environment.global_headers
        #headers['Content-Type'] = 'application/json'
        #url = self.environment.workbook_import

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

        payload = json.dumps({
            'Scenario': self._scenario,
            'WorkbookParameters': workbook_parameters,
            'Rows': rows
        })

        response = requests.request("POST", self.environment.workbook_import_url,
                                    headers=self.environment.global_headers, data=payload)
        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            #self._logger.error(payload)
            raise RequestsError(response,
                                f"failure during workbook-worksheet upload, POST to: {self.environment.global_headers}", payload)

        results = response_dict['Worksheets'][0]  # this only supports single worksheet, so no idea why it's an array.
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
            raise RequestsError(response,
                                f"partial failure during worksheet upload. ErrorCount: {results['ErrorRowCount']}, {self.environment.workbook_import_url}",
                                payload)
        else:
            self._logger.error(response_readable)
            self._logger.error(response_dict)
            self._logger.error(payload)
            raise RequestsError(response, f"failure during worksheet upload", payload)
        return results


class WorksheetRow(UserList):
    def __init__(self, iterable, worksheet: Worksheet):
        # initialises a new instance WorksheetRow(['GP', '0', '7000vE', '2017-08-31'], WorksheetName)
        self._logger = logging.getLogger('RapidPy.wb.wsr')
        if not isinstance(worksheet, Worksheet):
            raise TypeError("The parameter worksheet type must be Worksheet.")
        # grab the necessary info from owning table
        self._worksheet = worksheet

        if len(iterable) != len(self._worksheet.columns):
            raise DataError(str(iterable), 'mismatch in length of worksheet columns: ' + str(len(self._worksheet.columns)) + ' and row: ' + str(len(iterable)))

        super().__init__(str(item) for item in iterable)
        '''to_init = []
        for x in range(len(iterable)):
            to_init.append(Cell(iterable[x], self._worksheet.columns[x]["DataType"], self._worksheet.columns[x]["Id"],self._worksheet.columns[x]["Header"],self._worksheet.columns[x]["IsEditable"]))
        super().__init__(to_init)'''

    def __getattr__(self, name):
        # method only called as fallback when no named attribute
        cls = type(self)
        try:
            Ids = [i['Id'] for i in self.columns]
            pos = Ids.index(name)
        except ValueError: # this is thrown if you could not find name
            pos = -1
        if 0 <= pos < len(self.columns):
            return self[pos]
        msg = f'{cls.__name__!r} object has no attribute {name!r}'
        raise AttributeError(msg)

    '''def __setattr__(self, name, value):
        cls = type(self)

        if name in self.__dict__:
            super().__setattr__(name, value)
            return 0
        Ids = [i['Id'] for i in self.columns]
        if name in Ids:
            pos = Ids.index(name)
            self.__setitem__(pos, value)
        else:
            error = ''
        if error:
            msg = error.format(cls_name=cls.__name__, attr_name=name)
            raise AttributeError(msg)'''

    def __len__(self):
        return super().__len__()

    def __getitem__(self, position):
        return super().__getitem__(position)

    @property
    def columns(self):
        return self._worksheet.columns

    #def __setitem__(self, index, item):
        # assign a new value using the item’s index, like a_list[index] = item
        # super().__setitem__(index, str(item))
        #raise NotImplementedError
    def __setitem__(self, index, item):
        # assign a new value using the item’s index, like a_list[index] = item

        # when something is updated it should be pushed back to RR, if datatable is sync
        super().__setitem__(index, str(item))
        if self._worksheet.sync:
            to_send = list(self)
            '''types = [item['DataType'] for item in self.columns]
            for i in range(len(types)):
                if types[i] == 'Date':
                    if to_send[i] == 'Undefined':
                        to_send[i] = ''
                    elif to_send[i] == 'Future':
                        to_send[i] = '31-12-99'
                    elif to_send[i] == 'Past':
                        to_send[i] = '01-01-70'
                    elif to_send[i] == 'Today':
                        today = date.today()
                        formatted_today = today.strftime("%d-%m-%y")
                        to_send[i] = formatted_today
                    else:
                        print(to_send[i])
                        pattern = r"\b(19\d\d|20\d\d)[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b"  # YYYY-MM-DD
                        dates = re.findall(pattern, to_send[i])
                        to_send[i] = f"{dates[0][2]}-{dates[0][1]}-{dates[0][0][2:]}"  # '07-06-20'''''
            self._worksheet.add_row(to_send)


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


class Cell:
    def __init__(self, value, datatype, columnId, header, isEditable):
        self.value = str(value)
        self.datatype = str(datatype)
        self.columnId = str(columnId)
        self.header = str(header)
        self.isEditable = bool(isEditable)

    def __bool__(self):
        return bool(self._value)

    def __repr__(self):
        return f'Cell(value={self._value!r}, datatype={self.datatype!r}, columnId={self.columnId!r}, header={self.header!r}, isEditable={self.isEditable!r}) '

    def __str__(self):
        return self.value

    @property
    def value(self):
        if self.datatype == 'Date':
            if self._value == 'Undefined':
                return ''
            elif self._value == 'Future':
                return '31-12-99'
            elif self._value == 'Past':
                return '01-01-70'
            elif self._value == 'Today':
                today = date.today()
                formatted_today = today.strftime("%d-%m-%y")
                return formatted_today
            else:
                pattern = r"\b(19\d\d|20\d\d)[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b"  # YYYY-MM-DD
                dates = re.findall(pattern, self._value)
                return f"{dates[0][2]}-{dates[0][1]}-{dates[0][0][2:]}"  # '07-06-20'

            #return self.value # format needs to be '07-06-20'
        else:
            return self._value

    @value.setter
    def value(self, value):
        if self.isEditable:
            self._value = str(value)
        else:
            pass