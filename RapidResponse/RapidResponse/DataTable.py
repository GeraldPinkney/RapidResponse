import json
import logging
import requests
from copy import deepcopy
from RapidResponse.RapidResponse.Environment import Environment
from RapidResponse.RapidResponse.Err import RequestsError, TableError, DataError
from RapidResponse.RapidResponse.Table import Table
# todo fix logging

class DataTable(Table):
    """
    subclass of Table that contains row data & can be used to push updates to RR\n

    :param environment: RapidResponse environment for which the table is scoped.
    :param tablename: Table that contains the data. Format 'Mfg::Part'
    :param columns: list of column names ['Name', 'Site', ...]
    :param table_filter: string representation of any filter condition applied to the table
    :param sync: boolean control whether any updates are pushed back to RR
    :param refresh: boolean refresh row data on initialisation
    :raises ValueError: environment or tablename is not provided, or tablename is not in data model
    :raises TypeError: environment, tablename is not correctly typed
    :raises DataError: key column not in column list. will log failure but not fail.
    """
    def __init__(self, environment: Environment, tablename: str, columns: list = None, table_filter: str = None, sync: bool = True, refresh: bool = True):
        
        # validations
        if not isinstance(environment, Environment):
            raise TypeError("The parameter environment type must be Environment.")
        if not environment:
            raise ValueError("The parameter environment must not be empty.")

        if not isinstance(tablename, str):
            raise TypeError("The parameter tablename type must be str.")
        if not tablename:
            raise ValueError("The parameter tablename must not be empty.")

        if not isinstance(sync, bool):
            raise TypeError("The parameter sync type must be bool.")

        logging.basicConfig(filename=environment.log_location + '\\logging.log', filemode='a',level=logging.INFO)
        tabarray = tablename.split('::')

        try:
            super().__init__(tabarray[1], tabarray[0])
        except IndexError:
            raise ValueError('table name parameter must be in format namespace::tablename')

        self.uploadId = None
        self.exportID = None
        self.environment = environment
        self.table_data = []
        self.columns = []
        self._filter = None

        # total_row_count used during export data gathering
        self.total_row_count = 0

        # sync attribute to control whether updates are pushed back to RR
        self._sync = sync

        # copy data from data model table
        temp_tab = self.environment.get_table(tabarray[1], tabarray[0])
        self._identification_fields = deepcopy(temp_tab._identification_fields)
        self._key_fields = deepcopy(temp_tab._key_fields)
        self._keyed = deepcopy(temp_tab._keyed)
        self._table_fields = deepcopy(temp_tab._table_fields)
        self._table_type = deepcopy(temp_tab._table_type)

        # set columns and filters
        try:
            self.set_columns(columns)
        except DataError:
            # allow this to silently error and write it to log
            pass
        self.set_filter(table_filter)

        if refresh:
            self.RefreshData()

    def __bool__(self):
        if len(self.table_data) > 0:
            return True
        else:
            return False

    def __len__(self):
        return len(self.table_data)

    def __getitem__(self, position):
        return self.table_data[position]

    def __contains__(self, item):
        # get key fields for table. then check if that value is present
        if item in self.table_data:
            return True
        else:
            return False

    def __repr__(self):
        return f'DataTable(environment={self.environment!r},name={self._table_namespace + "::" + self._table_name!r},' \
               f'columns={self.columns!r}, filter={self._filter!r}, sync={self._sync!r}) '

    def __str__(self):
        # return self and first 5 rows
        response = self.__repr__() + '\n'
        if self.total_row_count > 5:
            for i in range(0, 5):
                response = response + 'rownum: ' + str(i) + ' ' + str(self.table_data[i]) + '\n'
            response = response + '...'
        return response

    def __setitem__(self, key, value):
        if key in self.table_data:
            if self._sync:

                self.environment.refresh_auth()
                self._create_upload(self.table_data[key])
                self._complete_upload()
                self.uploadId = None
                self.table_data[key] = value
            else:
                self.table_data[key] = value
        else:
            raise ValueError('value not in table')

    def __delitem__(self, key):

        if self._sync:
            # delete from RR
            self.environment.refresh_auth()
            self._create_deletion(self.table_data[key])
            self._complete_deletion()
            self.uploadId = None

            del self.table_data[key]
        else:
            del self.table_data[key]

    def append(self, values):
        # todo fix append
        self.table_data.append(values)

    def extend(self, *args):
        self.add_rows(*args)

    def set_columns(self, columns: list = None):
        # if columns = None, then set columns to all fields on table
        if columns is None:
            for c in self._table_fields:
                if c.datatype != 'CompoundVector':
                    self.columns.append(c)
            # self.columns = deepcopy(self._table_fields)
        else:
            # check whether columns provided includes all key fields
            for k in self._key_fields:
                if k not in columns:
                    raise DataError(k, 'key column not in column list')

            # add all valid fields to DataTable Cols
            for c in columns:
                col = self.get_field(c)
                if col.datatype != 'CompoundVector':
                    self.columns.append(col)
                else:
                    logging.info(col.name + ' skipped due to type CompoundVector')
            # add fields to columns

    def set_filter(self, value: str):
        # check filter is valid for table
        self._filter = value

    def indexof(self, rec):
        return self.table_data.index(rec)

    def del_row(self, rec):
        index = self.indexof(rec)
        self.__delitem__(index)

    def _create_export(self):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/bulkread_rest.htm?
        local_query_fields = []
        if self._filter:
            query_filter = '[' + self._filter + ']'
        else:
            query_filter = ''
        # print(self._table_fields)
        for f in self.columns:
            local_query_fields.append(f.name)

        # print(type(local_query_string))
        # print(local_query_string)
        table = {'Namespace': self._table_namespace,
                 'Name': self._table_name}

        payload = json.dumps({
            "Scenario": self.environment.scenarios[0],
            "Table": table,
            "Fields": local_query_fields,
            "Filter": query_filter
        })
        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/bulk/export"

        response = requests.request("POST", url, headers=headers, data=payload)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            print(payload)
            print(response.content)
            print(response.text)
            raise RequestsError(response.text, "failure during bulk//export create, status not 200")
        # print(response)

        self.exportID = response_dict["ExportId"]
        self.total_row_count = response_dict["TotalRows"]

    def _get_export_results(self, startRow: int = 0, pageSize: int = 5):
        # using slicing on the query handle to strip off the #
        url = self.environment._base_url + "/integration/V1/bulk/export/" + self.exportID[1:] + "?startRow=" + str(
            startRow) + "&pageSize=" + str(pageSize) + "&delimiter=%09" + "&finishExport=false"
        # print(url)

        headers = self.environment.global_headers
        # print(url)
        # print(headers)
        response = requests.request("GET", url, headers=headers)

        # check on response = 200 or whatever
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, "failure during get bulk//export results, status not 200")

        for rec in response_dict["Rows"]:
            returned = rec.split('\t')
            self.table_data.append(returned)

    def RefreshData(self, data_range: int = 5000):
        # check tablename is set, check fields are set
        self.table_data.clear()
        self.environment.refresh_auth()
        # initialise query
        self._create_export()

        for i in range(0, self.total_row_count, data_range):  #
            self._get_export_results(i, data_range)
        self.exportID = None

    def add_row(self, rec):
        self.environment.refresh_auth()
        self._create_upload(rec)
        self._complete_upload()
        self.uploadId = None
        self.table_data.extend(rec)

    def add_rows(self, rows: list):
        self.environment.refresh_auth()
        for i in range(0, len(rows), 500000):
            self._create_upload(*rows)
            self._complete_upload()
            self.uploadId = None
            self.table_data.extend(rows)

    def _create_upload(self, *args):
        operation = 'upsert'
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/update_rest.htm?
        table = {'Namespace': self._table_namespace,
                 'Name': self._table_name}
        local_query_fields = []
        # print(self._table_fields)
        for f in self.columns:
            local_query_fields.append(f.name)

        rows = []
        for i in args:
            # create inner array (list)
            # arr = [i]
            # arr.append(i)
            # create dict containing single element {"Values": []}
            values = {"Values": i}
            # append to Rows
            rows.append(values)

        payload = json.dumps({
            'Scenario': self.environment.scenarios[0],
            'Table': table,
            'Fields': local_query_fields,
            'Rows': rows
        })

        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/bulk/"
        if operation == 'upsert':
            url = url + 'upload'
        elif operation == 'delete':
            url = url + 'remove'
        else:
            raise ValueError('invalid operation')

        response = requests.request("POST", url, headers=headers, data=payload)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response.text,
                                "failure during bulk//upload create, status not 200" + '\nurl:' + url + '\npayload: ' + payload + '\nheaders' + headers)
        # print(response)
        if operation == 'upsert':
            self.uploadId = response_dict["UploadId"]
        elif operation == 'delete':
            self.uploadId = response_dict["RemovalId"]
        else:
            raise ValueError('invalid operation')

    def _complete_upload(self):
        operation = 'upsert'
        headers = self.environment.global_headers
        # headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/bulk/"
        if operation == 'upsert':
            url = url + "upload/" + self.uploadId[1:] + '/complete'
        elif operation == 'delete':
            url = url + "remove/" + self.uploadId[1:] + '/complete'
        else:
            raise ValueError('invalid operation')

        response = requests.request("POST", url, headers=headers)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            print(response)
            raise RequestsError(response.text, "failure during bulk//upload complete, status not 200" + '\nurl:' + url)

        results = response_dict['Results']
        response_readable = 'status: ' + results['Status'] + '\nInsertedRowCount: ' + str(
            results['InsertedRowCount']) + '\nModifiedRowCount: ' + str(
            results['ModifiedRowCount']) + '\nDeleteRowCount: ' + str(
            results['DeleteRowCount']) + '\nErrorRowCount: ' + str(
            results['ErrorRowCount']) + '\nUnchangedRowCount: ' + str(results['UnchangedRowCount'])
        logging.info(response_readable)

    def _create_deletion(self, *args):
        operation = 'delete'
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/update_rest.htm?
        table = {'Namespace': self._table_namespace,
                 'Name': self._table_name}
        local_query_fields = []
        # print(self._table_fields)
        for f in self.columns:
            local_query_fields.append(f.name)

        rows = []
        for i in args:
            # create inner array (list)
            # arr = [i]
            # arr.append(i)
            # create dict containing single element {"Values": []}
            values = {"Values": i}
            # append to Rows
            rows.append(values)

        payload = json.dumps({
            'Scenario': self.environment.scenarios[0],
            'Table': table,
            'Fields': local_query_fields,
            'Rows': rows
        })

        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/bulk/"
        if operation == 'upsert':
            url = url + 'upload'
        elif operation == 'delete':
            url = url + 'remove'
        else:
            raise ValueError('invalid operation')

        response = requests.request("POST", url, headers=headers, data=payload)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response.text,
                                "failure during bulk//upload create, status not 200" + '\nurl:' + url + '\npayload: ' + payload + '\nheaders' + headers)
        # print(response)
        if operation == 'upsert':
            self.uploadId = response_dict["UploadId"]
        elif operation == 'delete':
            self.uploadId = response_dict["RemovalId"]
        else:
            raise ValueError('invalid operation')

    def _complete_deletion(self):
        operation = 'delete'
        headers = self.environment.global_headers
        # headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/bulk/"
        if operation == 'upsert':
            url = url + "upload/" + self.uploadId[1:] + '/complete'
        elif operation == 'delete':
            url = url + "remove/" + self.uploadId[1:] + '/complete'
        else:
            raise ValueError('invalid operation')

        response = requests.request("POST", url, headers=headers)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            print(response)
            raise RequestsError(response.text, "failure during bulk//upload complete, status not 200" + '\nurl:' + url)

        results = response_dict['Results']
        response = 'status: ' + results['Status'] + '\nInsertedRowCount: ' + str(
            results['InsertedRowCount']) + '\nModifiedRowCount: ' + str(
            results['ModifiedRowCount']) + '\nDeleteRowCount: ' + str(
            results['DeleteRowCount']) + '\nErrorRowCount: ' + str(
            results['ErrorRowCount']) + '\nUnchangedRowCount: ' + str(results['UnchangedRowCount'])
        logging.info(response)
