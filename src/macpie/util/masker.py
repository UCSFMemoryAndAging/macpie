"""
Contains classes to help mask (i.e. de-identify) production data contained in your
files, currently PHI data contained in ID and Date columns. In the MAC Lava database,
for example, these would be any columns containing PIDNs, InstrIDs, and Dates of
Service (e.g. DCDate, VDate).

Specifically, a per-ID replacement ID and date-shift value (random number between
365 and 730) are created. Each unique ID is replaced with a unique masked ID,
and all Dates are shifted back by the random date-shift value for that
particular ID. A second set of ID columns (e.g. InstrID) can be replaced with another
set of replacement IDs as well.

Columns that are not masked by default have their column header renamed to a generic
name (e.g. Col1, Col2).

In summary, given a pandas DataFrame, these operations will be performed on the columns:

    1) ID Columns (e.g. PIDN, pidn_link) will have their IDs replaced with a set
       of masked IDs.

    2) Date Columns (e.g. DCDate, link_date) will have their dates shifted back by a
       date-shift value based on the first set of masked IDs.

    3) ID2 Columns (e.g. InstrID, link_id) will have their IDs replaced with a second
       set of masked IDs

    4) Columns in the variable COLS_TO_DROP will be dropped (i.e. removed)

    5) Remaining columns will be dentified (i.e. renamed to Col1, Col2, etc)

A dataframe can only be masked ONLY if there is at least one ID column found.

"""
import collections
import random
from typing import Dict

import pandas as pd
import tablib as tl

from macpie.tools import lltools


class Masker:
    """Masks data for pandas DataFrames.

    Parameters
    ----------
    mask_map : MaskMap
        An instance of :class:`MaskMap`
    id_col_names : str, list
        ID column names that should have their ids masked with `mask_map`
    date_col_names : str, list
        Date column names that should have their dates masked with `mask_map`
    """

    day_shift_helper_col_prefix = "__day_shift_"

    def __init__(self, mask_map, id_col_names, date_col_names=None):
        self.id_col_to_masker_map = {}
        self.date_col_to_masker_map = {}
        self.add(mask_map, id_col_names, date_col_names=date_col_names)

    def add(self, mask_map, id_col_names, date_col_names=None):
        """Add a new :class:`MaskMap` with associated `id_col_names`
        and `date_col_names`.
        """
        id_col_names = lltools.maybe_make_list(id_col_names)
        date_col_names = lltools.maybe_make_list(date_col_names)
        for id_col_name in id_col_names:
            if id_col_name in self.id_col_to_masker_map:
                raise KeyError(f"A mask for column '{id_col_name}' columns already exists.")
            else:
                self.id_col_to_masker_map[id_col_name] = mask_map
        if date_col_names:
            for date_col_name in date_col_names:
                if date_col_name in self.date_col_to_masker_map:
                    raise KeyError(f"A mask for column '{date_col_name}' columns already exists.")
                else:
                    self.date_col_to_masker_map[date_col_name] = (mask_map, id_col_names)

    def mask_df(self, df, rename_cols=True, norename_cols=None, drop_cols=None, inplace=False):
        """Perform data mask.

        Parameters
        ----------
        df : DataFrame
            The dataframe to mask
        rename_cols : bool, list, default is True
            Columns that should be renamed. If True, all columns (except masked
            columns) will be renamed
        norename_cols : list
            Columns that should not be renamed
        drop_cols : list
            Columns to drop (e.g. because they contain PHI or unnecessarily
            risky data.
        """

        if inplace:
            result = df
        else:
            result = df.copy()

        # 1. drop cols
        if drop_cols is None:
            drop_cols = []
        else:
            result.drop(columns=drop_cols, inplace=True, errors="ignore")

        # 2. mask cols
        masked_cols = []

        # 2a. mask date columns first
        for col in result.columns:
            col = col.lower()
            if col in self.date_col_to_masker_map:
                mask_map, id_col_names = self.date_col_to_masker_map[col]
                for id_col_name in id_col_names:
                    if id_col_name in result.columns:
                        break
                else:
                    # Masking a date column requires at least one id column in the same
                    # DataFrame from which to retrieve the day_shift value.
                    raise ValueError(f"No id column found to mask the date column: '{col}'")

                if not result.mac.is_date_col(col):
                    result[col] = pd.to_datetime(result[col], errors="raise")
                day_shift_helper_col_name = Masker.day_shift_helper_col_prefix + id_col_name
                if day_shift_helper_col_name not in result.columns:
                    result[day_shift_helper_col_name] = result[id_col_name].apply(
                        lambda x: pd.Timedelta(mask_map[x].day_shift, unit="d")
                        if not pd.isnull(x)
                        else None
                    )
                result[col] = result[col] - result[day_shift_helper_col_name]
                masked_cols.append(col)
        result.drop(
            columns=[
                c for c in result.columns if c.startswith(Masker.day_shift_helper_col_prefix)
            ],
            inplace=True,
        )

        # 2b. mask id columns
        for col in result.columns:
            col = col.lower()
            if col in self.id_col_to_masker_map:
                mask_map = self.id_col_to_masker_map[col]
                result[col] = result[col].apply(
                    lambda x: mask_map[x].masked_id if not pd.isnull(x) else None
                )
                masked_cols.append(col)

        # 3. rename cols
        col_rename_dict = {}
        if rename_cols is not False:
            if rename_cols is True:
                if norename_cols is None:
                    cols_not_to_rename = masked_cols
                else:
                    cols_not_to_rename = set().union(masked_cols, norename_cols)
                rename_cols = lltools.difference(result.columns.tolist(), cols_not_to_rename)
            for num, col_to_rename in enumerate(rename_cols):
                col_rename_dict[col_to_rename] = "Col" + str(num + 1)
            result.rename(columns=col_rename_dict, inplace=True)

        col_transformations = {**col_rename_dict, **dict.fromkeys(drop_cols)}

        if not inplace:
            return (result, col_transformations)
        return (None, col_transformations)


# stores the masking data for each unique, original ID
_MaskedData = collections.namedtuple("_MaskedData", "masked_id, day_shift")


class MaskMap(collections.UserDict):
    """A dict that maps IDs (ints) to a namedtuple containing the following
    named fields:

    * ``masked_id``: a replacement ID
    * ``day_shift``: a random number between 365 and 730 used to shift \
      date values backwards by

    This class is meant to be used by :class:`Masker` for masking dataframes,
    but can be used for other purposes.
    """

    def __len__(self):
        return len(self.data)

    @property
    def mask_map(self):
        return self.data

    @property
    def headers(self):
        return ["id", "masked_id", "day_shift"]

    def to_flat_rows(self):
        return [(k, v.masked_id, v.day_shift) for k, v in self.data.items()]

    def to_tablib(self, headers=True):
        """Convert to a :class:`tablib.Dataset`."""
        tlset = tl.Dataset()
        if headers:
            tlset.headers = self.headers
        tlset.extend(self.to_flat_rows())
        return tlset

    def to_csv(self, headers=True):
        return self.to_tablib(headers).export("csv", delimiter=",")

    def to_csv_file(self, filepath, headers=True):
        with open(filepath, "w") as f:
            f.write(self.to_csv(headers=headers))

    def print(self):
        """Print a representation table suited to a terminal in grid format."""
        tlset = self.to_tablib()
        print(tlset.export("cli", tablefmt="grid"))

    @classmethod
    def from_csv_file(cls, filepath, day_shift=True, headers=True):
        """
        Construct :class:`MaskMap` from a csv file, usually generated by
        :meth:`to_csv_file`.
        """
        with open(filepath, "r") as fh:
            tlset = tl.Dataset().load(fh, headers=headers)

        mask_map: Dict[int, _MaskedData] = {}
        for row in tlset:
            mask_map[int(row[0])] = _MaskedData(int(row[1]), int(row[2]) if day_shift else 0)

        return cls(mask_map)

    @classmethod
    def from_id_range(cls, min_id, max_id, day_shift=True, random_seed=None):
        """Create a map given a range of IDs (ints)

        Parameters
        ----------
        min_id : int
            Lower bound of ids to mask.
        max_id : int
            Upper bound of ids to mask.
        day_shift : bool, default True
            Whether to also generate a random day_shift value for each id
        random_seed : int, float, str, bytes, or bytearray
            Seed value. Note that pseudo-random number generation always
            produces the same output given the same seed. So if the same
            seed and ID ranges are used, you should reliably get the same
            masking. This is useful if you want to use the same masking
            across multiple executions of the command, which is often the case.
            'None' defaults to current system time.
        """
        # generate masked ids
        masked_ids = shuffle_range(min_id, max_id, random_seed=random_seed)

        # generate random day shift value for each id
        if day_shift:
            day_shifts = random_day_shifts(min_id, max_id, random_seed=random_seed)

        mask_map: Dict[int, _MaskedData] = {}
        for i in range(min_id, max_id + 1):
            masked_idx = i - min_id
            mask_map[i] = _MaskedData(
                masked_ids[masked_idx], day_shifts[masked_idx] if day_shift else 0
            )

        return cls(mask_map)


def shuffle_range(start, stop, random_seed=None):
    random.seed(random_seed)
    shuffled = list(range(start, stop + 1))
    random.shuffle(shuffled)
    return shuffled


def random_day_shifts(start, stop, lower_bound=365, upper_bound=730, random_seed=None):
    random.seed(random_seed)
    return [random.randint(lower_bound, upper_bound) for _ in range(start, stop + 1)]
