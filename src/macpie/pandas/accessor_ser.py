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

    def count_trailers(self, predicates=None, count_na=True, count_empty_string=True):
        """see :meth:`macpie.pandas.count_trailers`"""
        return general_ser.count_trailers(
            self._ser,
            predicates=predicates,
            count_na=count_na,
            count_empty_string=count_empty_string,
        )

    def remove_trailers(self, predicates=None, remove_na=True, remove_empty_string=True):
        """see :meth:`macpie.pandas.remove_trailers`"""
        return general_ser.remove_trailers(
            self._ser,
            predicates=predicates,
            remove_na=remove_na,
            remove_empty_string=remove_empty_string,
        )

    def rtrim(self, trim_empty_string=True):
        """see :meth:`macpie.pandas.rtrim`"""
        return general_ser.rtrim(self._ser, trim_empty_string=trim_empty_string)

    def rtrim_longest(self, *sers, trim_empty_string=True, as_tuple=False):
        """see :meth:`macpie.pandas.rtrim_longest`"""
        return general_ser.rtrim_longest(
            self._ser, *sers, trim_empty_string=trim_empty_string, as_tuple=as_tuple
        )
