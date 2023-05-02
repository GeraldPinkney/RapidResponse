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
    def __init__(self, data_model_directory, url=None, headers=None):
        """
        :param data_model_directory: Optional. file directory containing the Fields.tab and Tables.tab\n
        :raises TypeError: The parameter data_model_directory type must be str
        :raises ValueError: The parameter data_model_directory must be provided
        :raises DirectoryError: directory not valid or file not valid
        """

        # validate parameter
        #if not isinstance(data_model_directory, str):
        #    raise TypeError('The parameter data_model_directory type must be str')
        #if not data_model_directory:
        #    raise ValueError('The parameter data_model_directory must be provided')

        self.tables = []
        self._fields = []
        logging.basicConfig(filename='dm_logging.log', filemode='w',
                            format='%(name)s - %(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

        # if url is provided, then assume we can load from KXSHelperREST
        if url:
            self.load_table_data_from_helper_wbk(url, headers)
            self.load_field_data_from_helper_wbk(url,headers)

        # otherwise, if we have the DM dir, then assume we load from that
        elif data_model_directory:
            self._data_model_dir = data_model_directory

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

        # otherwise, if these are not provided, then load from package resources
        else:
            if resource_exists(__name__, 'data/Tables.tab'):
                file_name = resource_filename(__name__, 'data/Tables.tab')
                self.load_table_data_from_file(file_name)
            else:
                raise SetupError('failed to use data package - data/Tables.tab')

            if resource_exists(__name__, 'data/Fields.tab'):
                file_name = resource_filename(__name__, 'data/Fields.tab')
                self.load_field_data_from_file(file_name)
            else:
                raise SetupError('failed to use data package - data/Fields.tab')

        # if above was successful, then add fields to tables
        self.add_fields_to_tables()

    def __str__(self):
        return self.__repr__() + '\nTables: ' + str(len(self.tables))

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
                self.tables.append(Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))
                rowcount += 1
            logging.info(f'info: filename {file_path} rowcount {rowcount}')
        return self.tables

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
            if tab in self.tables:
                i = self.tables.index(tab)
                self.tables[i].add_fields(col)
        return self.tables

    def get_table(self, table: str, namespace: str):
        """
        take as input tablename and namespace and return the Table from data model\n
        :param table: string tablename
        :param namespace: string namespace of table
        :return: Table(table, namespace)
        """

        tab = Table(table, namespace)
        if tab in self.tables:
            i = self.tables.index(tab)
            return self.tables[i]
        else:
            raise ValueError('the table provided is not valid')

    def tables(self):
        return self.tables

    def load_table_data_from_helper_wbk(self, url, headers):
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
                    "Name": "KXSHelperREST",
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
                columns = ws.get('Columns')
                rows = ws.get('Rows')  # should be []
            else:
                raise RequestsError('missing queryID')
        q_url = b_url + "/integration/V1/data/worksheet" + "?queryId=" + queryID[1:] + "&workbookName=" + 'KXSHelperREST' + "&Scope=" + 'Public' + "&worksheetName=" + 'DataModel_Tables'

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
                #self.rows.append(WorksheetRow(r['Values'], self))
                self.tables.append(Table(*r['Values']))
                #self.tables.append(Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))

        return self.tables

    def load_field_data_from_helper_wbk(self, url, headers):
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
                    "Name": "KXSHelperREST",
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
                columns = ws.get('Columns')
                rows = ws.get('Rows')  # should be []
            else:
                raise RequestsError('missing queryID')
        q_url = b_url + "/integration/V1/data/worksheet" + "?queryId=" + queryID[1:] + "&workbookName=" + 'KXSHelperREST' + "&Scope=" + 'Public' + "&worksheetName=" + 'DataModel_Fields'

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
                #self.rows.append(WorksheetRow(r['Values'], self))
                self._fields.append({'Table': r['Values'][0],
                                     'Namespace': r['Values'][1],
                                     'Field': r['Values'][2],
                                     'Type': r['Values'][3],
                                     'Key': r['Values'][4]})
                #self.tables.append(Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))

        return self.tables