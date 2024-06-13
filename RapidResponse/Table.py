# Table.py
from typing import Literal, NamedTuple, Dict
import logging
from RapidResponse.Err import DataError

# Column = collections.namedtuple('Column', ['name', 'datatype', 'key', 'referencedTable', 'identification_fields', 'RelatedTableWithNamespace'])


class Column(NamedTuple):
    # prior implementation below
    # Column = collections.namedtuple('Column', ['name', 'datatype', 'key'])
    #DATA_TYPE = Literal['String', 'Boolean', 'Date', 'DateTime', 'Integer', 'Money', 'Note', 'Quantity', 'QuantitySingle', 'Reference', 'Time', 'Vector Set']
    name: str
    datatype: str
    key: str
    #DATA_TYPE = Literal['String', 'Boolean', 'Date', 'DateTime', 'Integer', 'Money', 'Note', 'Quantity', 'QuantitySingle', 'Reference', 'Time', 'Vector Set']
    # if datatype is Reference, then
    referencedTable: str = None
    referencedTableNamespace: str = None
    identification_fields: str = None
    correspondingField: str = None
    correspondingFieldNamespace: str = None

    def __eq__(self, other):
        if other.name == self.name:
            return True
        else:
            return False

    def to_dict(self) -> Dict:
        """
        Convert the instance of Column to a dictionary.

        Returns:
            dict: Dictionary representation of the Column.
        """
        column_dict = {
            "name": self.name,
            "datatype": self.datatype,
            "key": self.key,
            "referencedTable": self.referencedTable,
            "referencedTableNamespace": self.referencedTableNamespace,
            "identification_fields": self.identification_fields,
            "correspondingField": self.correspondingField,
            "correspondingFieldNamespace": self.correspondingFieldNamespace,
        }
        return column_dict

class Table:
    TABLE_TYPE = Literal['Input', 'Calculated']

    def __init__(self, name: str, namespace: str, table_type: TABLE_TYPE = 'Input', keyed: str = None,identification_fields: str = None):
        self._logger = logging.getLogger('RapidPy.wb.tab')
        self._table_fields = []
        self._key_fields = []

        self._table_name = name
        self._table_namespace = namespace
        self._table_type = table_type
        self._keyed = keyed
        self._identification_fields = identification_fields

    def __repr__(self):
        return f'Table(name={self.name!r}, fields={self._table_fields!r}, type={self._table_type!r}, keyed={self._keyed!r}, identification fields={self._identification_fields!r})'

    def __eq__(self, other):
        """
        check equality based off namespace::table\n
        :param other: needs properties of _table_namespace and _table_name. does not typecheck for it being of type Table
        :return: boolean
        """
        #full_name = self._table_namespace + "::" + self._table_name
        if other.name == self.name:
            return True
        else:
            return False

    def _add_field(self, field: Column):
        """
        Add field to the current table and record if it's a key field\n
        :param field: The Column that will be added to the table
        :return: None
        :raises TypeError: if parameter field type is not of type Column
        :raises ValueError: if parameter field is not provided
        """
        if not isinstance(field, Column):
            raise TypeError('The parameter field type must be Column. Is type: ' + str(type(field)))
        if not field:
            raise ValueError('The parameter field must be provided')

        if field in self._table_fields:
            return 0
            # todo come back to this and work out why on earth we are trying to assign fields multiple times.
            # print('The field is already assigned to table')
        else:
            self._table_fields.append(field)
            if field.key == 'Y':
                self._key_fields.append(field.name)

    def add_fields(self, fields):
        if isinstance(fields, Column):
            self._add_field(fields)
        else:
            for f in fields:
                self._add_field(f)
        return self._table_fields

    def _remove_field(self, field: Column):
        """
        Remove field from the current table and remove  if it's a key field\n
        :param field: The Column that will be added to the table
        :return: None
        :raises TypeError: if parameter field type is not of type Column
        :raises ValueError: if parameter field is not provided
        """
        if not isinstance(field, Column):
            raise TypeError('The parameter field type must be Column')
        if not field:
            raise ValueError('The parameter field must be provided')

        if field in self._table_fields:
            self._table_fields.remove(field)
            if field.key == 'Y':
                self._key_fields.remove(field.name)
        else:
            raise ValueError('The field is not associated to the table')

    def remove_fields(self, *fields):
        """
        remove fields from table\n
        :param fields: list of fields.
        :return: None
        """
        for f in fields:
            try:
                self._remove_field(f)
            except ValueError:
                pass

    def get_field(self, name: str):
        """
        take as input the name of a column on the table and return a Column object\n
        :param name: string of the name of the column you wish to add
        :return: The Column which has the name provided
        :raises TypeError: if parameter field type is not of type Column
        :raises ValueError: if parameter field is not provided
        :raises DataError: field not found in table fields
        """
        if not isinstance(name, str):
            raise TypeError('The parameter name type must be string')
        if not str:
            raise ValueError('The parameter name must be provided')

        response = None
        for f in self._table_fields:
            if name == f.name:
                response = f
                return response
        if response:
            return response
        else:
            raise DataError(name, "field: " + name + " not found in table fields.")

    @property
    def fields(self):
        return self._table_fields

    @property
    def name(self):
        return self._table_namespace + "::" + self._table_name

    @name.setter
    def name(self, new_name):
        tabarray = new_name.split('::')
        try:
            self._table_name = tabarray[1]
            self._table_namespace = tabarray[0]
        except IndexError:
            raise ValueError('table name parameter must be in format namespace::tablename')

