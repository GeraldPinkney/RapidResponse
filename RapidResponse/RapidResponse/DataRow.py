# DataRow.py

class DataRow(list):
    # todo implement this
    # should a record care about what table it belongs to? (yes, because we need to know if table is sync)
    def __init__(self, iterable):
        # initialises a new instance
        super().__init__(str(item) for item in iterable)

    def __setitem__(self, index, item):
        # allows you to assign a new value to an existing item using the item’s index, like in a_list[index] = item

        # when something is updated it should be pushed back to RR, if datatable is sync
        # however should not fire when data is being initialised from RR
        super().__setitem__(index, str(item))

    def insert(self, index, item):
        # allows you to insert a new item at a given position in the underlying list using the index.

        # when something is updated it should be pushed back to RR, if datatable is sync
        # however should not fire when data is being initialised from RR
        super().insert(index, str(item))

    def append(self, item):
        # adds a single new item at the end of the underlying list

        # validate on append
        # write this back to RR?
        super().append(str(item))

    def extend(self, other):
        # adds a series of items to the end of the list.

        # validate on append
        # write this back to RR?
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(str(item) for item in other)

    def __add__(self, other):
        # todo implement this for concat operations with +
        pass

    def __radd__(self, other):
        # todo implement this for concat operations with +
        pass

    def __iadd__(self, other):
        # todo implement this for concat operations with +
        pass

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

    def _validate_field(self, value):
        if True:
            # add validations here and if they pass then return string of value
            return str(value)
        else:
            pass
            # use

    def set_columns(self):
        pass