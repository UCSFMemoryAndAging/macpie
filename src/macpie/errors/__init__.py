class DataObjectDateColKeyError(KeyError):
    """
    Error raised when there is a problem with DataObject.date_col.
    Subclass of `KeyError`.
    """


class DataObjectIDColKeyError(KeyError):
    """
    Error raised when there is a problem with DataObject.id_col.
    Subclass of `KeyError`.
    """


class DataObjectIDColDuplicateKeyError(DataObjectIDColKeyError):
    """
    Error raised when there are duplicates in DataObject.id_col.
    Subclass of `DataObjectIDColKeyError`.
    """


class DataObjectID2ColKeyError(KeyError):
    """
    Error raised when there is a problem with DataObject.id2_col.
    Subclass of `KeyError`.
    """


class DateProximityError(ValueError):
    """
    Error raised when problems arise during DateProximity
    merging due to problems with input data. Subclass of `ValueError`.
    """


class MergeError(ValueError):
    """
    Error raised when problems arise during DateProximity
    merging due to problems with input data. Subclass of `ValueError`.
    """


class ParserError(Exception):
    """
    Error raised when parsing file.
    """
    def __init__(self, message):
        self.message = message


class PathError(Exception):
    """
    Generic error related to :class:`pathlib.Path`
    """

    def __init__(self, message):
        self.message = message
