# DataTable.py

import json
import logging
from collections import UserList
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
    #BULK_URL = "/integration/V1/bulk/"

    def __init__(self, environment: Environment, tablename: str, columns: list = None, table_filter: str = None,
                 sync: bool = True, refresh: bool = True, scenario=None):

        # logging.basicConfig(filename='logging.log', filemode='w',format='%(name)s - %(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self._logger = logging.getLogger('RapidPy.dt')

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

        self._uploadId = None
        self._exportID = None
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
                    # self.scenario = environment.scenarios[0]
            except AttributeError:
                raise ValueError("scenario parameter format is {'Name': 'Integration', 'Scope': 'Public'} " + scenario)

        # set columns and filters
        try:
            self.set_columns(columns)
        except DataError:
            # allow this to silently error and write it to log
            # make sure all key columns are in there. non-negotiable.
            for k in self._key_fields:
                if k not in columns:
                    columns.append(k)
            self.set_columns(columns)

        timeout = httpx.Timeout(10.0, connect=60.0)
        self.client = httpx.AsyncClient(timeout=timeout)
        if refresh:
            self.RefreshData_async()

    def __bool__(self):
        if len(self._table_data) > 0:
            return True
        else:
            return False

    # todo equality operator
    def __len__(self):
        return len(self._table_data)

    def __eq__(self, other):
        return False

    def __getitem__(self, position):
        return self._table_data[position]
        # todo change this so a slice will return an instance of DataRow

    def __contains__(self, item):
        # get key fields for table. then check if that value is present
        if item in self._table_data:
            return True
        else:
            return False

    def __repr__(self):

        return f'DataTable(environment={self.environment!r},name={self._table_namespace!r}::{self._table_name!r},' \
               f'columns={[col.name for col in self.columns]!r}, filter={self._filter!r}, sync={self._sync!r}) '

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
            self._uploadId = None

    def __delitem__(self, key):

        if self._sync:
            # delete from RR
            self._create_deletion(self._table_data[key])
            self._complete_deletion()
            self._uploadId = None

        del self._table_data[key]
        self.total_row_count -= 1

    def map(self, action):
        # yields new items that result from applying an action() callable to each item in the underlying list
        return type(self)(action(item) for item in self._table_data)

    # def filter(self, predicate):
    #    # yields all the items that return True when calling predicate() on them
    #    return type(self)(item for item in self._table_data if predicate(item))

    def for_each(self, func):
        # calls func() on every item in the underlying list to generate some side effect.
        for item in self._table_data:
            func(item)

    def append(self, values):
        # adds a single new item at the end of the underlying list
        if not isinstance(values, DataRow):
            values = DataRow(values, self)
        if self._sync:
            self.add_row(values)

        self._table_data.append(values)

    # todo remove

    def extend(self, args):
        # todo fix when doing insert messy reference fields
        to_send = []
        for rec in args:
            if isinstance(rec, type(DataRow)):
                to_send.append(rec)
            else:
                to_send.append(DataRow(rec, self))
        self._table_data.extend(to_send)
        if self._sync:
            self.add_rows(to_send)

    def set_columns(self, columns: list = None):
        # if columns = None, then set columns to all fields on table
        if columns is None:
            for c in self._table_fields:
                if c.datatype == 'CompoundVector':
                    self._logger.info(c.name + ' skipped due to type CompoundVector')
                elif '.' in c.name and c.key == 'N':
                    self._logger.info(c.name + ' skipped as non key reference')
                elif c.datatype == 'Reference' and c.key == 'N':
                    self._logger.info(c.name + ' skipped as non key reference')
                else:
                    self.columns.append(c)

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
                        col = Column(c, 'String', 'N', None)
                    else:
                        self._logger.warning(col.name + ' incorrect field name')
                finally:
                    if col.datatype == 'CompoundVector':
                        self._logger.info(col.name + ' skipped due to type CompoundVector')
                        pass
                    elif col.datatype == 'Reference':
                        self.columns.append(col)
                    else:
                        self.columns.append(col)
            # add fields to columns

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, new_filter):
        self._filter = dict({"Name": new_filter['Name'], "Scope": new_filter['Scope']})

    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, new_scenario):
        # if not isinstance(new_scenario, dict):
        #    raise TypeError("The parameter scenario type must be dict.")
        # scenario_keys = new_scenario.keys()
        # if len(scenario_keys) != 2:
        #    raise ValueError("The parameter scenario must contain only Name and Scope.")
        # if 'Name' not in scenario_keys:
        #    raise ValueError("The parameter scenario must contain Name.")
        # if 'Scope' not in scenario_keys:
        #    raise ValueError("The parameter scenario must contain Scope.")
        self._scenario = dict({"Name": new_scenario['Name'], "Scope": new_scenario['Scope']})

    def indexof(self, rec):
        return self._table_data.index(rec)

    def del_row(self, rec):
        index = self.indexof(rec)
        self.__delitem__(index)

    def _create_export(self, session):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/bulkread_rest.htm?
        if self._filter:
            query_filter = self.filter
        else:
            query_filter = ''
        local_query_fields = [f.name for f in self.columns]

        table = {'Namespace': self._table_namespace,
                 'Name': self._table_name}

        payload = json.dumps({
            "Scenario": self.scenario,
            "Table": table,
            "Fields": local_query_fields,
            "Filter": query_filter
        })

        req = requests.Request("POST", self.environment.bulk_export_url , headers=self.environment.global_headers, data=payload)
        prepped = req.prepare()
        response = session.send(prepped)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {self.environment.bulk_export_url}", payload)

        self._exportID = response_dict["ExportId"]
        self.total_row_count = response_dict["TotalRows"]

    def _get_export_results(self, session, startRow: int = 0, pageSize: int = 5000):
        # using slicing on the query handle to strip off the #
        url = self.environment.bulk_export_url + "/" + self._exportID[1:] + "?startRow=" + str(startRow) + "&pageSize=" + str(pageSize) + "&delimiter=%09" + "&finishExport=false"
        # print(url)

        #headers = self.environment.global_headers
        # print(url)
        # print(headers)
        req = requests.Request("GET", url, headers=self.environment.global_headers)
        prepped = req.prepare()
        response = session.send(prepped)
        # response = requests.request("GET", url, headers=headers)

        # check on response = 200 or whatever
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {url}", None)

        # data returned with tab delimiter %09. split results.
        rows = [DataRow(rec.split('\t'), self) for rec in response_dict["Rows"]]
        return rows

    def RefreshData(self, data_range: int = 100_000):
        # check tablename is set, check fields are set
        s = requests.Session()
        self.environment.refresh_auth()
        self._table_data.clear()
        self._create_export(s)
        calc_data_range = self._calc_optimal_pagesize(data_range)
        for i in range(0, self.total_row_count, calc_data_range):
            self._table_data.extend(self._get_export_results(s, i, calc_data_range))
        self._exportID = None
        s.close()

    async def _get_export_results_async(self, client, startRow: int = 0, pageSize: int = 5000, limit: asyncio.Semaphore = None):
        url = self.environment.bulk_export_url + "/" + self._exportID[1:] + "?startRow=" + str(startRow) + "&pageSize=" + str(pageSize) + "&delimiter=%09" + "&finishExport=false"
        if limit:
            async with limit:
                response = await client.get(url=url, headers=self.environment.global_headers)
                if limit.locked():
                    self._logger.info("Concurrency limit reached, waiting ...")
                    await asyncio.sleep(1)
        else:
            response = await client.get(url=url, headers=self.environment.global_headers)

        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during GET to: {url}", None)

        # data returned with tab delimiter %09. split results.
        rows = [DataRow(rec.split('\t'), self) for rec in response_dict["Rows"]]
        return rows

    async def _main_get_export_results_async(self, data_range):
        tasks = []

        for i in range(0, self.total_row_count - data_range, data_range):
            tasks.append(asyncio.Task(self._get_export_results_async(self.client, i, data_range, self.environment.limit)))
        for coroutine in asyncio.as_completed(tasks):
            self._table_data.extend(await coroutine)

        remaining_records = self.total_row_count % data_range
        if remaining_records > 0:
            self._table_data.extend(
                await self._get_export_results_async(self.client, self.total_row_count - remaining_records, data_range, self.environment.limit))
        await self.client.aclose()

    def RefreshData_async(self, data_range: int = None):
        # calc or assign the pagesize
        # todo implement this as a queue with retries https://github.com/rednafi/think-async/blob/master/patterns/limit_concurrency_on_queue.py
        if data_range is None:
            calc_data_range = self._calc_optimal_pagesize(500_000)
        else:
            calc_data_range = data_range
        #prepare for data refresh
        self._table_data.clear()
        self.environment.refresh_auth()
        # initialise_for_extract query
        s = requests.Session()
        self._create_export(s)
        s.close()
        asyncio.run(self._main_get_export_results_async(calc_data_range))
        self._exportID = None


    def _calc_optimal_pagesize(self, PageSizeSuggested=500_000):
        # todo account for rows returned
        # todo cache response to be able to use stats on string sizes
        # starting point is 100,000
        pageSizeFactor = 1000
        for c in self.columns:
            if c.datatype == 'String':
                pageSizeFactor = pageSizeFactor - 90
            elif c.datatype == 'DateTime':
                pageSizeFactor = pageSizeFactor - 75
            elif c.datatype == 'Date' or c.datatype == 'Time':
                pageSizeFactor = pageSizeFactor - 50
            elif c.datatype == 'Money' or c.datatype == 'Quantity' or c.datatype == 'Integer':
                pageSizeFactor = pageSizeFactor - 45
            elif c.datatype == 'Enum':
                pageSizeFactor = pageSizeFactor - 5
            else:
                self._logger.warning(f"datatype: {c.datatype} not expected. reduce factor by 50 & find out what this is")
                pageSizeFactor = pageSizeFactor - 50

        if pageSizeFactor < 1:
            PageSize = 5000
        else:
            pageSizeFactor = pageSizeFactor / 1000
            PageSize = PageSizeSuggested * pageSizeFactor
        self._logger.info(f'pageSizeFactor: {pageSizeFactor}, PageSize: {PageSize}')
        return round(PageSize)

    def add_row(self, rec):
        self.environment.refresh_auth()
        self._create_upload(rec)
        self._complete_upload()
        self._uploadId = None

    def add_rows(self, rows: list):
        self.environment.refresh_auth()
        pagesize = self._calc_optimal_pagesize(100_000)
        for i in range(0, len(rows), pagesize):
            self._create_upload(*rows[i:i + pagesize])
            self._complete_upload()
            self._uploadId = None

    def _create_upload(self, *args):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/update_rest.htm?
        table = {'Namespace': self._table_namespace,
                 'Name': self._table_name}

        local_query_fields = [f.name for f in self.columns]
        rows = [{"Values": i.data} for i in args]

        payload = json.dumps({
            'Scenario': self.scenario,
            'Table': table,
            'Fields': local_query_fields,
            'Rows': rows
        })

        response = requests.request("POST", self.environment.bulk_upload_url, headers=self.environment.global_headers, data=payload)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {self.environment.bulk_upload_url}", payload)
        self._uploadId = response_dict["UploadId"]

    def _complete_upload(self):
        url = self.environment.bulk_upload_url + "/" + self._uploadId[1:] + '/complete'
        response = requests.request("POST", url, headers=self.environment.global_headers)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {url}")
        results = response_dict['Results']
        response_readable = 'status: ' + results['Status'] + '\nInsertedRowCount: ' + str(
            results['InsertedRowCount']) + '\nModifiedRowCount: ' + str(
            results['ModifiedRowCount']) + '\nDeleteRowCount: ' + str(
            results['DeleteRowCount']) + '\nErrorRowCount: ' + str(
            results['ErrorRowCount']) + '\nUnchangedRowCount: ' + str(results['UnchangedRowCount'])

        if results['Status'] == 'Failure':
            raise RequestsError(response, f"error during POST to: {url}", None)
        elif results['Status'] == 'Partial Success' and results['ErrorRowCount'] > 10:
            raise DataError(response.text, "Partial Success during bulk upload complete, error count: " + str(
                results['ErrorRowCount']))
        else:
            self._logger.info(response_readable)
            self._logger.info(response_dict)

    def _create_deletion(self, *args):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/update_rest.htm?
        table = {'Namespace': self._table_namespace,
                 'Name': self._table_name}

        local_query_fields = [f.name for f in self.columns]
        rows = [{"Values": i.data} for i in args]

        payload = json.dumps({
            'Scenario': self.scenario,
            'Table': table,
            'Fields': local_query_fields,
            'Rows': rows
        })

        response = requests.request("POST", self.environment.bulk_remove_url, headers=self.environment.global_headers, data=payload)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"Failure during bulk//deletion create. Error during POST to: {self.environment.bulk_remove_url}", payload)
        self._uploadId = response_dict["RemovalId"]

    def _complete_deletion(self):

        url = self.environment.bulk_remove_url + "/" + self._uploadId[1:] + '/complete'
        response = requests.request("POST", url, headers=self.environment.global_headers)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            # print(response)
            raise RequestsError(response, f"Failure during bulk//deletion complete. Error during POST to: {url}", None)

        results = response_dict['Results']
        response_readable = 'status: ' + results['Status'] + '\nInsertedRowCount: ' + str(
            results['InsertedRowCount']) + '\nModifiedRowCount: ' + str(
            results['ModifiedRowCount']) + '\nDeleteRowCount: ' + str(
            results['DeleteRowCount']) + '\nErrorRowCount: ' + str(
            results['ErrorRowCount']) + '\nUnchangedRowCount: ' + str(results['UnchangedRowCount'])
        self._logger.info(response)
        self._logger.info(response_readable)
        self._logger.info(response_dict)

        if results['Status'] == 'Failure':
            self._logger.error(response_readable)
            self._logger.error(response_dict)
            raise RequestsError(response, f"Error during bulk//deletion complete. Error during POST to: {url}", None)

    @property
    def sync(self):
        return self._sync

    @property
    def max_connections(self):
        return self.environment.max_connections


class DataRow(UserList):
    # Can only be initialised from DataTable, therefore no need to validate its a good record on creation.
    def __init__(self, iterable, data_table: DataTable):
        # initialises a new instance DataRow(['GP', '0', '7000vE', '2017-08-31'], IndependentDemand)

        # perform validations
        if not isinstance(data_table, DataTable):
            raise TypeError("The parameter data_table type must be DataTable.")
        # grab the necessary info from owning table
        self._data_table = data_table

        if len(iterable) == len(self._data_table.columns):
            super().__init__(str(item) for item in iterable)
        else:
            raise DataError(str(iterable),
                            f'mismatch in length of data table columns {str(len(self._data_table.columns))} and row: {str(len(iterable))} ')

    def __setitem__(self, index, item):
        # assign a new value using the item’s index, like a_list[index] = item
        # when something is updated it should be pushed back to RR, if datatable is sync
        # todo check if its a reference field or calculated . then don't allow
        super().__setitem__(index, str(item))
        if self._data_table.sync:
            self._data_table.add_row(self)

    # todo equality operator def __eq__(self, other):

    def __getattr__(self, name):
        # method only called as fallback when no named attribute
        cls = type(self)
        try:
            Ids = [i.name for i in self.columns]
            pos = Ids.index(name.replace('_', '.'))
        except ValueError:  # thrown if could not find name
            pos = -1
        if 0 <= pos < len(self.columns):
            return self[pos]
        msg = f'{cls.__name__!r} object has no attribute {name!r}'
        raise AttributeError(msg)

    '''def g__setattr__(self, name, value):
        cls = type(self)

        if name in self.__dict__:
            super().__setattr__(name, value)
            return 0
        Ids = [i.name for i in self.columns]
        if name in Ids:
            pos = Ids.index(name)
            self.__setitem__(pos, value)
        else:
            error = ''
        if error:
            msg = error.format(cls_name=cls.__name__, attr_name=name)
            raise AttributeError(msg)'''

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
        if len(self) + 1 == len(self._data_table.columns):
            super().append(str(item))
        else:
            raise DataError(item, "cannot append as num of cols does not match length of new rec")
        # validate on append
        # write this back to RR?

    def extend(self, other):
        # adds a series of items to the end of the list.
        raise NotImplementedError
        if len(self) + len(other) == len(self._data_table.columns):
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

    def to_dict(self):
        """
        Convert the instance of DataRow to a dictionary.

        Returns:
            dict: Dictionary representation of the DataRow.
        """
        return {
            "_data_table": self._data_table,
            "data": [str(item) for item in self],
            "columns": [col.to_dict() for col in self.columns]  # Assuming columns have a to_dict method
        }

    def to_json(self):
        """
        Convert the instance of DataRow to a JSON string.

        Returns:
            str: JSON representation of the DataRow.
        """
        return json.dumps(self.to_dict(), default=lambda o: o.__dict__, indent=2)

    @classmethod
    def from_dict(cls, data_dict, data_table):
        """
        Create a DataRow instance from a dictionary.

        Args:
            data_dict (dict): Dictionary representation of the DataRow.
            data_table (DataTable): The owning DataTable instance.

        Returns:
            DataRow: The DataRow instance.
        """
        instance = cls([], data_table)
        instance._data_table = data_dict["_data_table"]
        instance.data = data_dict["data"]
        return instance

    @classmethod
    def from_json(cls, json_str, data_table):
        """
        Create a DataRow instance from a JSON string.

        Args:
            json_str (str): JSON representation of the DataRow.
            data_table (DataTable): The owning DataTable instance.

        Returns:
            DataRow: The DataRow instance.
        """
        data_dict = json.loads(json_str)
        return cls.from_dict(data_dict, data_table)
