# DataTable.py

import json
import logging
import requests
import asyncio
import httpx
from copy import deepcopy
from RapidResponse.Environment import Environment
from RapidResponse.Err import RequestsError, DataError
from RapidResponse.Table import Table, Column

# todo add controls to not allow update of calculated fields or delete of rows from calculated table

class DataTable(Table):
    """
    subclass of Table that contains row data & can be used to push updates to RR\n

    :param environment: RapidResponse environment for which the table is scoped.
    :param tablename: Table that contains the data. Format 'Mfg::Part'
    :param columns: list of column names ['Name', 'Site', ...]
    :param table_filter: string representation of any filter condition applied to the table
    :param sync: boolean control whether any updates are pushed back to RR
    :param refresh: boolean refresh row data on initialisation
    :param scenario: dict {"Name": "Enterprise Data", "Scope": "Public"}
    :raises ValueError: environment or tablename is not provided, or tablename is not in data model
    :raises TypeError: environment, tablename is not correctly typed
    :raises DataError: key column not in column list. will log failure but not fail.
    """
    def __init__(self, environment: Environment, tablename: str, columns: list = None, table_filter: str = None, sync: bool = True, refresh: bool = True, scenario = None):

        logging.basicConfig(filename='logging.log', filemode='w',format='%(name)s - %(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger('RapidPy.dt')

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

        tabarray = tablename.split('::')

        try:
            super().__init__(tabarray[1], tabarray[0])
        except IndexError:
            raise ValueError('table name parameter must be in format namespace::tablename')

        self.uploadId = None
        self.exportID = None
        self.environment = environment
        self._table_data = []
        self.columns = []
        self._filter = table_filter

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

        if scenario is None:
            self.scenario = self.environment.scenarios[0]
        else:
            # check scenario has both Name and scope {"Name": "Enterprise Data", "Scope": "Public"}
            try:
                if ['Name', 'Scope'] == list(scenario.keys()):
                    self.scenario = scenario
                else:
                    raise ValueError('scenario not valid: ' + scenario)
                    #self.scenario = environment.scenarios[0]
            except AttributeError:
                raise ValueError("scenario parameter format is {'Name': 'Integration', 'Scope': 'Public'} " + scenario)

        # set columns and filters
        try:
            self.set_columns(columns)
        except DataError:
            # allow this to silently error and write it to log
            for k in self._key_fields:
                if k not in columns:
                    columns.append(k)
            #columns.extend(self._key_fields)
            #print(columns)
            self.set_columns(columns)
        self.set_filter(table_filter)

        if refresh:
            self.RefreshData_async()

    def __bool__(self):
        if len(self._table_data) > 0:
            return True
        else:
            return False

    def __len__(self):
        return len(self._table_data)

    def __getitem__(self, position):
        return self._table_data[position]

    def __contains__(self, item):
        # get key fields for table. then check if that value is present
        if item in self._table_data:
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
                response = response + 'rownum: ' + str(i) + ' ' + str(self._table_data[i]) + '\n'
            response = response + '...'
        return response

    def __setitem__(self, key, value):
        if not isinstance(value, DataRow):
            self._table_data[key] = DataRow(value, self)
        else:
            self._table_data[key] = value
        if self._sync:
            self.environment.refresh_auth()
            self._create_upload(self._table_data[key])
            self._complete_upload()
            self.uploadId = None

    def __delitem__(self, key):

        if self._sync:
            # delete from RR
            # self.environment.refresh_auth()
            self._create_deletion(self._table_data[key])
            self._complete_deletion()
            self.uploadId = None

            del self._table_data[key]
        else:
            del self._table_data[key]
        self.total_row_count -= 1

    def map(self, action):
        # yields new items that result from applying an action() callable to each item in the underlying list
        return type(self)(action(item) for item in self._table_data)

    def filter(self, predicate):
        # yields all the items that return True when calling predicate() on them
        return type(self)(item for item in self._table_data if predicate(item))

    def for_each(self, func):
        # calls func() on every item in the underlying list to generate some side effect.
        for item in self._table_data:
            func(item)

    def append(self, values):
        # adds a single new item at the end of the underlying list
        if self._sync:
            self.add_row(values)

        if not isinstance(values, DataRow):
            self._table_data.append(DataRow(values, self))
        else:
            self._table_data.append(values)

    def extend(self, *args):
        # todo fix when doing insert messy refereence fields
        if self._sync:
            self.add_rows(*args)
        # self._table_data.extend(*args)

        if isinstance(*args, type(DataRow)):
            self._table_data.extend(*args)
        else:
            to_add = [DataRow(item, self) for item in args[0]]

            self._table_data.extend([DataRow(item, self) for item in args[0]])

    def set_columns(self, columns: list = None):
        # if columns = None, then set columns to all fields on table
        if columns is None:
            for c in self._table_fields:
                if c.datatype == 'CompoundVector':
                    pass
                elif '.' in c.name and c.key == 'N':
                    pass
                elif c.datatype == 'Reference' and c.key == 'N':
                    pass
                else:
                    self.columns.append(c)
            # self.columns = deepcopy(self._table_fields)
        else:
            # check whether columns provided includes all key fields
            for k in self._key_fields:
                if k not in columns:
                    raise DataError(k, 'key column not in column list: ' + str(k))

            # add all valid fields to DataTable Cols
            for c in columns:
                col = None
                try:
                    col = self.get_field(c)
                except DataError:
                    if self.environment.data_model._validate_fully_qualified_field_name(self._table_name, c):
                        col = Column(c, 'String', 'N',None)
                finally:
                    if col.datatype == 'CompoundVector':
                        self.logger.info(col.name + ' skipped due to type CompoundVector')
                        pass
                    elif col.datatype == 'Reference':
                        self.columns.append(col)
                    else:
                        self.columns.append(col)
            # add fields to columns

    def set_filter(self, value: str):
        # check filter is valid for table
        self._filter = value

    def indexof(self, rec):
        return self._table_data.index(rec)

    def del_row(self, rec):
        index = self.indexof(rec)
        self.__delitem__(index)

    def _create_export(self, session):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/bulkread_rest.htm?
        local_query_fields = []
        if self._filter:
            query_filter = self._filter
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
            "Scenario": self.scenario,
            "Table": table,
            "Fields": local_query_fields,
            "Filter": query_filter
        })

        headers = self.environment.global_headers
        headers['Content-Type'] = 'application/json'
        url = self.environment._base_url + "/integration/V1/bulk/export"

        req = requests.Request("POST", url, headers=headers, data=payload)
        #response = requests.request("POST", url, headers=headers, data=payload)
        prepped = req.prepare()
        response = session.send(prepped)

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

    def _get_export_results(self, session, startRow: int = 0, pageSize: int = 5000):
        # using slicing on the query handle to strip off the #
        url = self.environment._base_url + "/integration/V1/bulk/export/" + self.exportID[1:] + "?startRow=" + str(
            startRow) + "&pageSize=" + str(pageSize) + "&delimiter=%09" + "&finishExport=false"
        # print(url)

        headers = self.environment.global_headers
        # print(url)
        # print(headers)
        req = requests.Request("GET", url, headers=headers)
        prepped = req.prepare()
        response = session.send(prepped)
        #response = requests.request("GET", url, headers=headers)

        # check on response = 200 or whatever
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, "failure during get bulk//export results, status not 200")

        #for rec in response_dict["Rows"]:
        #    returned = rec.split('\t')
        #    self._table_data.append(DataRow(returned, self))
        rows = []
        for rec in response_dict["Rows"]:
            returned = rec.split('\t')
            rows.append(DataRow(returned, self))
        return rows

    async def _get_export_results_async(self, client, startRow: int = 0, pageSize: int = 5000):
        # using slicing on the query handle to strip off the #
        url = self.environment._base_url + "/integration/V1/bulk/export/" + self.exportID[1:] + "?startRow=" + str(
            startRow) + "&pageSize=" + str(pageSize) + "&delimiter=%09" + "&finishExport=false"
        # print(url)
        rows = []
        headers = self.environment.global_headers
        # print(url)
        # print(headers)
        response = await client.get(url=url, headers=headers)

        # check on response = 200 or whatever
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, "failure during get bulk//export results, status not 200")

        for rec in response_dict["Rows"]:
            returned = rec.split('\t')
            rows.append(DataRow(returned, self))
        return rows

    async def _main_get_export_results_async(self, data_range):
        tasks = []
        client = httpx.AsyncClient()
        for i in range(0, self.total_row_count-data_range, data_range):
            tasks.append(asyncio.Task(self._get_export_results_async(client, i, data_range)))
        #data = await asyncio.gather(*tasks)
        #self._table_data = list(data)
        for coroutine in asyncio.as_completed(tasks):
            self._table_data.extend(await coroutine)

        remaining_records = self.total_row_count % data_range
        if remaining_records > 0:
            self._table_data.extend(await self._get_export_results_async(client, self.total_row_count - remaining_records, data_range))
        await client.aclose()

    def RefreshData(self, data_range: int = 5000):
        # check tablename is set, check fields are set
        s = requests.Session()
        self.environment.refresh_auth()

        self._table_data.clear()
        self._create_export(s)
        for i in range(0, self.total_row_count, data_range):
            self._table_data.extend(self._get_export_results(s, i, data_range))
        self.exportID = None
        s.close()

    def RefreshData_async(self, data_range: int = 5000):
        self._table_data.clear()
        self.environment.refresh_auth()
        # initialise_for_extract query
        s = requests.Session()
        self._create_export(s)
        s.close()
        asyncio.run(self._main_get_export_results_async(data_range))
        self.exportID = None

        '''remaining_records = self.total_row_count % data_range
        if remaining_records > 0:
            s = requests.Session()
            self._create_export(s)
            self._table_data.extend(
                self._get_export_results(s, self.total_row_count - remaining_records, data_range))
            self.exportID = None'''

    def add_row(self, rec):
        self.environment.refresh_auth()
        self._create_upload(rec)
        self._complete_upload()
        self.uploadId = None

    def add_rows(self, rows: list):
        self.environment.refresh_auth()
        for i in range(0, len(rows), 500_000):
            self._create_upload(*rows)
            self._complete_upload()
            self.uploadId = None

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
            'Scenario': self.scenario,
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
                                "failure during bulk//upload create, status not 200" + '\nurl:' + url)
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
        self.logger.info(response_readable)
        self.logger.info(response_dict)

        if results['Status'] == 'Failure':
            self.logger.error(response_readable)
            self.logger.error(response_dict)
            raise RequestsError(response.text, "failure during bulk upload complete")
        elif results['Status'] == 'Partial Success' and results['ErrorRowCount'] > 10:
            self.logger.error(response_readable)
            self.logger.error(response_dict)
            raise DataError(response.text, "Partial Success during bulk upload complete, error count: " + str(results['ErrorRowCount']))
        else:
            self.logger.info(response_readable)
            self.logger.info(response_dict)

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
            'Scenario': self.scenario,
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
                                "failure during bulk//upload create, status not 200" + '\nurl:' + url)
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
        response_readable = 'status: ' + results['Status'] + '\nInsertedRowCount: ' + str(
            results['InsertedRowCount']) + '\nModifiedRowCount: ' + str(
            results['ModifiedRowCount']) + '\nDeleteRowCount: ' + str(
            results['DeleteRowCount']) + '\nErrorRowCount: ' + str(
            results['ErrorRowCount']) + '\nUnchangedRowCount: ' + str(results['UnchangedRowCount'])
        self.logger.info(response)
        self.logger.info(response_readable)
        self.logger.info(response_dict)

        if results['Status'] == 'Failure':
            self.logger.error(response_readable)
            self.logger.error(response_dict)
            raise RequestsError(response.text, "failure during bulk delete complete")

class DataRow(list):
    # Can only be initialised from DataTable, therefore no need to validate its a good record on creation.
    def __init__(self, iterable, data_table: DataTable):
        # initialises a new instance DataRow(['GP', '0', '7000vE', '2017-08-31'], IndependentDemand)

        # grab the necessary info from owning table
        self._data_table = data_table

        # perform validations
        if not isinstance(data_table, DataTable):
            raise TypeError("The parameter data_table type must be DataTable.")
        if len(iterable) == len(self._data_table.columns):
            super().__init__(str(item) for item in iterable)
        else:
            raise DataError(str(iterable), 'mismatch in length of data table columns '+ str(len(self._data_table.columns)) +  ' and row: ' + str(len(iterable)))

    def __setitem__(self, index, item):
        # assign a new value using the item’s index, like a_list[index] = item

        # when something is updated it should be pushed back to RR, if datatable is sync
        super().__setitem__(index, str(item))
        if self._data_table._sync:
            self._data_table.add_row(self)
        else:
            pass

    @property
    def columns(self):
        return self._data_table.columns

    def insert(self, index, item):
        # allows you to insert a new item at a given position in the underlying list using the index.
        raise NotImplementedError
        # todo implement insert
        # when something is updated it should be pushed back to RR, if datatable is sync
        # however should not fire when data is being initialised from RR
        super().insert(index, str(item))

    def append(self, item):
        # adds a single new item at the end of the underlying list
        raise NotImplementedError
        if len(self)+1 == len(self._data_table.columns):
            super().append(str(item))
        else:
            raise DataError(item, "cannot append as num of cols does not match length of new rec")
        # validate on append
        # write this back to RR?

    def extend(self, other):
        # adds a series of items to the end of the list.
        raise NotImplementedError
        if len(self)+len(other) == len(self._data_table.columns):
            if isinstance(other, type(self)):
                super().extend(other)
            else:
                super().extend(str(item) for item in other)
        else:
            raise DataError(other, "cannot append as num of cols does not match length of new rec")
        # validate on append
        # write this back to RR?

    def __add__(self, other):

        raise NotImplementedError

    def __radd__(self, other):

        raise NotImplementedError

    def __iadd__(self, other):

        raise NotImplementedError

    def join(self, separator=" "):
        # concatenates all the list’s items in a single string
        return separator.join(str(item) for item in self)

    def map(self, action):
        # yields new items that result from applying an action() callable to each item in the underlying list
        return type(self)(action(item) for item in self)

    def filter(self, predicate):
        # yields all the items that return True when calling predicate() on them
        return type(self)(item for item in self if predicate(item))

    def for_each(self, func):
        # calls func() on every item in the underlying list to generate some side effect.
        for item in self:
            func(item)

    def pre_process(self, input):
        # todo implement this
        # key purpose of this method is to handle the date messiness.
        ''' if datatype is date or datetime then convert
        past to 01/01/1970
        future to 31/12/9999
        current to time.now()
        undefined to
        '''
        output = str(input)
        return output
