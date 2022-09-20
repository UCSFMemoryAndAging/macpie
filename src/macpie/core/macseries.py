from typing import ClassVar, List

import numpy as np
import pandas as pd

from macpie._config import get_option
from macpie.pandas.select import get_col_name
from macpie.tools import itertools, lltools, strtools
from macpie.util.decorators.method import MethodHistory


class MacSeries(pd.Series):
    _metadata = [
        "is_key",
        "is_sys",
        "_tags",
    ]

    def __init__(
        self,
        data=None,
        is_key=False,
        is_sys=False,
        tags=None,
        **kwargs,
    ):
        self.is_key = is_key
        self.is_sys = is_sys
        self.tags = tags

        super().__init__(data, **kwargs)

    def __setattr__(self, attr, val):
        if attr in ("tags"):
            object.__setattr__(self, attr, val)
        else:
            super().__setattr__(attr, val)

    @property
    def tags(self):
        """Tag(s) of MacSeries."""
        return self._tags

    @tags.setter
    def tags(self, val):
        if val is None:
            self._tags = []
        else:
            self._tags = list(val)

    @property
    def _constructor(self):
        return MacSeries

    @property
    def _constructor_expanddim(self):
        from macpie.core.dataset import Dataset

        return Dataset
