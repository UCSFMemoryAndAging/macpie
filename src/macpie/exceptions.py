class MACPieException(Exception):
    """MACPie common exception."""


class DatasetIDColError(MACPieException):
    """
    Error raised when there is a problem with Dataset.id_col.
    """


class DatasetIDColDuplicateError(DatasetIDColError):
    """
    Error raised when there are duplicates in Dataset.id_col.
    """


class DatasetDateColError(MACPieException):
    """
    Error raised when there is a problem with Dataset.date_col.
    """


class DatasetID2ColError(MACPieException):
    """
    Error raised when there is a problem with Dataset.id2_col.
    """


class DatasetIDColKeyError(KeyError):
    """
    Error raised when there is a problem with Dataset.id_col.
    Subclass of `KeyError`.
    """


class DatasetDateColKeyError(KeyError):
    """
    Error raised when there is a problem with Dataset.date_col.
    Subclass of `KeyError`.
    """


class DatasetID2ColKeyError(KeyError):
    """
    Error raised when there is a problem with Dataset.id2_col.
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


class MergeableAnchoredListError(MACPieException):
    """
    Error raised in MergeableAnchoredList class
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
