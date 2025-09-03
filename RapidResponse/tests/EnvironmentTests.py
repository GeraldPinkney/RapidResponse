import unittest
from unittest.mock import patch, MagicMock
import os

import RapidResponse
import RapidResponse.Table as Table
import RapidResponse.DataModel as DataModel
from RapidResponse.DataTable import DataTable, DataRow
from RapidResponse.Environment import Environment
from samples import sample_configuration
from RapidResponse.Err import DataError

# Mocking imports from RapidResponse
'''class DataModel:
    def __init__(self, data_model_directory, url, headers, workbook):
        self.data_model_directory = data_model_directory
        self.url = url
        self.headers = headers
        self.workbook = workbook

    def get_table(self, table, namespace):
        return f"Mocked Table: {namespace}.{table}"'''

class SetupError(Exception):
    pass

class RequestsError(Exception):
    def __init__(self, response, message, payload):
        self.response = response
        self.message = message
        self.payload = payload

import base64
import json
import requests


class TestEnvironment(unittest.TestCase):
    local_sample_bootstrap = {'url': 'http://localhost/rapidresponse',
                              'data_model_bootstrap': 'KXSHelperREST',
                              'auth_type': 'basic',
                              'username': 'gpinkney_ws',
                              'password': '1L0veR@pidResponse',
                              'worksheet_script': 'GP.GetWorkbook.Worksheets',
                              'variables_script': 'GP.GetWorkbook.Variables'
                              }
    def setUp(self):
        self.valid_config = {
            'url': 'http://example.com',
            'auth_type': 'basic',
            'username': 'user',
            'password': 'pass',
            'data_model_directory': 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel'
            #,'data_model_bootstrap': 'bootstrap_wbk'
        }

        self.invalid_config = {
            'url': 'http://example.com',
            'auth_type': 'invalid_auth',
            'data_model_directory': '/invalid/path'
        }

    def test_init_valid_config(self):
        env = Environment(self.valid_config)
        self.assertEqual(env.base_url, 'http://example.com')
        self.assertEqual(env.auth_type, 'basic')
        self.assertEqual(env.authentication['username'], 'user')
        self.assertEqual(env.authentication['password'], 'pass')
        self.assertEqual(env._data_model_dir, 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')
        self.assertIsInstance(env.data_model, DataModel.DataModel)

    def test_init_invalid_auth_type(self):
        with self.assertRaises(ValueError) as context:
            Environment(self.invalid_config)
        self.assertEqual(str(context.exception), 'invalid authentication type')

    def test_init_missing_url(self):
        config = self.valid_config.copy()
        del config['url']
        with self.assertRaises(ValueError) as context:
            Environment(config)
        self.assertEqual(str(context.exception), 'url not provided in configuration dict')

    def test_init_missing_auth_type(self):
        config = self.valid_config.copy()
        del config['auth_type']
        with self.assertRaises(ValueError) as context:
            Environment(config)
        self.assertEqual(str(context.exception), 'auth_type not provided in configuration dict')

    def test_get_basic_auth(self):
        env = Environment(self.valid_config)
        expected_auth = base64.b64encode(b'user:pass').decode('ascii')
        self.assertEqual(env._getBasicAuth(), expected_auth)

    @patch('requests.request')
    def test_get_oauth2(self, mock_request):
        config = self.valid_config.copy()
        config['auth_type'] = 'oauth2'
        config['clientID'] = 'client_id'
        config['client_secret'] = 'client_secret'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({'access_token': 'token'})
        mock_request.return_value = mock_response

        env = Environment(config)
        token = env._getOauth2()
        self.assertEqual(token, 'token')


    def test_refresh_auth_basic(self):
        env = Environment(self.valid_config)
        env.refresh_auth()
        expected_auth = 'Basic ' + base64.b64encode(b'user:pass').decode('ascii')
        self.assertEqual(env.global_headers['Authorization'], expected_auth)

    @patch('requests.request')
    def test_refresh_auth_oauth2(self, mock_request):
        config = self.valid_config.copy()
        config['auth_type'] = 'oauth2'
        config['clientID'] = 'client_id'
        config['client_secret'] = 'client_secret'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({'access_token': 'token'})
        mock_request.return_value = mock_response

        env = Environment(config)
        env.refresh_auth()
        expected_auth = 'Bearer token'
        self.assertEqual(env.global_headers['Authorization'], expected_auth)

    def test_set_scenarios(self):
        env = Environment(self.valid_config)
        scenarios = env.set_scenarios({"Name": "Scenario 1", "Scope": "Public"},
                                      {"Name": "Scenario 2", "Scope": "Private"})
        self.assertEqual(len(scenarios), 2)
        self.assertIn({"Name": "Scenario 1", "Scope": "Public"}, scenarios)
        self.assertIn({"Name": "Scenario 2", "Scope": "Private"}, scenarios)


    def test_invalid_data_model_directory(self):
        invalid_config = self.valid_config.copy()
        invalid_config['data_model_directory'] = '/invalid/path'
        with self.assertRaises(RapidResponse.Err.SetupError):
            Environment(invalid_config)

    @patch('os.path.exists', return_value=True)
    def test_valid_data_model_directory(self, mock_exists):
        env = Environment(self.valid_config)
        self.assertEqual(env._data_model_dir, 'C:\\Users\\gpinkney\\PycharmProjects\\RapidResponse\\RapidResponse\\tests\\DataModel')

    def test_env_with_scripts(self):
        env = Environment(self.local_sample_bootstrap)
        print(env._worksheet_script)

if __name__ == '__main__':
    unittest.main()
