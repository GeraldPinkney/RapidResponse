# Table.py
import collections
from typing import Literal

from RapidResponse.RapidResponse.Err import DataError

# Column = collections.namedtuple('Column', ['name', 'datatype', 'key', 'referencedTable', 'referencedNamespace', 'identification_fields'])
Column = collections.namedtuple('Column', ['name', 'datatype', 'key'])

class Table:
    TABLE_TYPE = Literal['Input', 'Calculated']

    def __init__(self, name: str, namespace: str, table_type: TABLE_TYPE = 'Input', keyed: str = None,
                 identification_fields: str = None):
        self._table_fields = []
        self._key_fields = []

        self._table_name = name
        self._table_namespace = namespace
        self._table_type = table_type
        self._keyed = keyed
        self._identification_fields = identification_fields

    def __repr__(self):
        return f'Table(name={self._table_namespace + "::" + self._table_name!r}, fields={self._table_fields!r}, type={self._table_type!r}, keyed={self._keyed!r}, identification fields={self._identification_fields!r})'

    def __eq__(self, other):
        """
        check equality based off namespace::table\n
        :param other: needs properties of _table_namespace and _table_name. does not typecheck for it being of type Table
        :return: boolean
        """
        full_name = self._table_namespace + "::" + self._table_name
        if other._table_namespace + "::" + other._table_name == full_name:
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
            raise TypeError('The parameter field type must be Column')
        if not field:
            raise ValueError('The parameter field must be provided')

        self._table_fields.append(field)
        if field.key == 'Y':
            self._key_fields.append(field.name)

    def add_fields(self, *fields):
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
        if response:
            return response
        else:
            raise DataError(name, "field: " + name + " not found in table fields.")
