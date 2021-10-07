class MACPieException(Exception):
    """MACPie common exception."""


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
