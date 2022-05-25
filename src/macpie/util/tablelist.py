import collections
import itertools

from macpie.tools.listlike import make_same_length


class TableList(collections.UserList):
    """
    A list of of equal-sized lists.
    """

    def __init__(self, data, axis=0, fillvalue=None):
        if data is None:
            super().__init__([[]])
        else:
            if axis == 0:
                data = list(map(list, make_same_length(*data, fillvalue=fillvalue)))
            else:
                data = list(map(list, itertools.zip_longest(*data, fillvalue=fillvalue)))
            super().__init__(data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" f"data={self.data!r})"

    def transpose(self):
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
