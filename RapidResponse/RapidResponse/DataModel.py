# DataModel.py

import csv
import logging
import os

from RapidResponse.RapidResponse.Err import DirectoryError
from RapidResponse.RapidResponse.Table import Table, Column


class DataModel:
    """
    This is the data model for the environment. It includes information about the tables, columns, etc.
    """
    def __init__(self, data_model_directory: str):
        """
        :param data_model_directory: file directory containing the Fields.tab and Tables.tab\n
        :raises TypeError: The parameter data_model_directory type must be str
        :raises ValueError: The parameter data_model_directory must be provided
        :raises DirectoryError: directory not valid or file not valid
        """

        # validate parameter
        if not isinstance(data_model_directory, str):
            raise TypeError('The parameter data_model_directory type must be str')
        if not data_model_directory:
            raise ValueError('The parameter data_model_directory must be provided')

        # validate its a valid directory
        if os.path.isdir(data_model_directory):
            self._data_model_dir = data_model_directory
        else:
            raise DirectoryError('directory not valid', data_model_directory)

        self._tables = []
        self._fields = []

        try:
            # check tables file is present, then load
            if os.path.isfile(self._data_model_dir + '\\Tables.tab'):
                self.load_table_data_from_file(self._data_model_dir + '\\Tables.tab')
            else:
                raise DirectoryError('file not valid', self._data_model_dir + '\\Tables.tab')

            # check fields file is present, then load
            if os.path.isfile(self._data_model_dir + '\\Fields.tab'):
                self.load_field_data_from_file(self._data_model_dir + '\\Fields.tab')
            else:
                raise DirectoryError('file not valid', self._data_model_dir + '\\Fields.tab')
        except:
            raise Exception
        else:
            # if above was successful, then add fields to tables
            self.add_fields_to_tables()

    def __str__(self):
        return self.__repr__() + '\nTables: ' + str(len(self._tables))

    def __repr__(self):
        return f'DataModel(data_model_directory={self._data_model_dir!r})'

    def load_table_data_from_file(self, file_path: str):
        """
        load table data from local file. will not have field data until enriched\n
        :param file_path: file path containing the Tables.tab file
        :return: 2d list of tables
        """
        with open(file_path, newline='', encoding='UTF-8-sig') as csvfile:
            rowcount = 0
            reader = csv.DictReader(csvfile, delimiter='\t')  # update delimiter if its comma not tab
            for row in reader:
                self._tables.append(Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))
                rowcount += 1
            logging.info(f'info: filename {file_path} rowcount {rowcount}')
        return self._tables

    def load_field_data_from_file(self, file_path: str):
        """
        load field data from local file\n
        :param file_path: file path containing the Fields.tab file
        :return: 2d list of fields
        """
        with open(file_path, newline='', encoding='UTF-8-sig') as csvfile:
            rowcount = 0
            reader = csv.DictReader(csvfile, delimiter='\t')  # update delimiter if its comma not tab
            for row in reader:
                self._fields.append(row)
                rowcount += 1
            logging.info(f'info: filename {file_path} rowcount {rowcount}')
        return self._fields

    def add_fields_to_tables(self):
        """
        iterate over fields populated from file & add them to the tables\n
        :return: list of tables
        """
        for f in self._fields:
            col = Column(f['Field'], f['Type'], f['Key'])
            tab = Table(f['Table'], f['Namespace'])
            if tab in self._tables:
                i = self._tables.index(tab)
                self._tables[i].add_fields(col)
        return self._tables

    def get_table(self, table: str, namespace: str):
        """
        take as input tablename and namespace and return the Table from data model\n
        :param table: string tablename
        :param namespace: string namespace of table
        :return: Table(table, namespace)
        """

        tab = Table(table, namespace)
        if tab in self._tables:
            i = self._tables.index(tab)
            return self._tables[i]
        else:
            raise ValueError('the table provided is not valid')
