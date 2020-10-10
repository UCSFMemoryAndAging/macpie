class DateProximityError(ValueError):
    """
    Error raised when problems arise during DateProximity
    merging due to problems with input data. Subclass of `ValueError`.
    """


class FileImportError(Exception):
    def __init__(self, message):
        self.message = message


class WriteError(Exception):
    def __init__(self, message):
        self.message = message
