# Script.py
import json
import logging
from requests import Request, Session, HTTPError
from http import HTTPStatus
from RapidResponse.Environment import Environment
from RapidResponse.Err import RequestsError, ScriptError

class Script:
    '''
    A class to represent and execute a script within a RapidResponse environment.

    :param environment: RapidResponse environment for which the script is scoped. Mandatory.
    :param name: string, name of script. Mandatory.
    :param scope: enumerated, 'Public' or 'Private'. Optional, default is 'Public'
    :param parameters: dictionary containing the parameters. Optional.
    :raises ScriptError: If there is an error in the script execution.
    :raises RequestsError: If there is an error with the HTTP request.
    :raises ValueError: If the environment or name parameters are invalid.
    :raises TypeError: If the type of the environment or name parameters are incorrect.

    https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/rest_endpoint.htm
    '''
    def __init__(self, environment:Environment, name:str, scope:str=None, parameters:dict=None):
        self._logger = logging.getLogger('RapidPy.spt')

        # validations
        if not isinstance(environment, Environment):
            raise TypeError("The parameter environment type must be Environment.")
        if not environment:
            raise ValueError("The parameter environment must not be empty.")
        if not isinstance(name, str):
            raise TypeError("The parameter name type must be str.")
        if not name:
            raise ValueError("The parameter name must not be empty.")


        self._environment = environment
        self._name = name
        self._sanitized_name = name.replace('&', '%26').replace(' ','%20')
        if scope is None:
            self._scope = 'Public'
        else:
            if scope not in ['Public', 'Private']:
                raise ValueError("The parameter 'scope' must be either 'Public' or 'Private'.")
            self._scope = scope
        if parameters is None:
            self._parameters = dict()
        else:
            self._parameters = dict(parameters)

        self._response = dict(console='', value='', error='')
        self._session = Session()
        self._session.headers = self.environment.global_headers
        self._internal_status = 0 # 0=not run, -1=error, 1=success
    @property
    def environment(self):
        return self._environment
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, new_name):
        self._name = new_name
        self._sanitized_name = new_name.replace('&', '%26').replace(' ', '%20')
    @property
    def scope(self):
        return self._scope
    @scope.setter
    def scope(self, new_scope: str) -> None:
        if new_scope not in ['Public', 'Private']:
            raise ValueError("The scope must be either 'Public' or 'Private'.")
        self._scope = new_scope
    @property
    def console(self) -> str:
        return self._response['console']
    @property
    def value(self) -> str:
        return self._response['value']
    @property
    def status(self):
        if len(self._response['error']) > 0:
            return f"Error: errorcode {self._response['error']['Code']}\nmessage {self._response['error']['Message']}\n\nSee log for details"
        elif self._internal_status == 0:
            return f"Not Run"
        elif self._internal_status == 1:
            return f"Success"
        else:
            return f"Unknown"
    @property
    def parameters(self):
        return self._parameters
    @parameters.setter
    def parameters(self, new_params):
        self._parameters = dict(new_params)

    def __str__(self) -> str:
        return f"Script(name={self._name}, scope={self._scope}, status={self.status}, parameters={self._parameters}) "

    def __repr__(self) -> str:
        return (f"Script(environment={repr(self._environment)}, name={self._name}, "
                f"scope={self._scope}, parameters={self._parameters})")

    def __eq__(self, other) -> bool:
        if not isinstance(other, Script):
            return NotImplemented
        return (self._environment == other._environment and
                self._name == other._name and
                self._scope == other._scope and
                self._parameters == other._parameters)

    def __hash__(self) :
        return hash((self._environment, self._name, self._scope, frozenset(self._parameters.items())))

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    def close(self):
        self._session.close()

    def execute(self, sync = True):
        '''
        Executes the script. Currently supports only synchronous execution.

        :param sync: Boolean flag indicating synchronous execution. Default is True.
        :raises ScriptError: If there is an error in the script execution.
        :raises RequestsError: If there is an error with the HTTP request.
        '''

        response_dict = self._send_execute_script(self._session)

        try:
            self._process_execute_response(response_dict)
        except ScriptError:
            self._internal_status = -1
        else:
            self._internal_status = 1

    def _send_execute_script(self, session):
        # clear state
        self._internal_status = -1
        self._response.update({'console': ''})
        self._response.update({'value': ''})
        self._response.update({'error': ''})

        s = session
        payload = json.dumps(self._parameters)
        url = f'{self.environment.script_url}/{self.scope}/{self._sanitized_name}'
        req = Request('POST',url , headers=s.headers, data=payload)
        prepped = req.prepare()
        response = s.send(prepped)
        if response.status_code == 200: # will get this if its executed, regardless of whether its successful or not.
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {url}", payload)
        return response_dict

    def _process_execute_response(self, response_dict):
        rd = response_dict
        self._response.update({'console':rd['Console']})
        self._response.update({'value': rd['Value']})
        if 'ScriptError' in rd:
            error = rd['ScriptError']
            self._response.update({'error': error})
            raise ScriptError(error['Code'], error['Message'], error['Console'], error['ScriptName'],
                              error['ScriptScope'], error['Line'], error['Character'])