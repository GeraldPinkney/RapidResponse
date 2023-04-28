import base64
import json
import logging
import os
import requests
from RapidResponse.RapidResponse.DataModel import DataModel

from RapidResponse.RapidResponse.Err import SetupError, RequestsError

sample_configuration = {'url': 'http://localhost/rapidresponse',
                        'data_model_bootstrap': 'KXSHelperREST',
                        'data_model_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\RapidResponse\\DataModel',
                        'auth_type': 'basic',
                        'username': 'gpinkney_ws',
                        'password': '1L0veR@pidResponse'
                        }


class Environment:
    """
    this is the python representation of your enviornment. It contains authentication details, data model data (tables, fields, etc) and provides the scoping for working with RR.\n
    :param configuration: dictionary containing necessary information for initialising environment
    :raises SetupError: Data Model directory not valid
    """
    def __init__(self, configuration: dict):
        if not isinstance(configuration, dict):
            raise TypeError('The parameter configuration type must be dict')
        if not configuration:
            raise ValueError('The parameter configuration must be provided')

        # base url on which stuff is appended for requests
        try:
            self._base_url = configuration['url']
        except KeyError:
            raise ValueError('url not provided in configuration dict')

        if os.path.exists(configuration['data_model_directory']):
            self._data_model_dir = configuration['data_model_directory']
        else:
            raise SetupError("Data Model directory not valid: " + configuration['data_model_directory'])

        # bootstrap in data model from local
        self._data_model = DataModel(self._data_model_dir)

        # authentication
        try:
            self.auth_type = configuration['auth_type']
        except KeyError:
            raise ValueError('auth_type not provided in configuration dict')

        self.authentication = {}
        if self.auth_type == 'basic':
            self.authentication['username'] = configuration['username']
            self.authentication['password'] = configuration['password']
        elif self.auth_type == 'oauth2':
            self.authentication['clientID'] = configuration['clientID']
            self.authentication['client_secret'] = configuration['client_secret']
        else:
            raise ValueError('invalid authentication type')

        # set global headers and populate with auth details
        self.global_headers = {}
        self.refresh_auth()

        self.scenarios = self.set_scenarios({"Name": "Enterprise Data", "Scope": "Public"})

        if configuration['data_model_bootstrap']:
            pass
        # todo add conditional logic to either get DM from local file, or from wbb

    def __repr__(self):
        return f'Environment(url={self._base_url!r}, data model directory={self._data_model_dir!r}, auth_type={self.auth_type!r})'

    def __str__(self):
        return f'Environment(url={self._base_url!r})'

    def _getOauth2(self):
        """return the access token from RR instance based on clientID and client secret"""
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/token_rest.htm?
        # at some point, go back and rewrite this with the requests-oauthlib
        if self.authentication['clientID'] is None or self.authentication['client_secret'] is None:
            raise SetupError("oauth2 failed due to clientID or clientsecret being null")

        concat_data = self.authentication['clientID'] + ":" + self.authentication[
            'client_secret']  # clientID + client secret
        data_bytes = concat_data.encode('ascii')
        base64_bytes = base64.b64encode(data_bytes)
        b64_data = base64_bytes.decode('ascii')
        url = self._base_url + "/oauth2/token"

        payload = 'grant_type=client_credentials'
        headers = {
            'Authorization': 'Basic ' + b64_data,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # requests.get(url, auth=HTTPDigestAuth('user', 'pass'))
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, "failure during oauth2, status not 200")
        # return response_text["access_token"]
        # print(response_dict["access_token"])
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
        b64_authentication = None
        if auth_type == 'basic':
            b64_authentication = 'Basic ' + str(self._getBasicAuth())
        elif auth_type == 'oauth2':
            b64_authentication = 'Bearer ' + str(self._getOauth2())
        else:
            raise SetupError("invalid auth type")
        return b64_authentication

    def set_scenarios(self, *args):

        scenarios = []
        # scenarios.append({"Name": "Enterprise Data", "Scope": "Public"})
        for arg in args:
            scenarios.append(arg)
        return scenarios

    def get_table(self, table: str, namespace: str):
        """
        take as input the table name and return a Table object from the data dictionary.
        :param table: table name, for example Part
        :param namespace: table namespace, for example Mfg
        :return: Table
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
        tab = self._data_model.get_table(table, namespace)
        return tab

    def refresh_auth(self):
        auth = self._getAuth(self.auth_type)
        self.global_headers['Authorization'] = str(auth)
