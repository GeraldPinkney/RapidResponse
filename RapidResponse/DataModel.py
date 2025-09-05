# DataModel.py

import csv
import json
import logging
import os

import requests
from pkg_resources import resource_filename, resource_exists

from RapidResponse.Err import DirectoryError, SetupError, RequestsError, DataError
from RapidResponse.Table import Table, Column


# from importlib_resources import

class AbstractDataModel:
    """
        This is the data model for the environment. It includes information about the tables, columns, etc.
        """

    def __init__(self, data_model_directory=None, url=None, headers=None, workbook=None):
        """
        :param data_model_directory: Optional. file directory containing the Fields.tab and Tables.tab
        :param url:
        :param headers:
        :param workbook:
        :raises TypeError: The parameter data_model_directory type must be str
        :raises ValueError: The parameter data_model_directory must be provided
        :raises DirectoryError: directory not valid or file not valid
        """
        self._excludedNamespacesList = ['System']
        self.tables = []
        self._fields = []
        # logging.basicConfig(filename='logging.log', filemode='w',format='%(name)s - %(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger('RapidPy.dm')

        self._url = url
        self._headers = headers
        self._workbook = workbook
        self._data_model_dir = data_model_directory
        self.Refresh()

    def Refresh(self):
        pass

    def _load_from_workbook(self):
        pass

    def _load_from_directory(self):
        pass

    def _load_from_package_resources(self):
        pass

    def _add_fields_to_tables(self):
        pass

    def _get_table_field(self, tablename, fieldname):
        """
        input like dm._get_table_field('Mfg::Part', 'Name')
        do not provide nested fields, or reference fields
        :param tablename:
        :param fieldname:
        :return Column:
        """
        tablearray = tablename.split('::')

        tab = self.get_table(table=tablearray[1], namespace=tablearray[0])
        # c = Column(name = fieldname, datatype='Str', key='N')

        if self._validate_fully_qualified_field_name(tablename=tab._table_name, fieldname=fieldname):
            if '.' not in fieldname:
                c = tab.get_field(fieldname)
            else:
                raise DataError(f'cannot process nested field, {fieldname}')
        else:
            raise DataError(f'invalid field {tablename}, {fieldname}')
        return c

    def _get_nested_table_field(self, tablename, fieldname):
        """
        # input like self._get_nested_field( 'Mfg::PartCustomer', 'Part.Site.Value')
        :param tablename: namespace qualified tablename, 'Mfg::PartCustomer'
        :param fieldname: field name, delimited by . 'Part.Site.Value'
        :return Column:
        """
        modified_column = None
        tablearray = tablename.split('::')
        if len(tablearray) != 2:
            raise DataError(f'invalid table: {tablename}. Requires format Mfg::PartCustomer')

        tab = Table(namespace=tablearray[0], name=tablearray[1])

        if not self._validate_fully_qualified_field_name(tab._table_name, fieldname):
            raise DataError(f'Field failed validity test. Invalid table: {tablename} and field: {fieldname}')

        if '.' not in fieldname:
            try:
                modified_column = self._get_table_field(tablename, fieldname)
            except DataError:
                if self._is_reference_field(tablearray[1], fieldname):
                    for c in self._fields:
                        # print(f'{c['Table']} == {tablearray[1]}, {c["Field"]} == {field_to_search}')
                        if c['Table'] == tablearray[1] and c["Field"] == fieldname:
                            # print('found rec')
                            modified_column = Column(name=c['Field'], datatype=c['Type'], key=c['Key'],
                                                     referencedTable=c['referencedTable'],
                                                     referencedTableNamespace=c['Related Namespace'],
                                                     fieldNamespace=c['FieldNameSpace'])
                else:
                    raise DataError(
                        f'Caught DataError exception, but field is not a refeerence. invalid table: {tablename} and field: {fieldname}')
        else:
            fieldarray = fieldname.split('.')  # [Part, Site, Value]
            fieldarray.insert(0, tab._table_name)  # [PartCustomer, Part, Site, Value]

            for i in range(len(fieldarray) - 1):
                if self._is_reference_field(fieldarray[i], fieldarray[i + 1]):
                    fieldarray[i + 1] = self._get_referenced_table(fieldarray[i], fieldarray[i + 1])
                else:
                    pass
            referenced_tab = self._get_referenced_tableAndNamespace(fieldarray[-3], fieldarray[-2])
            c = self._get_table_field(referenced_tab, fieldarray[-1])
            modified_column = Column(name=fieldname, datatype=c.datatype, key=c.key, referencedTable=c.referencedTable,
                                     referencedTableNamespace=c.referencedTableNamespace,
                                     fieldNamespace=c.fieldNamespace)
        return modified_column

    def get_field(self, tablename, fieldname):
        """
        get_field( 'Mfg::PartCustomer', 'Part.Site.Value')
        :param tablename: fully qualified, in format namespace::name
        :param fieldname: can be nested, for example 'Part.Site.Value'
        :return Column:
        """
        col = self._get_nested_table_field(tablename, fieldname)
        # now take the original namespace from the field. and overwrite it.
        tablearray = tablename.split('::')
        if len(tablearray) != 2:
            raise DataError(f'invalid table: {tablename}. Requires format Mfg::PartCustomer')

        # split to get the first bit of the fieldname, i.e. Part from Part.Site.Value
        if '.' not in fieldname:
            field_to_search = fieldname
        else:
            fieldarray = fieldname.split('.')  # [Part, Site, Value]
            field_to_search = fieldarray[0]

        # get the namespace of the original field
        for c in self._fields:
            # print(f'{c['Table']} == {tablearray[1]}, {c["Field"]} == {field_to_search}')
            if c['Table'] == tablearray[1] and c["Field"] == field_to_search:
                # print('found rec')
                col = col._replace(fieldNamespace=c['FieldNameSpace'])
        return col

    def _validate_fully_qualified_field_name(self, tablename, fieldname):
        """
        loop over the fieldname, and replace the fieldnames with their real table names, then validate whether the entire thing is valid
        :param tablename: example, Part (does not include namespace)
        :param fieldname: ReferencePart.Des
        :return: boolean, isValid
        """
        isValid = False
        # basecase
        if '.' not in fieldname:
            isValid = self._is_valid_field(tablename, fieldname)
        else:
            fieldarray = fieldname.split('.')
            fieldarray.insert(0, tablename)

            for i in range(len(fieldarray) - 1):
                # check it is a valid field
                if self._is_valid_field(fieldarray[i], fieldarray[i + 1]):
                    isValid = True
                    if self._is_reference_field(fieldarray[i], fieldarray[i + 1]):
                        fieldarray[i + 1] = self._get_referenced_table(fieldarray[i], fieldarray[i + 1])
                else:
                    isValid = False

        return isValid

    def _is_valid_field(self, tablename, fieldname):
        """
        _is_valid_field(Part, ReferencePart.BrandSubFlag.BrandFlag.Name)
        :param tablename:
        :param fieldname:
        :return:
        """

        isValid = False
        # basecase
        if '.' in fieldname:
            isValid = self._validate_fully_qualified_field_name(tablename, fieldname)
        else:
            for f in self._fields:
                if f['Table'] == tablename and f['Field'] == fieldname:
                    isValid = True
        return isValid

    def _get_referenced_table(self, tablename, fieldname):
        """

        :param tablename: example Part
        :param fieldname: example ReferencePart
        :return referencedTable: table name of the reference field ReferencePart
        :raises ValueError: if given fieldname with .
        """
        referencedTable = None
        if '.' not in fieldname:
            for f in self._fields:
                if f['Table'] == tablename and f['Field'] == fieldname and f['Type'] == 'Reference':
                    referencedTable = f['referencedTable']
                    return referencedTable
        else:
            raise ValueError(f'tablename: {tablename}, fieldname: {fieldname}', 'Fieldname cannot be . qualified')

        return referencedTable

    def _get_referenced_tableAndNamespace(self, tablename, fieldname):
        """

        :param tablename: part
        :param fieldname: referencepart
        :return referencedTableWithNamespace: {f["Related Namespace"]}::{f["referencedTable"]} table name of the reference field ReferencePart
        :raises ValueError: Fieldname cannot be . qualified
        :raises DataError: if provided with field that is not a reference
        """
        if '.' in fieldname:
            raise ValueError(f'tablename: {tablename}, fieldname: {fieldname}', 'Fieldname cannot be . qualified')

        referencedTableWithNamespace = None

        for fld in self._fields:
            if fld['Table'] == tablename and (fld['Field'] == fieldname or fld["referencedTable"] == fieldname) and fld[
                'Type'] == 'Reference':
                relatedNamespace = fld["Related Namespace"]
                referencedTab = fld["referencedTable"]
                referencedTableWithNamespace = f'{relatedNamespace}::{referencedTab}'
            elif fld['Table'] == tablename and fld['Field'] == fieldname and fld['Type'] != 'Reference':
                raise DataError(f'tablename: {tablename}, fieldname: {fieldname}', 'is not a reference field')

        if referencedTableWithNamespace is None:
            raise DataError(f'tablename: {tablename}, fieldname: {fieldname}',
                            f'tablename: {tablename}, fieldname: {fieldname} does not resolve to a referenced table with namespace')

        return referencedTableWithNamespace

    def _is_reference_field(self, tablename, fieldname):
        """
        _is_reference_field(part, site)
        :param tablename: table name, not qualified
        :param fieldname: fieldname, not . qualified
        :return boolean: isReference
        :raise ValueError: if fieldname contains .
        """
        # list((filter(lambda x: x['Table'] == tablename and x['Field'] == fieldname, env.data_model._fields)))
        isReference = False
        if '.' in fieldname:
            raise ValueError(f'tablename: {tablename}, fieldname: {fieldname}', 'Fieldname cannot be . qualified')

        for f in self._fields:
            if f['Table'] == tablename and f['Field'] == fieldname and f['Type'] == 'Reference':
                isReference = True
        return isReference

    def validate_field(self, tablename, fieldname):
        """
        loop over the fieldname, and replace the fieldnames with their real table names, then validate whether the entire thing is valid
        :param tablename: example, Part (does not include namespace)
        :param fieldname: ReferencePart.Des
        :return: boolean, isValid
        """
        return self._validate_fully_qualified_field_name(tablename, fieldname)

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

    def __contains__(self, item):

        if not isinstance(item, Table):
            tabarray = item.split('::')
            try:
                to_check = Table(tabarray[1], tabarray[0])
            except IndexError:
                raise ValueError(f'tablename parameter must be in format namespace::tablename. Table: {Table}')
        else:
            to_check = item

        if to_check in self.tables:
            return True
        else:
            return False

    def __getitem__(self, position):
        return self.tables[position]

    def __str__(self):
        return self.__repr__() + '\nTables: ' + str(len(self.tables))

    def __repr__(self):
        if self._data_model_dir:
            return f'DataModel(data_model_directory={self._data_model_dir!r})'
        else:
            return f'DataModel(data_model_workbook={self._workbook!r}, url={self._url!r})'

class DataModel(AbstractDataModel):
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

        super().__init__(data_model_directory, url, headers, workbook)

    def Refresh(self):
        # if we get a helper workbook, use that
        if self._workbook:
            self._load_from_workbook()
        # otherwise, if we have the DM dir, then assume we load from that
        elif self._data_model_dir:
            self._load_from_directory()
        # otherwise, if these are not provided, then load from package resources
        else:
            self._load_from_package_resources()
        # then add fields to tables
        self._add_fields_to_tables()

    def _load_from_workbook(self):
        self._load_table_data_from_helper_wbk(self._url, self._headers, self._workbook)
        self._load_field_data_from_helper_wbk(self._url, self._headers, self._workbook)

    def _load_from_directory(self):
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

    def _load_from_package_resources(self):
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
                # todo exclude based on namespace
                self.tables.append(
                    Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))
                rowcount += 1
            self.logger.info(f'info: filename {file_path} rowcount {rowcount}')
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
                # todo exclude based on namespace
                self._fields.append(row)
                rowcount += 1
            self.logger.info(f'info: filename {file_path} rowcount {rowcount}')
        return self._fields

    def _add_fields_to_tables(self):
        """
        iterate over fields populated from file & add them to the tables\n
        Should contain all possible fields that could be accessed from this table
        :return: list of tables
        """
        for f in self._fields:
            cols = list()
            tab = Table(f['Table'], f['Namespace'])

            if f['Type'] != 'Reference':
                cols.append(
                    Column(name=f['Field'], datatype=f['Type'], key=f['Key'], fieldNamespace=f['FieldNameSpace']))
            else:
                for ref in self._fields:
                    if ref['Table'] == f['referencedTable'] and f['Key'] == 'Y':  # and ref['Key'] == 'Y':
                        cols.append(Column(name=f['Field'] + '.' + ref['Field'], datatype=ref['Type'], key=ref['Key'],
                                           referencedTable=ref['referencedTable'],
                                           referencedTableNamespace=ref['Related Namespace'],
                                           fieldNamespace=f['FieldNameSpace']))
                        # Column(name, datatype, key, referenceTable, referencedTableNamespace, identification_fields, correspondingField, correspondingFieldNamespace, fieldNamespace)
                    elif ref['Table'] == f['referencedTable'] and f['Key'] == 'N':
                        cols.append(Column(name=f['Field'] + '.' + ref['Field'], datatype=ref['Type'], key=f['Key'],
                                           referencedTable=ref['referencedTable'],
                                           referencedTableNamespace=ref['Related Namespace'],
                                           fieldNamespace=f['FieldNameSpace']))
                        # Column(name, datatype, key, referenceTable, referencedTableNamespace, identification_fields, correspondingField, correspondingFieldNamespace, fieldNamespace)
                    else:
                        pass
            if tab in self.tables:
                i = self.tables.index(tab)
                self.tables[i].add_fields(cols)

        return self.tables

    def _validate_fully_qualified_field_name(self, tablename, fieldname):
        isValid = False
        # basecase
        if '.' not in fieldname:
            isValid = self._is_valid_field(tablename, fieldname)
        else:
            fieldarray = fieldname.split('.')
            fieldarray.insert(0, tablename)

            for i in range(len(fieldarray) - 1):
                # check it is a valid field
                #
                if self._is_valid_field(fieldarray[i], fieldarray[i + 1]):
                    isValid = True
                    if self._is_reference_field(fieldarray[i], fieldarray[i + 1]):
                        fieldarray[i + 1] = self._get_referenced_table(fieldarray[i], fieldarray[i + 1])
                else:
                    isValid = False

        return isValid

    def _load_table_data_from_helper_wbk(self, url, headers, workbook):
        queryID = None
        total_row_count = None
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
            raise RequestsError(response,
                                " failure during workbook initialise_for_extract, status not 200", payload)
        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == 'DataModel_Tables':
                queryID = ws['QueryHandle']['QueryID']
                total_row_count = ws.get('TotalRowCount')
            else:
                raise RequestsError(response, 'missing queryID', payload)
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
            if response.status_code == 200:
                response_dict = json.loads(response.text)
            else:
                raise RequestsError(response,
                                    "failure during workbook retrieve_worksheet_data, status not 200" + '\nurl:' + url)
            for r in response_dict["Rows"]:
                if r['Values'][1] in self._excludedNamespacesList:
                    self.logger.debug(f'record skipped due to excluded namespace: {r['Values'][1]}')
                else:
                    self.tables.append(Table(*r['Values']))
        return self.tables

    def _load_field_data_from_helper_wbk(self, url, headers, workbook):
        total_row_count = None
        queryID = None
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
            raise RequestsError(response,"failure during workbook initialise_for_extract", payload)

        response_worksheets = response_dict.get('Worksheets')
        for ws in response_worksheets:
            if ws.get('Name') == 'DataModel_Fields':
                queryID = ws['QueryHandle']['QueryID']
                total_row_count = ws.get('TotalRowCount')
                # columns = ws.get('Columns')
                # rows = ws.get('Rows')  # should be []
            else:
                raise RequestsError(response, 'missing queryID', payload)
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

                raise RequestsError(response,
                                    "failure during workbook retrieve_worksheet_data, status not 200" + '\nurl:' + url, payload)

            for r in response_dict["Rows"]:
                if r['Values'][8] in self._excludedNamespacesList:
                    self.logger.debug(f'record skipped due to excluded namespace: {r['Values'][1]}')
                else:
                    self._fields.append({'Table': r['Values'][0],
                                         'Namespace': r['Values'][1],
                                         'Field': r['Values'][2],
                                         'Type': r['Values'][3],
                                         'Key': r['Values'][4],
                                         'referencedTable': r['Values'][5],
                                         'Related Namespace': r['Values'][7][0:r['Values'][7].find('::')],
                                         'FieldNameSpace': r['Values'][8]
                                         })
                # self.tables.append(Table(row['Table'], row['Namespace'], row['Type'], row['Keyed'], row['Identification Fields']))

        return self._fields

