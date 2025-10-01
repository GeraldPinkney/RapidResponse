import abc
import asyncio
import base64
import json
import logging
import os

import httpx
import requests

from RapidResponse.DataModel import DataModel
from RapidResponse.Utils import WORKBOOK_URL, BULK_URL, WORKSHEET_URL, SCRIPT_URL, ENTERPRISE_DATA_SCENARIO, SetupError, \
    RequestsError


class BaseEnvironment(abc.ABC):
    """
        this is the python representation of your environment. It contains authentication details, data model data (tables, fields, etc) and provides the scoping for working with RR.\n
        :param configuration: dictionary containing necessary information for initialising environment
        :raises SetupError: Data Model directory not valid
        """

    def __init__(self, configuration: dict):


        logging.basicConfig(filename='logging.log', filemode='w',
                            format='%(name)s - %(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
        self._logger = logging.getLogger('RapidPy.env')

        self._base_url = None
        self.auth_type = None
        self.authentication = dict()
        self.global_headers = dict()
        self._data_model_dir = None
        self.data_model = None
        self.scenarios = None
        self._maxconnections = None
        self._session = None
        self._variables_script = None
        self._worksheet_script = None
        self.client = None


        if not isinstance(configuration, dict):
            raise TypeError('The parameter configuration type must be dict')
        if not configuration:
            raise ValueError('The parameter configuration must be provided')

        self.global_headers['Content-Type'] = 'application/json'

    def __repr__(self):
        return f'Environment(url={self.base_url!r}, data_model_directory={self._data_model_dir!r}, auth_type={self.auth_type!r})'

    def __str__(self):
        return f'Environment(url={self.base_url!r})'

    def __contains__(self, item):
        return item in self.data_model

    def __enter__(self):
        return self

    def close(self):
        self._session.close()
        self.client.aclose()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def set_scenarios(self, *args):
        """

        :param args:
        :return:
        """
        scenarios = []
        # scenarios.append({"Name": "Enterprise Data", "Scope": "Public"})
        for arg in args:
            s = dict(Name=arg['Name'], Scope=arg['Scope'])
            scenarios.append(s)
        return scenarios

    @abc.abstractmethod
    def refresh_auth(self):
        pass

    @property
    def data_model(self):
        return self._data_model

    @data_model.setter
    def data_model(self, dm):
        self._data_model = dm

    @property
    def base_url(self):
        return self._base_url

    @property
    def bulk_export_url(self):
        return self.base_url + BULK_URL + '/export'

    @property
    def bulk_upload_url(self):
        return self.base_url + BULK_URL + '/upload'

    @property
    def bulk_remove_url(self):
        return self.base_url + BULK_URL + '/remove'

    @property
    def workbook_url(self):
        return self.base_url + WORKBOOK_URL

    @property
    def workbook_import_url(self):
        return self.workbook_url + '/import'

    @property
    def worksheet_url(self):
        return self.base_url + WORKSHEET_URL

    @property
    def script_url(self):
        return self.base_url + SCRIPT_URL

    @property
    def oauth2_url(self):
        return self._base_url + "/oauth2/token"

    @property
    def max_connections(self):
        return self._maxconnections

class Environment(BaseEnvironment):
    def __init__(self, configuration: dict):
        super().__init__(configuration)
        self._session = requests.Session()
        self._maxconnections = 8

        timeout = httpx.Timeout(10.0, connect=60.0)
        self.client = httpx.AsyncClient(timeout=timeout)
        self.limit = asyncio.Semaphore(self.max_connections)

        # url
        self._configure_url(configuration)
        # authentication
        self._configure_auth(configuration)
        self._session.headers = self.global_headers
        # Data Model
        self._configure_data_model(configuration)
        # Scenario default
        self.scenarios = self.set_scenarios(ENTERPRISE_DATA_SCENARIO)
        # Workbook scripts
        self._configure_workbook_defaults(configuration)

    def _configure_url(self, configuration):
        try:
            self._base_url = configuration['url']
        except KeyError:
            raise ValueError('url not provided in configuration dict')

    def _configure_auth(self, configuration):

        try:
            self.auth_type = configuration['auth_type']
        except KeyError:
            raise ValueError('auth_type not provided in configuration dict')

        if self.auth_type == 'basic':
            self.authentication['username'] = configuration['username']
            self.authentication['password'] = configuration['password']
        elif self.auth_type == 'oauth2':
            self.authentication['clientID'] = configuration['clientID']
            self.authentication['client_secret'] = configuration['client_secret']
        else:
            raise ValueError(f'invalid authentication type {self.auth_type}')
        self.refresh_auth()

    def _configure_workbook_defaults(self, configuration):
        try:
            self._variables_script = configuration['variables_script']
        except KeyError:
            self._variables_script = None
            self._logger.debug(f'configuration variables_script not provided')
        try:
            self._worksheet_script = configuration['worksheet_script']
        except KeyError:
            self._worksheet_script = None
            self._logger.debug(f'configuration worksheet_script not provided')

    def _configure_data_model(self, configuration):
        try:
            self._data_model_dir = configuration['data_model_directory']
        except KeyError:
            self._data_model_dir = None
            # raise SetupError("Data Model directory not valid: " + configuration['data_model_directory'])
            self._logger.debug(f'configuration data_model_directory not provided')

        else:
            if os.path.exists(configuration['data_model_directory']):
                self._data_model_dir = configuration['data_model_directory']
            else:
                raise SetupError("Data Model directory not valid: " + configuration['data_model_directory'])

        # bootstrap in data model from local
        try:
            bootstrap_wbk = configuration['data_model_bootstrap']
        except KeyError:
            self.data_model = DataModel(None, None, None, None)
        else:
            self.data_model = DataModel(data_model_directory=None, url=self.base_url, headers=self.global_headers,
                                        workbook=bootstrap_wbk)

    def refresh_auth(self):
        auth = self._getAuth(self.auth_type)
        self.global_headers['Authorization'] = str(auth)
        asyncio.run(self.refresh_auth_async())

    async def refresh_auth_async(self):
        auth = await self._getAuth_async(self.auth_type)
        self.global_headers['Authorization'] = str(auth)

    def _getOauth2(self):
        """return the access token from RR instance based on clientID and client secret"""
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/token_rest.htm?
        # at some point, go back and rewrite this with the requests-oauthlib
        if self.authentication['clientID'] is None or self.authentication['client_secret'] is None:
            raise SetupError("oauth2 failed due to clientID or clientsecret being null")

        concat_data = self.authentication['clientID'] + ":" + self.authentication['client_secret']
        data_bytes = concat_data.encode('ascii')
        base64_bytes = base64.b64encode(data_bytes)
        b64_clientID_secret = base64_bytes.decode('ascii')


        payload = 'grant_type=client_credentials'
        headers = {
            'Authorization': 'Basic ' + b64_clientID_secret,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # requests.get(url, auth=HTTPDigestAuth('user', 'pass'))
        response = requests.request("POST", self.oauth2_url, headers=headers, data=payload)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, "failure during oauth2, status not 200", payload)
        return response_dict["access_token"]

    async def _get_oauth_async(self, client, limit: asyncio.Semaphore = None):
        if self.authentication['clientID'] is None or self.authentication['client_secret'] is None:
            raise SetupError("oauth2 failed due to clientID or clientsecret being null")

        concat_data = self.authentication['clientID'] + ":" + self.authentication['client_secret']
        data_bytes = concat_data.encode('ascii')
        base64_bytes = base64.b64encode(data_bytes)
        b64_clientID_secret = base64_bytes.decode('ascii')

        payload = 'grant_type=client_credentials'
        headers = {
            'Authorization': 'Basic ' + b64_clientID_secret,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            async with limit:
                response = await client.post(url=self.oauth2_url, headers=headers, content=payload)
                # do I need to check limit here?
        except:
            raise RequestsError(response, f"error during POST to: {self.oauth2_url}", payload)
        else:
            response_dict = json.loads(response.text)
            return response_dict["access_token"]

    def _getBasicAuth(self):
        """encode username and password as base64 and return it"""
        # at some point go back and use requests.auth HTTPDigestAuth
        if self.authentication['username'] is None or self.authentication['password'] is None:
            raise SetupError("basic auth failed due to username or password being null")

        concat_user_pass = self.authentication['username'] + ":" + self.authentication['password']
        user_pass_bytes = concat_user_pass.encode('ascii')
        base64_bytes = base64.b64encode(user_pass_bytes)
        b64_authentication = base64_bytes.decode('ascii')
        return b64_authentication

    def _getAuth(self, auth_type: str):
        """
        get the necessary authentication details dependent on what type of auth is needed (basic or oauth2)\n

        :param auth_type: basic or oauth2
        :return: string of authentication
        :raises SetupError: invalid auth type if not basic or oauth2
        """
        if auth_type == 'basic':
            b64_authentication = 'Basic ' + str(self._getBasicAuth())
        elif auth_type == 'oauth2':
            b64_authentication = 'Bearer ' + str(self._getOauth2())
        else:
            raise SetupError("invalid auth type")
        return b64_authentication

    async def _getAuth_async(self, auth_type: str):
        """
        get the necessary authentication details dependent on what type of auth is needed (basic or oauth2)\n

        :param auth_type: basic or oauth2
        :return: b64_authentication string of authentication
        :raises SetupError: invalid auth type if not basic or oauth2
        """
        if auth_type == 'basic':
            b64_authentication = 'Basic ' + str(self._getBasicAuth())
        elif auth_type == 'oauth2':
            bstr = await self._get_oauth_async(self.client, self.limit)
            b64_authentication = 'Bearer ' + str(bstr)
        else:
            raise SetupError("invalid auth type")
        return b64_authentication

    def get_table(self, table: str, namespace: str):
        """
        take as input the table name and return a Table object from the data dictionary.
        :param table: table name, for example Part
        :param namespace: table namespace, for example Mfg
        :return Table:
        :raises TypeError:
        :raises ValueError:
        """
        # validate input
        if not isinstance(table, str):
            raise TypeError("The parameter table type must be str.")
        if not table:
            raise ValueError("The parameter table must not be empty.")
        if not isinstance(namespace, str):
            raise TypeError("The parameter namespace type must be str.")
        if not namespace:
            raise ValueError("The parameter namespace must not be empty.")

        # get the Table from the data model and return it.
        tab = self.data_model.get_table(table, namespace)
        return tab
