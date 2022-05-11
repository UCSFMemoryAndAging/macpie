import pandas as pd

from . import general_ser


@pd.api.extensions.register_series_accessor("mac")
class MacSeriesAccessor:
    """
    Custom Series accessor to extend the :class:`pandas.Series` object.
    This creates an additional namepace on the Series object called ``mac``.
    """

    def __init__(self, ser):
        self._validate(ser)
        self._ser = ser

    @staticmethod
    def _validate(obj):
        pass

    def remove_trailers(self, predicate=None, remove_na=True):
        """see :meth:`macpie.pandas.remove_trailers`"""
        return general_ser.remove_trailers(self._ser, predicate=predicate, remove_na=remove_na)
