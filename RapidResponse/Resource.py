import abc
import asyncio
import json
import logging
import re
from abc import abstractmethod
from collections import UserList
from datetime import date

import httpx
import requests
from requests import Session, Request, HTTPError

from RapidResponse.Environment import Environment
from RapidResponse.Utils import VALID_SCOPES, SCOPE_PUBLIC, ScriptError, RequestsError, ALL_SITES, ALL_PARTS, DataError


class Resource(abc.ABC):
    def __init__(self, environment, name, scope: str = None):

        self._validate_parameters(environment, name)

        self._environment = environment
        self._name = name
        self._sanitized_name = self._sanitize_input(name)
        self._scope = scope if scope in VALID_SCOPES else SCOPE_PUBLIC

        self._logger = logging.getLogger('RapidPy.rcs')
        self._logger.setLevel(logging.DEBUG)
        self._logger.debug('Resource')
        self._logger.debug('environment: %s', self._environment)
        self._logger.debug('name: %s', self._name)

    @staticmethod
    def _validate_parameters(environment, name):
        if not isinstance(environment, Environment):
            raise TypeError("The parameter environment type must be Environment.")
        if not environment:
            raise ValueError("The parameter environment must not be empty.")
        if not isinstance(name, str):
            raise TypeError("The parameter name type must be str.")
        if not name:
            raise ValueError("The parameter name must not be empty.")

    @staticmethod
    def _sanitize_input(to_sanitize: str):
        if to_sanitize is None:
            return ''
        else:
            return to_sanitize.replace('&', '%26').replace(' ', '%20')

    @property
    def environment(self):
        return self._environment

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self._sanitized_name = self._sanitize_input(new_name)

    @property
    def qualified_name(self):
        return dict(Name=self.name, Scope=self.scope)

    @property
    def scope(self):
        return self._scope

    @scope.setter
    def scope(self, new_scope: str) -> None:
        if new_scope not in VALID_SCOPES:
            raise ValueError("The scope must be either 'Public' or 'Private'.")
        self._scope = new_scope

    @abstractmethod
    def status(self):
        """
        Representation of the load status for the resource

        :return: string containing the status, Success, Unknown, Not Run, or the actual error message.
        """
        pass

class WorkbookResource(Resource,abc.ABC):
    def __init__(self, environment, name, scope, Scenario: dict = None, SiteGroup: str = None, Filter: dict = None, VariableValues: dict = None):
        Resource.__init__(self,environment, name, scope)

        self.fetch_variables_from_mx = False
        self._scenario = dict()
        self._workbook = dict()
        self._site_group = None
        self._filter = None
        self._variable_values = None
        self._logger = logging.getLogger('RapidPy.rcs.wb')


        if Scenario:
            self._scenario = dict(Name=Scenario['Name'], Scope=Scenario['Scope'])
        else:
            self._scenario = self.environment.scenarios[0]

        if not SiteGroup:
            self._site_group = ALL_SITES
        else:
            self._site_group = str(SiteGroup)

        # set Filter
        if not Filter:
            self._filter = ALL_PARTS
        else:
            self._filter = dict(Name=Filter['Name'], Scope=Filter['Scope'])


    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, new_scenario):
        if new_scenario['Scope'] in VALID_SCOPES:
            self._scenario = dict(Name=new_scenario['Name'], Scope=new_scenario['Scope'])
        else:
            raise ValueError(f'Invalid scope: {new_scenario["Scope"]}. Valid scopes are: {VALID_SCOPES}')

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, new_filter):
        if new_filter['Scope'] in VALID_SCOPES:
            self._filter = dict(Name=new_filter['Name'], Scope=new_filter['Scope'])
        else:
            raise ValueError(f'Invalid scope: {new_filter["Scope"]}. Valid scopes are: {VALID_SCOPES}')

    @property
    def site_group(self):
        return self._site_group

    @site_group.setter
    def site_group(self, new_site_group):
        self._site_group = str(new_site_group)

class AbstractScript(Resource,abc.ABC):
    """
    A class to represent and execute a script within a RapidResponse environment. This loosely follows the Command design pattern (GOF).

    :param environment: RapidResponse environment for which the script is scoped. Mandatory.
    :param name: string, name of script. Mandatory.
    :param scope: enumerated, 'Public' or 'Private'. Optional, default is 'Public'
    :param parameters: dictionary containing the parameters. Optional.
    :raises ScriptError: If there is an error in the script execution.
    :raises RequestsError: If there is an error with the HTTP request.
    :raises ValueError: If the environment or name parameters are invalid.
    :raises TypeError: If the type of the environment or name parameters are incorrect.
    """

    def __init__(self, environment: Environment, name: str, scope: str = None, parameters: dict = None):
        Resource.__init__(self, environment, name, scope)
        self._logger = logging.getLogger('RapidPy.spt')

        self._parameters = dict(parameters) if parameters is not None else {}

        self._response = {'console': '', 'value': '', 'error': ''}
        self._internal_status = 0  # 0=not run, -1=error, 1=success

        self._session = Session()

    @property
    def console(self) -> str:
        return self._response['console']

    @property
    def value(self) -> str:
        return self._response['value']

    @property
    def status(self) -> str:
        if self._response['error']:
            error = self._response['error']
            return f"Error: Code {error['Code']}\nMessage {error['Message']}\n\nSee log for details"
        if self._internal_status == 0:
            return "Not Run"
        if self._internal_status == 1:
            return "Success"
        return "Unknown"

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, new_params):
        self._parameters = dict(new_params)

    def __str__(self) -> str:
        return f"Script(name={self._name}, scope={self._scope}, status={self.status}, parameters={self._parameters})"

    def __repr__(self) -> str:
        return (f"Script(environment={repr(self._environment)}, name={self._name}, "
                f"scope={self._scope}, parameters={self._parameters})")

    def __eq__(self, other) -> bool:
        if not issubclass(other, AbstractScript):
            return NotImplemented
        return (self.environment == other.environment and
                self._name == other.name and
                self._scope == other.scope and
                self._parameters == other.parameters)

    def __hash__(self):
        return hash((self._environment, self._name, self._scope, frozenset(self._parameters.items())))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self._session.close()

    @abstractmethod
    def execute(self):
        pass

class Script(AbstractScript):
    """
    A class to represent and execute a script within a RapidResponse environment. This loosely follows the Command design pattern (GOF).

    :param environment: RapidResponse environment for which the script is scoped. Mandatory.
    :param name: string, name of script. Mandatory.
    :param scope: listed, 'Public' or 'Private'. Optional, default is the 'Public'
    :param parameters: dictionary containing the parameters. Optional.
    :raises ScriptError: If there is an error in the script execution.
    :raises RequestsError: If there is an error with the HTTP request.
    :raises ValueError: If the environment or name parameters are invalid.
    :raises TypeError: If the type of the environment or name parameters are incorrect.
    """

    def __init__(self, environment: Environment, name: str, scope: str = None, parameters: dict = None):
        AbstractScript.__init__(self,environment, name, scope, parameters)

        self._session.headers.update(self.environment.global_headers)

    def execute(self, sync=True):
        """
        Executes the script. Currently, supports only synchronous execution.

        :param sync: Boolean flag indicating synchronous execution. Default is True.
        :raises ScriptError: If there is an error in the script execution.
        :raises RequestsError: If there is an error with the HTTP request.
        """
        self._logger.debug(f"Executing script {self._name} with scope {self._scope} and parameters {self._parameters}")
        try:
            response_dict = self._send_execute_script(self._session)
            self._process_execute_response(response_dict)
            self._internal_status = 1
        except ScriptError as e:
            self._internal_status = -1
            self._logger.error(f"Script execution failed: {e}")
        except RequestsError as e:
            self._internal_status = -1
            self._logger.error(f"Script execution failed: {e}")
            raise
        finally:
            self.close()

    def _send_execute_script(self, session):
        """

        :rtype: JSON
        :param session:
        :raises RequestsError:
        """
        self._reset_response_state()

        payload = json.dumps(self._parameters)
        url = f'{self.environment.script_url}/{self.scope}/{self._sanitized_name}'
        self._logger.debug(f"Sending POST request to {url} with payload {payload}")

        req = Request('POST', url, headers=session.headers, data=payload)
        prepped = req.prepare()
        response = None
        try:
            response = session.send(prepped)
            response.raise_for_status()  # Will raise HTTPError for bad responses
            return response.json()
        except HTTPError as e:
            raise RequestsError(response, f"HTTP error during POST to: {url}", payload) from e

    def _reset_response_state(self):
        """
        blanks the internally stored response values before execution

        """
        self._internal_status = -1
        self._response.update({'console': '', 'value': '', 'error': ''})

    def _process_execute_response(self, response_dict: dict):
        """
        takes the response from execution and handles if there were issues raised in response, or if success

        :param response_dict: expected elements are console, value, and if applicable, ScriptError
        :raises ScriptError:
        """
        self._response.update({
            'console': response_dict.get('Console'),
            'value': response_dict.get('Value')
        })

        if 'ScriptError' in response_dict:
            error = response_dict['ScriptError']
            self._response.update({'error': error})
            raise ScriptError(
                error['Code'], error['Message'], error['Console'], error['ScriptName'],
                error['ScriptScope'], error['Line'], error['Character']
            )

class AbstractWorkBook(WorkbookResource,abc.ABC):
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

    def __init__(self, environment, workbook, Scenario, SiteGroup, WorksheetNames, Filter, VariableValues):
        """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?

        :param environment: Required. contains the env details for worksheet.
        :param workbook : Required, The workbook the required data is in. Example,{"Name": 'workbookname', "Scope": 'Public'}
        :param Scenario : Optional {"Name": "Integration", "Scope": "Public"}
        :param SiteGroup : Optional, the site or site filter to use with the workbook Example, "All Sites"
        :param WorksheetNames : Optional, the worksheets you want to retrieve data from ["worksheet name1", "worksheet name2"]
        :param Filter : Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues : Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}


        """
        WorkbookResource.__init__(self,environment, workbook['Name'], workbook['Scope'],Scenario, SiteGroup, Filter, VariableValues)

        self._logger = logging.getLogger('RapidPy.rcs.wb')
        self.worksheets = list()
        self._workbook =  dict(Name=workbook['Name'], Scope=workbook['Scope'])

        # set script params
        if self.environment._worksheet_script is None:
            self.fetch_worksheets_from_mx = False
        else:
            self.fetch_worksheets_from_mx = True

    def __repr__(self):
        return f'Workbook({self.environment!r}, {self.name!r}, {self.scenario!r}, {self.site_group!r}, {self.worksheets!r}, {self.filter!r}, {self._variable_values!r})'

    def __str__(self):
        return f'Name: {self.name!r}, Scope: {self.workbook_scope!r}'

    def __len__(self):
        return len(self.worksheets)

    def __getitem__(self, position):
        return self.worksheets[position]

    def indexof(self, rec):
        return self.worksheets.index(rec)

    def __contains__(self, item):
        if item in self.worksheets:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False

    def __getattr__(self, name):
        # method only called as fallback when no named attribute
        cls = type(self)
        try:
            Ids = [i.name for i in self.worksheets]
            pos = Ids.index(name.replace('_', ' '))
        except ValueError:  # exception thrown if could not find name
            pos = -1
        if 0 <= pos < len(self.worksheets):
            return self[pos]
        msg = f'{cls.__name__!r} object has no attribute {name!r}'
        raise AttributeError(msg)

    @abc.abstractmethod
    def RefreshData(self):
        # populate all child worksheets with data
        pass

    @WorkbookResource.scenario.setter
    def scenario(self, new_scenario):
        #self._scenario = super().scenario(new_scenario) #dict(Name=new_scenario['Name'], Scope=new_scenario['Scope'])
        super(__class__, type(self)).scenario.fset(self, new_scenario)
        for ws in self.worksheets:
            ws.scenario = self.scenario


    @WorkbookResource.site_group.setter
    def site_group(self, new_site_group):
        super(__class__, type(self)).site_group.fset(self, new_site_group)
        #self._site_group = super().site_group.setter(new_site_group)
        for ws in self.worksheets:
            ws.site_group = self.site_group

    @property
    def status(self) -> str:
        return f'{[(ws.name, ws.status,) for ws in self.worksheets]}'

class Workbook(AbstractWorkBook):
    """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?\n
        :param environment: Required. contains the env details for worksheet.
        :param workbook : Required, The workbook the required data is in. Example,{"Name": 'workbookname', "Scope": 'Public'}
        :param Scenario : Optional {"Name": "Integration", "Scope": "Public"}
        :param SiteGroup : Optional, the site or site filter to use with the workbook Example, "All Sites"
        :param WorksheetNames : Optional, the worksheets you want to retrieve data from ["worksheet name1", "worksheet name2"]
        :param Filter : Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues : Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}
    """

    def __init__(self, environment, workbook: dict, Scenario: dict = None, SiteGroup: str = None,
                 WorksheetNames: list = None, Filter: dict = None, VariableValues: dict = None, refresh: bool = True):
        """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?

        :param environment: Required. contains the env details for worksheet.
        :param workbook : Required, The workbook the required data is in. Example,{"Name": 'workbookname', "Scope": 'Public'}
        :param Scenario : Optional {"Name": "Integration", "Scope": "Public"}
        :param SiteGroup : Optional, the site or site filter to use with the workbook Example, "All Sites"
        :param WorksheetNames : Optional, the worksheets you want to retrieve data from ["worksheet name1", "worksheet name2"]
        :param Filter : Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues : Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}


        """
        AbstractWorkBook.__init__(self, environment, workbook, Scenario, SiteGroup, WorksheetNames, Filter, VariableValues)
        self._refresh = refresh

        if WorksheetNames:
            self._set_worksheets(WorksheetNames)
        elif self.fetch_worksheets_from_mx:
            self._logger.debug(
                f'Attempting to fetch worksheets from Maestro using {self.environment._worksheet_script}')
            self._set_worksheets(self._fetch_worksheets(self.environment._worksheet_script))
        else:
            raise ValueError('worksheets are required')

        if self.environment._variables_script is None:
            self.fetch_variables_from_mx = False
        else:
            self.fetch_variables_from_mx = True

        if VariableValues:
            self._variable_values = dict(VariableValues)
        elif self.fetch_variables_from_mx:
            self._logger.debug(f'Fetching variables from Maestro using {self.environment._variables_script}')
            self._variable_values = self._fetch_variables(self.environment._variables_script)
        else:
            self._logger.debug(f'Variables might be required, who really knows?! Guess we see if it gives error later')

    def RefreshData(self):
        # populate all child worksheets with data
        for ws in self.worksheets:
            try:
                ws.RefreshData()
            except:
                self._logger.error(f'something went wrong with {ws.name}')
                raise

    def _set_worksheets(self, list_of_worksheets):
        self.worksheets = [
            Worksheet(self.environment, name, self._workbook, self._scenario, self._site_group, self._filter,
                      self._variable_values, refresh=self._refresh) for name in list_of_worksheets]

    def _fetch_worksheets(self, helper_workbook):
        param = {"SharedWorkbookName": self.name, "IsIncludeHiddenWorksheet": False, "loggingLevel": "2"}
        worksheetsResponse = Script(self.environment, helper_workbook, scope='Public', parameters=param)
        worksheetsResponse.execute()
        worksheets = worksheetsResponse.value.replace('"', '')
        worksheetarray = worksheets.split(', ')
        self._logger.debug(f'{worksheetarray}')
        return worksheetarray

    def _fetch_variables(self, helper_workbook):
        param = {"SharedWorkbookName": self.name, "IsIncludeHiddenWorksheet": False, "loggingLevel": "2"}
        variablesResponse = Script(self.environment, helper_workbook, scope=SCOPE_PUBLIC, parameters=param)
        variablesResponse.execute()
        var_list = json.loads('[' + variablesResponse.value + ']')
        variables_dict = dict()
        for var in var_list:
            variables_dict.update({var["name"]: var["defaultValue"]})
        return variables_dict

class Worksheet(WorkbookResource):
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
    # todo work out what is broken with extend or append in worksheet
    DEFAULT_PAGESIZE = 5000

    def __init__(self, environment, worksheet: str, workbook: dict, scenario=None, SiteGroup: str = None,
                 Filter: dict = None, VariableValues: dict = None, sync: bool = True, refresh: bool = True):
        """
        https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/retrieve_workbook_rest.htm?

        :param scenario:
        :param environment: Required. contains the env details for worksheet.
        :param worksheet: Required, the worksheets you want to retrieve data from. Example, DataModel_Summary
        :param workbook: Required, The workbook the required data is in. Example, {'Name': 'KXSHelperREST', "Scope": 'Public'}
        :param SiteGroup: Optional, the site or site filter to use with the workbook Example, "All Sites"
        :param Filter: Optional,the filter to apply to the workbook, defined as an object that contains the filter name and scope {"Name": "All Parts", "Scope": "Public"}
        :param VariableValues: Required if WS has them. keyvalue pairs {"DataModel_IsHidden": "No", "DataModel_IsReadOnly": "All"}
        """
        WorkbookResource.__init__(self, environment, worksheet, workbook['Scope'], scenario, SiteGroup, Filter, VariableValues)
        self._logger = logging.getLogger('RapidPy.ws')

        self._name = str(worksheet)

        # workbook
        self._parent_workbook = dict({"Name": workbook['Name'], "Scope": workbook['Scope']})
        self._sync = bool(sync)
        self._refresh = bool(refresh)
        self._variable_values = VariableValues

        self._export_status = None
        self._upload_status = None
        self.columns = list()
        self._rows = list()
        self._queryID = None
        self.total_row_count = 0
        timeout = httpx.Timeout(10.0, connect=60.0)
        self.client = httpx.AsyncClient(timeout=timeout)
        self.max_connections = 10

        if self._refresh: self.RefreshData()
            #self.RefreshData_async()

    @property
    def status(self):
        if self._upload_status:
            if not self._upload_status['Success']:
                error = self._upload_status['Errors']
                return f"Error: Code {error['Code']}\nMessage {error['Message']}\n\nSee log for details"
            else:
                return f'Success'
        elif self._export_status:
            return f'Success'
        else:
            return f'Not Run'

    @property
    def parent_workbook(self):
        return self._parent_workbook

    @property
    def parent_workbook_name(self):
        return self._parent_workbook['Name']

    @property
    def parent_workbook_scope(self):
        return self._parent_workbook['Scope']

    @WorkbookResource.filter.setter
    def filter(self, new_filter):
        WorkbookResource.filter.fset(self, new_filter)
        if self._refresh: self.RefreshData()

    @WorkbookResource.scenario.setter
    def scenario(self, new_scenario):
        WorkbookResource.scenario.fset(self, new_scenario)
        if self._refresh: self.RefreshData()

    @property
    def sync(self):
        return self._sync

    @WorkbookResource.site_group.setter
    def site_group(self, new_site_group):
        WorkbookResource.site_group.fset(self, new_site_group)
        if self._refresh: self.RefreshData()

    def __len__(self):
        return len(self._rows)

    def __bool__(self):
        if len(self._rows) > 0:
            return True
        else:
            return False

    def __getitem__(self, position):
        return self._rows[position]

    def __eq__(self, other):
        if self.name == other.name and self.parent_workbook == other.parent_workbook:
            return True
        else:
            return False

    def __contains__(self, item):
        if item in self._rows:
            return True
        else:
            return False

    def __repr__(self):
        return f'Worksheet(environment={self.environment!r},worksheet={self.name!r},workbook={self.parent_workbook!r},SiteGroup={self._site_group!r},Filter={self._filter!r},VariableValues={self._variable_values!r}) '

    def __str__(self):
        # return self and first 5 rows
        response = f'Worksheet: {self.name!r}, Scope: {self.parent_workbook_scope!r} '
        if len(self._rows) > 0:
            response = response + '\n'
        if len(self._rows) > 5:
            for i in range(0, 5):
                response = response + 'rownum: ' + str(i) + ' ' + str(self._rows[i]) + '\n'
            response = response + '...'
        return response

    def __setitem__(self, key, value):
        if not isinstance(value, WorksheetRow):
            self._rows[key] = WorksheetRow(value, self)
        else:
            self._rows[key] = value
        if self._sync:
            self.environment.refresh_auth()
            self.upload(self._rows[key])

    def add_row(self, rec):
        #s = requests.Session()
        self.environment.refresh_auth()
        self.upload(rec)

    def add_rows(self, rows: list):
        self.environment.refresh_auth()
        for i in range(0, len(rows), 500_000):
            self.upload(*rows)

    def append(self, values):
        """
        Adds a single new item to the end of the underlying list.

        :param values: A single item or an instance of WorksheetRow to be added.
        :type values: Any
        :return: None
        """
        if self._sync:
            self.add_row(values)

        if not isinstance(values, WorksheetRow):
            self._rows.append(WorksheetRow(values, self))
        else:
            self._rows.append(values)
        self.total_row_count = len(self._rows)

    def extend(self, *args):
        if self._sync:
            self.add_rows(*args)

        if isinstance(*args, type(WorksheetRow)):
            self._rows.extend(*args)
        else:
            self._rows.extend([WorksheetRow(item, self) for item in args[0]])
        self.total_row_count = len(self._rows)

    def _prepare_export_params(self):
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
        return workbook_parameters

    def _process_create_export_response(self, response_dict):
        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == self.name:
                self._queryID = ws['QueryHandle']['QueryID']
                self.total_row_count = ws.get('TotalRowCount')
                self.columns = ws.get('Columns')
                # self.rows = ws.get('Rows')  # should be []
                self._export_status = ws

    def _create_export(self, session):
        """
        :param session:
        :return: response_dict
        """

        workbook_parameters = self._prepare_export_params()

        payload = json.dumps({
            'Scenario': self._scenario,
            'WorkbookParameters': workbook_parameters
        })

        req = requests.Request("POST", self.environment.workbook_url, headers=self.environment.global_headers, data=payload)
        prepped = req.prepare()
        response = session.send(prepped)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response,
                                f"failure during POST workbook initialise_for_extract to: {self.environment.global_headers}",
                                payload)

        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == self.name:
                self._queryID = ws['QueryHandle']['QueryID']
                self.total_row_count = ws.get('TotalRowCount')
                self.columns = ws.get('Columns')
                #self.rows = ws.get('Rows')  # should be []
                self._export_status = ws
        return response_dict

    def _get_export_results(self, session, startRow: int = 0, pageSize: int = DEFAULT_PAGESIZE):
        # add some checking for not null, blah. check pagesize is not insane
        """

        :param session:
        :param startRow:
        :param pageSize:
        :return: rows[]
        """
        self._logger.debug(f'_get_export_results start: {startRow}, pagesize: {pageSize}')

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

    def RefreshData(self, data_range: int = DEFAULT_PAGESIZE):
        s = requests.Session()
        self.environment.refresh_auth()
        try:
            self._create_export(s)
        except TypeError:
            raise RequestsError(None, msg='LIKELY due to invalid worksheetname')
        else:
            self._rows.clear()
            for i in range(0, self.total_row_count, data_range):
                self._rows.extend(self._get_export_results(s, i, data_range))
        finally:
            self._queryID = None
            s.close()

    async def _create_export_async(self, client, limit: asyncio.Semaphore = None):
        """
                :param client:
                :param limit:
                :return: response_dict
                """

        workbook_parameters = self._prepare_export_params()

        payload = json.dumps({
            'Scenario': self._scenario,
            'WorkbookParameters': workbook_parameters
        })

        try:
            async with limit:
                response = await client.post(url=self.environment.workbook_url, headers=self.environment.global_headers,
                                             content=payload)
        except:
            raise RequestsError(response,
                                f"failure during POST workbook _create_export_async to: {self.environment.workbook_url}",
                                payload)
        else:
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                self._process_create_export_response(response_dict)
                return response_dict
            else:
                raise RequestsError(response,
                                    f"failure during POST workbook _create_export_async to: {self.environment.global_headers}",
                                    payload)

    async def _get_export_results_async(self, client, startRow: int = 0, pageSize: int = DEFAULT_PAGESIZE):
        url = self.environment.worksheet_url + "?queryId=" + self._queryID[1:] + "&workbookName=" + self.parent_workbook['Name'].replace('&', '%26').replace(' ','%20') + "&Scope=" + self.parent_workbook['Scope'] + "&worksheetName=" + self.name.replace('&', '%26').replace(' ','%20') + "&startRow=" + str(startRow) + "&pageSize=" + str(pageSize)
        self._logger.debug(f'_get_export_results start: {startRow}, pagesize: {pageSize}')

        response = await client.get(url=url, headers=self.environment.global_headers)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during GET to: {url}", None)
        rows = [WorksheetRow(rec['Values'], self) for rec in response_dict["Rows"]]
        return rows

    async def _main_get_export_results_async(self, data_range):

        limit = asyncio.Semaphore(self.max_connections)
        # set exportID and totrowcount
        response_dict = await self._create_export_async(self.client, limit)
        self._process_create_export_response(response_dict)

        tasks = [asyncio.Task(self._get_export_results_async(self.client, i, data_range)) for i in
                 range(0, self.total_row_count - data_range, data_range)]
        for coroutine in asyncio.as_completed(tasks):
            self._rows.extend(await coroutine)

        remaining_records = self.total_row_count % data_range
        if remaining_records > 0:
            self._rows.extend(
                await self._get_export_results_async(self.client, self.total_row_count - remaining_records, data_range))
        await self.client.aclose()

    def _calc_optimal_pagesize(self, pagesize):

        return self.DEFAULT_PAGESIZE

    def RefreshData_async(self, data_range: int = None):
        # todo get this to work. then modify environment to create event loop and take sessions from there.
        calc_data_range = self._calc_optimal_pagesize(data_range)

        self.environment.refresh_auth()
        # initialise_for_extract query
        self._rows.clear()
        asyncio.run(self._main_get_export_results_async(calc_data_range))
        self._queryID = None


    def _prepare_upload_params(self):
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
        return workbook_parameters

    def upload(self, *args):
        """
        Sending the request imports the data specified in the Rows field using the worksheet's import rules

        :param args: list [] of records you want to send. don't just send a single record!! i.e. [0,0]
        :return: results from request
        """
        #headers = self.environment.global_headers
        #headers['Content-Type'] = 'application/json'
        #url = self.environment.workbook_import

        workbook_parameters = self._prepare_upload_params()

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
                                f"failure during workbook-worksheet upload. Non-200 response, POST to: {self.environment.global_headers}",
                                payload)

        results = response_dict['Worksheets'][0]  # this only supports single worksheet, so no idea why it's an array.
        self._upload_status = response_dict
        response_readable = self._format_response(results)

        if response_dict['Success'] and results['ErrorRowCount'] <= 0:
            self._logger.info(response_readable)
        elif response_dict['Success'] and results['ErrorRowCount'] > 0:
            self._logger.warning(response_readable)
            raise RequestsError(response,
                                f"partial failure during worksheet upload. ErrorCount: {results['ErrorRowCount']}, {self.environment.workbook_import_url}",payload)
        else:
            self._logger.error(response_dict)
            raise RequestsError(response, f"failure during worksheet upload", payload)
        return results

    def _format_response(self, response_dict):
        """
        Formats a dictionary containing webservice call operation results into a human-readable string.

        Args:
            response_dict (dict): A dictionary with a 'Results' key, where the value
                                  is a dictionary containing webservice call operation counts.

        Returns:
            str: A formatted string showing the status and row counts of the operation.
        """
        response_readable = (
            f"status: {response_dict.get('Status', 'N/A')}\n"
            f"ImportedRowCount: {response_dict.get('ImportedRowCount', 'N/A')}\n"
            f"InsertedRowCount: {response_dict.get('InsertedRowCount', 'N/A')}\n"
            f"ModifiedRowCount: {response_dict.get('ModifiedRowCount', 'N/A')}\n"
            f"DeleteRowCount: {response_dict.get('DeleteRowCount', 'N/A')}\n"
            f"ErrorRowCount: {response_dict.get('ErrorRowCount', 'N/A')}\n"
            f"Errors: {response_dict.get('Errors', 'N/A')}\n"
            f"UnchangedRowCount: {response_dict.get('UnchangedRowCount', 'N/A')}"
        )
        self._logger.info(response_readable)
        return response_readable

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

    def __len__(self):
        return super().__len__()

    def __getitem__(self, position):
        return super().__getitem__(position)

    @property
    def columns(self):
        return self._worksheet.columns

    def __setitem__(self, index, item):
        # assign a new value using the item’s index, like a_list[index] = item

        # when something is updated it should be pushed back to RR, if datatable is sync
        super().__setitem__(index, str(item))
        if self._worksheet.sync:
            to_send = list(self)
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
        """
        calls func() on every item in the underlying list to generate some side effect.
        :param func:
        """
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
