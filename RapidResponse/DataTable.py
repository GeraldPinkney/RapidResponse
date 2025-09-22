# DataTable.py

import asyncio
import json
import logging
from collections import UserList
from copy import deepcopy

import httpx
import requests

from RapidResponse.DataModel import Column, Table
from RapidResponse.Environment import Environment
from RapidResponse.Utils import RequestsError, DataError


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

        tabarray = tablename.split('::')
        try:
            super().__init__(tabarray[1], tabarray[0])
        except IndexError:
            raise ValueError('table name parameter must be in format namespace::tablename')

        # set values from parameters
        self.environment = environment
        self._filter = table_filter
        self._sync = bool(sync)

        self._total_row_count = 0 # _total_row_count used during export data gathering
        # initialise internal variables to be used later
        self._uploadId = None
        self._exportID = None
        self._table_data = list()
        self.columns = list()


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
            self.scenario = scenario

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

        self._session = requests.Session()
        self.environment.refresh_auth()
        self._session.headers = self.environment.global_headers

        if refresh:
            self.RefreshData_async()

    def __bool__(self):
        return len(self._table_data) > 0


    def __len__(self):
        return len(self._table_data)

    def __eq__(self, other):
        return super().__eq__(other)

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
               f'columns={[col.name for col in self.columns]!r}, filter={self._filter!r}, sync={self.sync!r}) '

    def __str__(self):
        # return self and first 5 rows
        response = self.__repr__() + '\n'
        if self._total_row_count > 5:
            for i in range(0, 5):
                response = response + 'rownum: ' + str(i) + ' ' + str(self._table_data[i]) + '\n'
            response = response + '...'
        return response

    def __setitem__(self, key, value):
        if not isinstance(value, DataRow):
            self._table_data[key] = DataRow(value, self)
        else:
            self._table_data[key] = value
        if self.sync:
            self.environment.refresh_auth()
            self._create_upload(self._table_data[key])
            self._complete_upload()
            self._uploadId = None

    def __delitem__(self, key):

        if self.sync:
            # delete from RR
            self._create_deletion(self._table_data[key])
            self._complete_deletion()
            self._uploadId = None

        del self._table_data[key]
        self._total_row_count -= 1

    def map(self, action):
        """
        yields new items that result from applying an action() callable to each item in the underlying list
        :param action:
        :return:
        """
        #
        return type(self)(action(item) for item in self._table_data)

    def for_each(self, func):
        """
        calls func() on every item in the underlying list to generate some side effect.
        :param func: who knows...
        """
        #
        for item in self._table_data:
            func(item)

    def append(self, values):
        """
        adds a single new item at the end of the underlying list
        :param values:
        """
        #
        if not isinstance(values, DataRow):
            values = DataRow(values, self)
        if self.sync:
            self.add_row(values)

        self._table_data.append(values)
        self._total_row_count += 1

    def extend(self, args):
        to_send = []
        for rec in args:
            if isinstance(rec, DataRow):
                to_send.append(rec)
            else:
                to_send.append(DataRow(rec, self))
        self._table_data.extend(to_send)
        if self.sync:
            self.add_rows(to_send)
        self._total_row_count += len(args)

    def explode_reference_field(self, col: Column, running_list_of_cols: list = None):
        """
        recursive algo that explodes fields.
        :param col: input should look like Column(name='Header.Category', datatype='Reference', key='Y', referencedTable='HistoricalDemandHeader', referencedTableNamespace='Mfg', identification_fields=None, correspondingField=None, correspondingFieldNamespace=None)
        :param running_list_of_cols: list containing cols (added to)
        :return: running_list_of_cols
        """
        #
        if running_list_of_cols is None:
            running_list_of_cols = list()
        # basecase, if its not a reference field just return the column
        if col.datatype != 'Reference':
            running_list_of_cols.append(col)
            return running_list_of_cols
        # get the keys of the table that the column belongs to, then add each of those values to the response

        else:
            tab = self.environment.get_table(col.referencedTable, col.referencedTableNamespace)
            if tab.keyed == 'Y':
                for c in tab.fields:
                    if c.key == 'Y':
                        key_col = Column(name=col.name + '.' + c.name,
                                         datatype=c.datatype,
                                         key=c.key,
                                         referencedTable=c.referencedTable,
                                         referencedTableNamespace=c.referencedTableNamespace,
                                         identification_fields=c.identification_fields,
                                         correspondingField=c.correspondingField,
                                         correspondingFieldNamespace=c.correspondingFieldNamespace,
                                         # modified the below. previously was fieldNamespace=c.fieldNamespace. issue was that if nested then did not work
                                         fieldNamespace=col.fieldNamespace)
                        self.explode_reference_field(key_col, running_list_of_cols)

        # print(running_list_of_cols)
        return running_list_of_cols

    def _assign_all_cols(self):
        cols_to_add = list()
        for c in self._table_fields:
            if c.datatype == 'CompoundVector':
                self._logger.info(c.name + ' skipped due to type CompoundVector')
            elif '.' in c.name and c.key == 'N':
                self._logger.info(c.name + ' skipped as non key reference')
            elif c.datatype == 'Reference' and c.key == 'N':
                self._logger.info(c.name + ' skipped as non key reference')
            elif c.datatype == 'Reference' and c.key == 'Y':
                cols = self.explode_reference_field(c)
                if len(cols) > 1:
                    cols_to_add.extend(cols)
                elif len(cols) == 1:
                    cols_to_add.append(cols[0])
                else:
                    pass
            else:
                cols_to_add.append(c)
        # print(cols_to_add)
        self._logger.info(f'cols to add: {[c.name for c in cols_to_add]}')
        self.columns.extend(cols_to_add)

    def _assign_cols_from_input(self, columns):
        if self.sync:  # previously this checked for self.sync
            for k in self._key_fields:
                if k not in columns:
                    self._logger.debug(f'key column not in column list: {str(k)}')
        cols_to_add = list()
        for c in columns:
            col = self.get_field(c)
            if col is None:
                pass
            elif col.datatype == 'CompoundVector':
                self._logger.info(str(col) + ' skipped due to type CompoundVector')
                pass
            elif col.datatype == 'Reference' and col.key == 'Y':
                cols = self.explode_reference_field(col)
                if len(cols) > 1:
                    for exploded_col in cols:
                        if exploded_col not in cols_to_add:
                            cols_to_add.append(exploded_col)
                elif len(cols) == 1:
                    if cols[0] not in cols_to_add:
                        cols_to_add.append(cols[0])
            elif col.datatype == 'Reference' and col.key == 'N':
                if col not in cols_to_add:
                    cols_to_add.append(col)
            else:
                if col not in cols_to_add:
                    cols_to_add.append(col)
        self._logger.info(f'cols to add: {[c.name for c in cols_to_add]}')
        self.columns.extend(cols_to_add)

    def set_columns(self, columns: list = None):
        """
        If columns = None, then set columns to all fields on table and explode out any columns that are references and key.
        If list of columns is provided, add any key cols if they are missing (done via the DataError), check the field is valid,

        :param columns: nullable list of columns to initialise table with ['Order.Id', 'Order.Site.Value', 'Order.Type.ControlSet.Value', 'Order.Type', 'Line', 'Part.Name', 'Part.Site','DueDate', 'Quantity']
        :returns None:
        :raises DataError: if keys are missing from table, or column is not valid
        """

        if columns is None:
            self._assign_all_cols()
        else:
            # add all valid fields to DataTable Cols
            self._assign_cols_from_input(columns)

    @property
    def sync(self):
        return self._sync

    @property
    def max_connections(self):
        return self.environment.max_connections

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, new_filter):
        self._filter = str(new_filter)

    @property
    def scenario(self):
        return self._scenario

    @scenario.setter
    def scenario(self, new_scenario):
        try:
            self._scenario = dict({"Name": new_scenario['Name'], "Scope": new_scenario['Scope']})
        except AttributeError:
            raise ValueError(f"scenario not valid:  {new_scenario}. provide Name, Scope")

    def indexof(self, rec):
        return self._table_data.index(rec)

    def del_row(self, rec):
        index = self.indexof(rec)
        self.__delitem__(index)

    def _create_export(self, session=None):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/bulkread_rest.htm?
        if session is None:
            session = self._session

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
        self._total_row_count = response_dict["TotalRows"]

    def _get_export_results(self, session, startRow: int = 0, pageSize: int = 5000):
        if session is None:
            session = self._session
        # using slicing on the query handle to strip off the #
        url = self.environment.bulk_export_url + "/" + self._exportID[1:] + "?startRow=" + str(startRow) + "&pageSize=" + str(pageSize) + "&delimiter=%09" + "&finishExport=false"

        req = requests.Request("GET", url, headers=self.environment.global_headers)
        prepped = req.prepare()
        response = session.send(prepped)

        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {url}", None)

        # data returned with tab delimiter %09. split results.
        rows = [DataRow(rec.split('\t'), self) for rec in response_dict["Rows"]]
        return rows

    def RefreshData(self, data_range: int = 100_000, action_on_page=None):
        """
        Function that sequentially reads pages of response data from table read. will apply the action_on_page function to the returned data
        :param data_range: integer, requested page size. note, this is not the page size you'll get, but is adjusted by pagesizefactor
        :param action_on_page: function, function passed to RefreshData that is applied to each returned page
        :return: None
        """

        s = self._session
        self.environment.refresh_auth()
        s.headers=self.environment.global_headers

        self._create_export(s)
        self._table_data.clear()
        calc_data_range = self._calc_optimal_pagesize(data_range)
        for i in range(0, self._total_row_count, calc_data_range):
            page_response = self._get_export_results(s, i, calc_data_range)
            self._table_data.extend(page_response)
            if action_on_page is None:
                pass
            else:
                action_on_page(page_response)
        self._exportID = None
        s.close()

    async def _create_export_async(self, client, limit: asyncio.Semaphore = None):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/bulkread_rest.htm?
        url = self.environment.bulk_export_url

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
        self._logger.debug(f'Create Export payload sent is: {payload}')
        try:
            async with limit:
                response = await client.post(url=url, headers=self.environment.global_headers, content=payload)
        except:
            raise RequestsError(response, f"error during POST to: {url}", payload)
        else:
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                self._exportID = response_dict["ExportId"]
                self._total_row_count = response_dict["TotalRows"]
            else:
                raise RequestsError(response, f"error during POST to: {url}", payload)

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
        # temporary fix due to not getting released
        limit = asyncio.Semaphore(self.max_connections)

        # set exportID and totrowcount
        await self._create_export_async(self.client, limit)

        for i in range(0, self._total_row_count - data_range, data_range):
            # tasks.append(asyncio.Task(self._get_export_results_async(self.client, i, data_range, self.environment.limit)))
            tasks.append(asyncio.Task(self._get_export_results_async(self.client, i, data_range, limit)))
        for coroutine in asyncio.as_completed(tasks):
            self._table_data.extend(await coroutine)

        remaining_records = self._total_row_count % data_range
        if remaining_records > 0:
            self._table_data.extend(
                await self._get_export_results_async(self.client, self._total_row_count - remaining_records, data_range,
                                                     limit))
        # can I close client here? No. Need to shift this to environment level for client and limit
        await self.client.aclose()

    def RefreshData_async(self, data_range: int = None):
        # calc or assign the pagesize
        if data_range is None:
            calc_data_range = self._calc_optimal_pagesize(500_000)
        else:
            calc_data_range = self._calc_optimal_pagesize(data_range)
        #prepare for data refresh
        self._table_data.clear()
        self.environment.refresh_auth()
        # initialise_for_extract query
        asyncio.run(self._main_get_export_results_async(calc_data_range))
        self._exportID = None

    def _format_response(self, response_dict):
        """
        Formats a dictionary containing webservice call operation results into a human-readable string.

        Args:
            response_dict (dict): A dictionary with a 'Results' key, where the value
                                  is a dictionary containing webservice call operation counts.

        Returns:
            str: A formatted string showing the status and row counts of the operation.
        """
        response_readable = (
            f"status: {response_dict.get('Status', 'N/A')}\n"
            f"InsertedRowCount: {response_dict.get('InsertedRowCount', 'N/A')}\n"
            f"ModifiedRowCount: {response_dict.get('ModifiedRowCount', 'N/A')}\n"
            f"DeleteRowCount: {response_dict.get('DeleteRowCount', 'N/A')}\n"
            f"ErrorRowCount: {response_dict.get('ErrorRowCount', 'N/A')}\n"
            f"UnchangedRowCount: {response_dict.get('UnchangedRowCount', 'N/A')}"
        )
        self._logger.info(response_readable)
        return response_readable

    def _calc_optimal_pagesize(self, PageSizeSuggested=500_000):
        '''
        take the proposed pagesize, and modify it based off the number of chunky datatypes in the table.
        :param PageSizeSuggested: requsted pagesize that is mutliplied by the pagesizefactor to get the action pagesize
        :return PageSize: the optimal pagesize based on number of cols and datatypes
        '''

        pageSizeFactor = 1000
        if PageSizeSuggested < 5000:
            PageSize = PageSizeSuggested
        else:
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
                    self._logger.warning(
                        f"datatype: {c.datatype} not expected. reduce factor by 50 & find out what this is")
                    pageSizeFactor = pageSizeFactor - 50

            if pageSizeFactor < 1:
                PageSize = 5000
            else:
                pageSizeFactor = pageSizeFactor / 1000
                PageSize = PageSizeSuggested * pageSizeFactor
        self._logger.debug(f'pageSizeFactor: {pageSizeFactor}, PageSize: {PageSize}')
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

        # local_query_fields = [f.name for f in self.columns]
        local_query_fields = [f.name if self._table_namespace == self.get_field(
            f.name).fieldNamespace else f.fieldNamespace + '::' + f.name for f in self.columns]
        # local_query_fields = [f.name if self._table_namespace == self.get_field(f.name).fieldNamespace else f.fieldNamespace + '::' + f.name for f in self.columns]
        # local_query_fields = [f.name if self._table_namespace == f.fieldNamespace else f.fieldNamespace + '::' + f.name for f in self.columns]
        rows = [{"Values": i.data} for i in args]

        payload = json.dumps({
            'Scenario': self.scenario,
            'Table': table,
            'Fields': local_query_fields,
            'Rows': rows
        })
        self._logger.debug(f'Create Upload payload: {payload}')
        response = requests.request("POST", self.environment.bulk_upload_url, headers=self.environment.global_headers, data=payload)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {self.environment.bulk_upload_url}", payload)
        self._uploadId = response_dict["UploadId"]

    def _complete_upload(self):
        url = f'{self.environment.bulk_upload_url}/{self._uploadId[1:]}/complete'
        response = requests.request("POST", url, headers=self.environment.global_headers)

        # check valid response
        if response.status_code == 200:
            response_dict = json.loads(response.text)
        else:
            raise RequestsError(response, f"error during POST to: {url}")
        results = response_dict['Results']
        response_readable = self._format_response(results)
        if results['Status'] == 'Failure':
            raise RequestsError(response,
                                f"Status is Failure during bulk upload complete. error during POST to: {url}. {response.text}",
                                None)
        elif results['Status'] == 'Partial Success' and results['ErrorRowCount'] > 10:
            raise DataError(response.text,
                            f"Status is Partial Success during bulk upload complete, error count: {str(results['ErrorRowCount'])}")
        else:
            self._logger.debug(response_readable)

    def _create_deletion(self, *args):
        # https://help.kinaxis.com/20162/webservice/default.htm#rr_webservice/external/update_rest.htm?
        table = {'Namespace': self._table_namespace,
                 'Name': self._table_name}

        # local_query_fields = [f.name for f in self.columns]
        local_query_fields = [f.name if self._table_namespace == self.get_field(
            f.name).fieldNamespace else f.fieldNamespace + '::' + f.name for f in self.columns]

        rows = [{"Values": i.data} for i in args]

        payload = json.dumps({
            'Scenario': self.scenario,
            'Table': table,
            'Fields': local_query_fields,
            'Rows': rows
        })
        self._logger.debug(f'Create Deletion payload: {payload}')
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
            raise RequestsError(response, f"Failure during bulk//deletion complete. Error during POST to: {url}", None)

        results = response_dict['Results']
        response_readable = self._format_response(results)
        if results['Status'] == 'Failure':
            raise RequestsError(response, f"Error during bulk//deletion complete. Error during POST to: {url}", None)
        elif results['Status'] == 'Success':
            pass
            # self._logger.debug(response_readable)
        else:
            self._logger.warning(response_readable)

    def get_field(self, field):
        """
        get_field( 'Order.Site.Value')
        take as input a fieldname, can be qualified
        :param field: 'Order.Site.Value'
        :return Column:
        """
        try:
            response = super(self.__class__, self).get_field(field)
        except DataError:
            self._logger.debug(
                'Caught data error when trying to get from Table object, now using data model to get field. using get_field()')
            if self.environment.data_model._validate_fully_qualified_field_name(self._table_name, field):
                response = self.environment.data_model.get_field(self.name, field)
            else:
                raise DataError(f'Invalid Field: fieldname: {field}', f'tablename {self.name}')

        return response

class DataRow(UserList):
    # Can only be initialised from DataTable, therefore no need to validate it's a good record on creation.
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
        super().__setitem__(index, str(item))
        if self._data_table.sync:
            self._data_table.add_row(self)

    def __eq__(self, other):
        return super().__eq__(other)  # and self._data_table == other._data_table

    def __getattr__(self, name):
        # method only called as fallback when no named attribute
        cls = type(self)
        try:
            Ids = [i.name for i in self.columns]
            pos = Ids.index(name.replace('_', '.'))
        except ValueError:  # exception thrown if could not find name
            pos = -1
        if 0 <= pos < len(self.columns):
            return self[pos]
        msg = f'{cls.__name__!r} object has no attribute {name!r}'
        raise AttributeError(msg)

    @property
    def columns(self):
        return self._data_table.columns

    def insert(self, index, item):
        # allows you to insert a new item at a given position in the underlying list using the index.
        raise NotImplementedError
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

