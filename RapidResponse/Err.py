import logging


class Error(Exception):
    pass
    # def __init__(self, *argv):
    #    logging.info(f'Error: exception instance {type(self)}.')
    #    logging.info(f'Error: exception arguments stored in .args {self.args}.')
    #    logging.info(f'Error: exception str() {self}.')


class ScriptError(Error):
    def __init__(self, code, message, console, scriptname, scriptscope, line, character):
        self.code = code  # JavascriptException,
        self.message = message
        self.console = console
        self.script = {"Name": scriptname, "Scope": scriptscope}
        self.error_location = f'line {line}, character {character}'
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.info(f'Error: exception str() {self}.')


class DirectoryError(Error):
    def __init__(self, msg, directory):
        # Error message thrown is saved in msg
        self.msg = msg
        self.directory = directory
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.info(f'Error: exception str() {self}.')


class TableError(Error):
    def __init__(self, tablename):
        # Error message thrown is saved in msg
        self.tablename = tablename
        self.msg = "Table: " + tablename + " is not valid. Please use format Namespace::Tablename"
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.info(f'Error: exception str() {self}.')


class SetupError(Error):
    def __init__(self, msg=None):
        self.msg = "Setup Error: " + msg
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.info(f'Error: exception str() {self}.')


class RequestsError(Error):
    def __init__(self, response, msg=None, payload=None):
        self.response = response
        self.msg = "RequestsError: " + msg
        self.payload = payload
        if response is None:
            self.msg + f"\n No idea ."
        elif response.status_code == 400:
            self.msg + f"\nstatus: {response.status_code}. The request body contains an error."
        elif response.status_code == 401:
            self.msg + f"\nstatus: {response.status_code}. Invalid credentials provided for the user account or the authorization method is not supported by the endpoint"
        elif response.status_code == 403:
            self.msg + f"\nstatus: {response.status_code}. The user specified does not have permission to perform web service operations"
        elif response.status_code == 404:
            self.msg + f"\nstatus: {response.status_code}.The specified endpoint is not valid or does not exist"
        elif response.status_code == 405:
            self.msg + f"\nstatus: {response.status_code}. The specified HTTP method is not supported by the endpoint"
        elif response.status_code == 415:
            self.msg + f"\nstatus: {response.status_code}. The specified media type is not supported by the endpoint"
        elif response.status_code == 503:
            self.msg + f"\nstatus: {response.status_code}. RapidResponse is not available."
        else:
            self.msg + f"\nstatus: {response.status_code}. status not 200"

        self.logger = logging.getLogger('RapidPy')
        self.logger.error(f'Error: exception instance {type(self)}.')
        self.logger.error(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.error(f'Error: exception str() {self}.')
        self.logger.error(self.msg)
        self.logger.error(response.text)
        self.logger.error(response.content)
        self.logger.error(payload)


class DataError(Error):
    def __init__(self, data, msg=None):
        self.msg = "DataError: " + msg
        self.data = data
        self.logger = logging.getLogger('RapidPy')
        self.logger.error(f'Error: exception instance {type(self)}.')
        self.logger.error(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.error(f'Error: exception str() {self}.')
        self.logger.error(str(self.data))
