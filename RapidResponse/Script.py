import json
import logging
from requests import Request, Session, HTTPError
from http import HTTPStatus
from RapidResponse.Environment import Environment
from RapidResponse.Err import RequestsError, ScriptError

class AbstractScript:
    '''
    A class to represent and execute a script within a RapidResponse environment. This loosely follows the Command design pattern (GOF).

    :param environment: RapidResponse environment for which the script is scoped. Mandatory.
    :param name: string, name of script. Mandatory.
    :param scope: enumerated, 'Public' or 'Private'. Optional, default is 'Public'
    :param parameters: dictionary containing the parameters. Optional.
    :raises ScriptError: If there is an error in the script execution.
    :raises RequestsError: If there is an error with the HTTP request.
    :raises ValueError: If the environment or name parameters are invalid.
    :raises TypeError: If the type of the environment or name parameters are incorrect.
    '''
    # todo take these from Utils.py
    SCOPE_PUBLIC = 'Public'
    SCOPE_PRIVATE = 'Private'
    VALID_SCOPES = {SCOPE_PUBLIC, SCOPE_PRIVATE}

    def __init__(self, environment: Environment, name: str, scope: str = None, parameters: dict = None):
        self._logger = logging.getLogger('RapidPy.spt')

        self._validate_parameters(environment, name)

        self._environment = environment
        self._name = name
        self._sanitized_name = self._sanitize_name(name)
        self._scope = scope if scope in self.VALID_SCOPES else self.SCOPE_PUBLIC
        self._parameters = parameters if dict(parameters) is not None else {}

        self._response = {'console': '', 'value': '', 'error': ''}
        self._internal_status = 0  # 0=not run, -1=error, 1=success

        self._session = Session()

    def _validate_parameters(self, environment, name):
        if not isinstance(environment, Environment):
            raise TypeError("The parameter environment type must be Environment.")
        if not environment:
            raise ValueError("The parameter environment must not be empty.")
        if not isinstance(name, str):
            raise TypeError("The parameter name type must be str.")
        if not name:
            raise ValueError("The parameter name must not be empty.")

    @staticmethod
    def _sanitize_name(name):
        return name.replace('&', '%26').replace(' ', '%20')

    @property
    def environment(self):
        return self._environment

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self._sanitized_name = self._sanitize_name(new_name)

    @property
    def scope(self):
        return self._scope

    @scope.setter
    def scope(self, new_scope: str) -> None:
        if new_scope not in self.VALID_SCOPES:
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
        if self._response['error']:
            error = self._response['error']
            return f"Error: errorcode {error['Code']}\nmessage {error['Message']}\n\nSee log for details"
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
        if not isinstance(other, AbstractScript):
            return NotImplemented
        return (self._environment == other._environment and
                self._name == other._name and
                self._scope == other._scope and
                self._parameters == other._parameters)

    def __hash__(self):
        return hash((self._environment, self._name, self._scope, frozenset(self._parameters.items())))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self._session.close()

    def execute(self):
        pass



class Script(AbstractScript):
    '''
    A class to represent and execute a script within a RapidResponse environment. This loosely follows the Command design pattern (GOF).

    :param environment: RapidResponse environment for which the script is scoped. Mandatory.
    :param name: string, name of script. Mandatory.
    :param scope: enumerated, 'Public' or 'Private'. Optional, default is 'Public'
    :param parameters: dictionary containing the parameters. Optional.
    :raises ScriptError: If there is an error in the script execution.
    :raises RequestsError: If there is an error with the HTTP request.
    :raises ValueError: If the environment or name parameters are invalid.
    :raises TypeError: If the type of the environment or name parameters are incorrect.
    '''

    def __init__(self, environment: Environment, name: str, scope: str = None, parameters: dict = None):
        super().__init__(environment, name, scope, parameters)

        self._session.headers.update(self.environment.global_headers)

    def execute(self, sync=True):
        '''
        Executes the script. Currently, supports only synchronous execution.

        :param sync: Boolean flag indicating synchronous execution. Default is True.
        :raises ScriptError: If there is an error in the script execution.
        :raises RequestsError: If there is an error with the HTTP request.
        '''
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
        self._reset_response_state()

        payload = json.dumps(self._parameters)
        url = f'{self.environment.script_url}/{self.scope}/{self._sanitized_name}'
        self._logger.debug(f"Sending POST request to {url} with payload {payload}")

        req = Request('POST', url, headers=session.headers, data=payload)
        prepped = req.prepare()

        try:
            response = session.send(prepped)
            response.raise_for_status()  # Will raise HTTPError for bad responses
            return response.json()
        except HTTPError as e:
            raise RequestsError(response, f"HTTP error during POST to: {url}", payload) from e

    def _reset_response_state(self):
        self._internal_status = -1
        self._response.update({'console': '', 'value': '', 'error': ''})

    def _process_execute_response(self, response_dict):
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