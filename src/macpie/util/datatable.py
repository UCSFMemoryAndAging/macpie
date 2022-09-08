import collections
import itertools

from macpie.tools import lltools


class DataTable(collections.UserList):
    """
    A list of of equal-sized lists.

    Parameters
    ----------
    axis : int, Default is 0
        Axis the lists belong to (as rows if axis=0, or columns if axis=1)
    fillvalue : optional, default is None
        If lists are unequally sized, fill in missing values with `fillvalue`.

    Examples
    --------
    Constructing a DataTable.

    >>> dt = mp.util.DataTable(data=[[1, 2], [4, 5, 6]])
    >>> dt
    DataTable(data=[[1, 2, None], [4, 5, 6]])
    >>> dt = mp.util.DataTable(data=[[1, 2, 3], [4, 5, 6]], axis=1)
    >>> dt
    DataTable(data=[[1, 4], [2, 5], [3, 6]])

    Transposing the data.

    >>> dt = mp.util.DataTable(data=[[1, 2, 3], [4, 5, 6]])
    >>> dt.data
    [[1, 2, 3], [4, 5, 6]]
    >>> dt.transpose()
    >>> dt.data
    [[1, 4], [2, 5], [3, 6]]
    """

    def __init__(self, data, axis=0, fillvalue=None):
        if data is None:
            super().__init__([[]])
        else:
            if axis == 0:
                data = list(map(list, lltools.make_same_length(*data, fillvalue=fillvalue)))
            else:
                data = list(map(list, itertools.zip_longest(*data, fillvalue=fillvalue)))
            super().__init__(data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" f"data={self.data!r})"

    def transpose(self):
        """Transpose the list of lists."""
        self.data = list(map(list, zip(*self.data)))

    @classmethod
    def from_df(cls, df):
        return cls(df.to_numpy().tolist(), axis=0)

    @classmethod
    def from_seqs(cls, *seqs, axis=0, fillvalue=None):
        """
        Create from one or more sequencs.

        Parameters
        ----------
        seqs : sequences
        axis : {0='rows', 1='columns'}, default 1
            The axis ``seqs`` belong to.
        fillvalue : optional, default: None
            Value to fill missing items with (if seqs are of uneven length.)
        """

        return cls(seqs, axis=axis, fillvalue=fillvalue)
