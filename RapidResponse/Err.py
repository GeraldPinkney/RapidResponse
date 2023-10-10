

import logging


class Error(Exception):
    pass
    #def __init__(self, *argv):
    #    logging.info(f'Error: exception instance {type(self)}.')
    #    logging.info(f'Error: exception arguments stored in .args {self.args}.')
    #    logging.info(f'Error: exception str() {self}.')


class DirectoryError(Error):
    def __init__(self, msg, directory):
        # Error message thrown is saved in msg
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.info(f'Error: exception str() {self}.')
        self.msg = msg
        self.directory = directory


class TableError(Error):
    def __init__(self, tablename):
        # Error message thrown is saved in msg
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.info(f'Error: exception str() {self}.')
        self.tablename = tablename
        self.msg = "Table: " + tablename + " is not valid. Please use format Namespace::Tablename"


class SetupError(Error):
    def __init__(self, msg=None):
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        logging.info(f'Error: exception str() {self}.')
        self.msg = "Setup Error: " + msg


class RequestsError(Error):
    def __init__(self, response, msg=None):
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.info(f'Error: exception str() {self}.')
        self.msg = "RequestsError: " + msg
        self.response = response


class DataError(Error):
    def __init__(self, data, msg=None):
        self.logger = logging.getLogger('RapidPy')
        self.logger.info(f'Error: exception instance {type(self)}.')
        self.logger.info(f'Error: exception arguments stored in .args {self.args}.')
        self.logger.info(f'Error: exception str() {self}.')
        self.msg = "DataError: " + msg
        self.data = data

