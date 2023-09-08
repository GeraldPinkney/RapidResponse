# DataModel.py

import csv
import json
import logging
import os

import requests
from pkg_resources import resource_filename, resource_exists

from RapidResponse.Err import DirectoryError, SetupError, RequestsError
from RapidResponse.Table import Table, Column


class DataModel:
    """
    This is the data model for the environment. It includes information about the tables, columns, etc.
    """

    def __init__(self, data_model_directory=None, url=None, headers=None, workbook=None):
        """
        :param data_model_directory: Optional. file directory containing the Fields.tab and Tables.tab\n
        :raises TypeError: The parameter data_model_directory type must be str
        :raises ValueError: The parameter data_model_directory must be provided
        :raises DirectoryError: directory not valid or file not valid
        """

        self.tables = []
        self._fields = []
        logging.basicConfig(filename='dm_logging.log', filemode='w',
                            format='%(name)s - %(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

        self._url = url
        self._headers = headers
        self._workbook = workbook
        self._data_model_dir = data_model_directory

        # if we get a helper workbook, use that
        if self._workbook:
            self.load_from_workbook()
        # otherwise, if we have the DM dir, then assume we load from that
        elif data_model_directory:
            self.load_from_directory()
        # otherwise, if these are not provided, then load from package resources
        else:
            self.load_from_package_resources()

        # then add fields to tables
        self._add_fields_to_tables()

    def __str__(self):
        return self.__repr__() + '\nTables: ' + str(len(self.tables))

    def __repr__(self):
        if self._data_model_dir:
            return f'DataModel(data_model_directory={self._data_model_dir!r})'
        else:
            return f'DataModel(data_model_workbook={self._workbook!r}, url={self._url!r})'

    def load_from_workbook(self):
        self._load_table_data_from_helper_wbk(self._url, self._headers, self._workbook)
        self._load_field_data_from_helper_wbk(self._url, self._headers, self._workbook)

    def load_from_directory(self):
        # check tables file is present, then load
        if os.path.isfile(self._data_model_dir + '\\Tables.tab'):
            self._load_table_data_from_file(self._data_model_dir + '\\Tables.tab')
        else:
            raise DirectoryError('file not valid', self._data_model_dir + '\\Tables.tab')

        # check fields file is present, then load
        if os.path.isfile(self._data_model_dir + '\\Fields.tab'):
            self._load_field_data_from_file(self._data_model_dir + '\\Fields.tab')
        else:
            raise DirectoryError('file not valid', self._data_model_dir + '\\Fields.tab')

    def load_from_package_resources(self):
        if resource_exists(__name__, 'data/Tables.tab'):
            file_name = resource_filename(__name__, 'data/Tables.tab')
            self._load_table_data_from_file(file_name)
        else:
            raise SetupError('failed to use data package - data/Tables.tab')

        if resource_exists(__name__, 'data/Fields.tab'):
            file_name = resource_filename(__name__, 'data/Fields.tab')
            self._load_field_data_from_file(file_name)
        else:
            raise SetupError('failed to use data package - data/Fields.tab')

    def _load_table_data_from_file(self, file_path: str):
        """
        load table data from local file. will not have field data until enriched\n
        :param file_path: file path containing the Tables.tab file
        :return: 2d list of tables
        """
        with open(file_path, newline='', encoding='UTF-8-sig') as csvfile:
            rowcount = 0
            reader = csv.DictReader(csvfile, delimiter='\t')  # update delimiter if its comma not tab
            for row in reader:
                self.tables.append(
                    Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))
                rowcount += 1
            logging.info(f'info: filename {file_path} rowcount {rowcount}')
        return self.tables

    def _load_field_data_from_file(self, file_path: str):
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

    def _add_fields_to_tables(self):
        """
        iterate over fields populated from file & add them to the tables\n
        :return: list of tables
        """
        for f in self._fields:
            cols = []
            tab = Table(f['Table'], f['Namespace'])

            if f['Type'] != 'Reference':
                cols.append(Column(f['Field'], f['Type'], f['Key']))
            else:
                for ref in self._fields:
                    if ref['Table'] == f['referencedTable']: #and ref['Key'] == 'Y':
                        cols.append(Column(f['Field']+'.'+ref['Field'], ref['Type'], ref['Key'], ref['referencedTable']))
            if tab in self.tables:
                i = self.tables.index(tab)
                self.tables[i].add_fields(cols)

        return self.tables

    def get_table(self, table: str, namespace: str):
        """
        take as input tablename and namespace and return the Table from data model\n
        :param table: string tablename
        :param namespace: string namespace of table
        :return: Table(table, namespace)
        :raises ValueError: tablename is not in data model
        """

        tab = Table(table, namespace)
        if tab in self.tables:
            i = self.tables.index(tab)
            return self.tables[i]
        else:
            raise ValueError('the table provided is not valid: ' + str(tab))

    def tables(self):
        return self.tables

    def _load_table_data_from_helper_wbk(self, url, headers, workbook):
        b_url = url
        url = b_url + "/integration/V1/data/workbook"
        headers = headers
        headers['Content-Type'] = 'application/json'

        payload = json.dumps({
            "Scenario": {
                "Name": "Enterprise Data",
                "Scope": "Public"
            },
            "WorkbookParameters": {
                "Workbook": {
                    "Name": workbook,
                    "Scope": "Public"
                },
                "SiteGroup": "All Sites",
                "Filter": {
                    "Name": "All Parts",
                    "Scope": "Public"
                },
                "VariableValues": {
                    "DataModel_IsHidden": "No",
                    "DataModel_IsReadOnly": "All",
                    "DataModel_IsIncludeDataTypeSet": "N",
                    "FilterType": "All"
                },
                "WorksheetNames": [
                    "DataModel_Tables"
                ]
            }
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            print(payload)
            print(url)
            raise RequestsError(response.text,
                                " failure during workbook initialise_for_extract, status not 200")

        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == 'DataModel_Tables':
                queryID = ws['QueryHandle']['QueryID']
                total_row_count = ws.get('TotalRowCount')
                # columns = ws.get('Columns')
                # rows = ws.get('Rows')  # should be []
            else:
                raise RequestsError('missing queryID')
        q_url = b_url + "/integration/V1/data/worksheet" + "?queryId=" + queryID[
                                                                         1:] + "&workbookName=" + 'KXSHelperREST' + "&Scope=" + 'Public' + "&worksheetName=" + 'DataModel_Tables'

        pagesize = 500
        pages = total_row_count // pagesize
        if total_row_count % pagesize != 0:
            pages = pages + 1

        for i in range(pages):
            url = q_url + "&startRow=" + str(0 + (pagesize * i)) + "&pageSize=" + str(pagesize)
            response = requests.request("GET", url,
                                        headers=headers)  # using GET means you can embed stuff in url, rather than the POST endpoint which needs you to have stuff in payload
            # check valid response
            if response.status_code == 200:
                response_dict = json.loads(response.text)

            else:

                raise RequestsError(response.text,
                                    "failure during workbook retrieve_worksheet_data, status not 200" + '\nurl:' + url)

            # response_rows = response_dict['Rows']
            # for r in response_rows:
            #    # print(r['Values'])
            #    rows.append()
            # self.rows = rows
            for r in response_dict["Rows"]:
                # returned = rec.split('\t')
                # self.rows.append(WorksheetRow(r['Values'], self))
                self.tables.append(Table(*r['Values']))
                # self.tables.append(Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))

        return self.tables

    def _load_field_data_from_helper_wbk(self, url, headers, workbook):
        b_url = url
        url = b_url + "/integration/V1/data/workbook"
        headers = headers
        headers['Content-Type'] = 'application/json'

        payload = json.dumps({
            "Scenario": {
                "Name": "Enterprise Data",
                "Scope": "Public"
            },
            "WorkbookParameters": {
                "Workbook": {
                    "Name": workbook,
                    "Scope": "Public"
                },
                "SiteGroup": "All Sites",
                "Filter": {
                    "Name": "All Parts",
                    "Scope": "Public"
                },
                "VariableValues": {
                    "DataModel_IsHidden": "No",
                    "DataModel_IsReadOnly": "All",
                    "DataModel_IsIncludeDataTypeSet": "N",
                    "FilterType": "All"
                },
                "WorksheetNames": [
                    "DataModel_Fields"
                ]
            }
        })

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            print(payload)
            print(url)
            raise RequestsError(response.text,
                                " failure during workbook initialise_for_extract, status not 200")

        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == 'DataModel_Fields':
                queryID = ws['QueryHandle']['QueryID']
                total_row_count = ws.get('TotalRowCount')
                # columns = ws.get('Columns')
                # rows = ws.get('Rows')  # should be []
            else:
                raise RequestsError('missing queryID')
        q_url = b_url + "/integration/V1/data/worksheet" + "?queryId=" + queryID[
                                                                         1:] + "&workbookName=" + workbook + "&Scope=" + 'Public' + "&worksheetName=" + 'DataModel_Fields'

        pagesize = 500
        pages = total_row_count // pagesize
        if total_row_count % pagesize != 0:
            pages = pages + 1

        for i in range(pages):
            url = q_url + "&startRow=" + str(0 + (pagesize * i)) + "&pageSize=" + str(pagesize)
            response = requests.request("GET", url,
                                        headers=headers)  # using GET means you can embed stuff in url, rather than the POST endpoint which needs you to have stuff in payload
            # check valid response
            if response.status_code == 200:
                response_dict = json.loads(response.text)

            else:

                raise RequestsError(response.text,
                                    "failure during workbook retrieve_worksheet_data, status not 200" + '\nurl:' + url)

            # response_rows = response_dict['Rows']
            # for r in response_rows:
            #    # print(r['Values'])
            #    rows.append()
            # self.rows = rows
            for r in response_dict["Rows"]:
                # returned = rec.split('\t')
                # self.rows.append(WorksheetRow(r['Values'], self))
                self._fields.append({'Table': r['Values'][0],
                                     'Namespace': r['Values'][1],
                                     'Field': r['Values'][2],
                                     'Type': r['Values'][3],
                                     'Key': r['Values'][4],
                                     'referencedTable': r['Values'][5]}
                                    )
                # self.tables.append(Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))

        return self._fields

    def __contains__(self, item):

        if not isinstance(item, Table):
            tabarray = item.split('::')
            try:
                to_check = Table(tabarray[1], tabarray[0])
            except IndexError:
                raise ValueError('table name parameter must be in format namespace::tablename')
        else:
            to_check = item

        if to_check in self.tables:
            return True
        else:
            return False

    def __getitem__(self, position):
        return self.tables[position]
