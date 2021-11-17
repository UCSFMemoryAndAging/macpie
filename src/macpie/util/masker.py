"""
Contains classes to help mask (i.e. de-identify) production data contained in your files,
currently PHI data contained in ID and Date columns. In the MAC Lava database, for
example, these would be any columns containing PIDNs, InstrIDs, and Dates of Service
(e.g. DCDate, VDate).

Specifically, a per-ID replacement ID and a per-ID date-shift value
(random number between 365 and 730) are created. Each unique ID is replaced with a
unique masked ID, and all Dates are shifted back by the date-shift value for that
particular ID. A second set of ID columns can be replaced with a second set of
replacement IDs as well.

Columns that are not masked will have their column header renamed to a generic
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
import itertools
import random
from typing import Dict

import pandas as pd
import tablib as tl

from macpie import lltools


class Masker:
    """Masks data in pandas DataFrames.

    :param mappers: One or more instances of :class:`macpie.util.IdMapCols`.
    :param cols_to_drop: Columns to drop (e.g. because they contain PHI or unnecessarily
                         risky data.
    :param cols_no_mask: Columns not to mask (leave untouched). Columns specified elsewhere
                         will override these columns.
    """

    def __init__(self, mappers, cols_to_drop=None, cols_no_mask=None):
        self.mappers = mappers
        self.cols_to_drop = cols_to_drop if cols_to_drop else []
        self.cols_no_mask = cols_no_mask if cols_no_mask else []

    @property
    def mappers(self):
        return self._mappers

    @mappers.setter
    def mappers(self, mappers):
        self._mappers = []
        mappers = lltools.maybe_make_list(mappers)
        for mapper in mappers:
            self.add_mapper(mapper)

    @property
    def id_cols(self):
        return list(itertools.chain.from_iterable([mapper.id_cols for mapper in self.mappers]))

    @property
    def date_cols(self):
        return list(itertools.chain.from_iterable([mapper.date_cols for mapper in self.mappers]))

    @property
    def cols(self):
        return self.id_cols + self.date_cols

    def add_mapper(self, mapper):
        common_cols = lltools.common_members(self.cols, mapper.cols)
        if common_cols:
            raise KeyError(f"A mask for the following columns already exists: {str(common_cols)}")

        self._mappers.append(mapper)

    def get_mapper(self, col):
        for mapper in self.mappers:
            if mapper.has_col(col):
                return mapper
        return None

    def get_mappers(self, cols):
        return [self.get_mapper(col) for col in cols]

    def mask_df(self, df):
        id_cols_to_mask = [c for c in df.mac.get_col_names(self.id_cols, strict=False) if c]
        if len(id_cols_to_mask) < 1:
            print("No id cols to mask in df. Skipping.")
            return

        date_cols_to_mask = [c for c in df.mac.get_col_names(self.date_cols, strict=False) if c]

        # all cols to mask
        cols_to_mask = id_cols_to_mask + date_cols_to_mask

        # identify columns not to mask (leave untouched)
        cols_no_mask = [c for c in df.mac.get_col_names(self.cols_no_mask, strict=False) if c]
        cols_no_mask = lltools.diff(cols_no_mask, cols_to_mask)

        # identify columns to drop
        cols_to_drop = [c for c in df.mac.get_col_names(self.cols_to_drop, strict=False) if c]
        cols_to_drop = lltools.diff(cols_to_drop, cols_to_mask)

        # identify columns to rename
        cols_not_to_rename = set().union(cols_to_mask, cols_no_mask, cols_to_drop)
        cols_to_rename = lltools.diff(df.columns.tolist(), cols_not_to_rename)

        # now perform the masking

        # 1. drop columns
        result_df = df.drop(columns=cols_to_drop)

        # 2. rename columns
        col_rename_dict = {}
        for num, col_to_rename in enumerate(cols_to_rename):
            col_rename_dict[col_to_rename] = "Col" + str(num + 1)
        result_df.rename(columns=col_rename_dict, inplace=True)

        # 3. mask id columns
        for id_col in id_cols_to_mask:
            mapper = self.get_mapper(id_col)
            if mapper:
                mapper.mask_df_id_col(result_df, id_col)
            else:
                print("Mapper not found for id col", id_col)

        # 4. mask date columns
        for date_col_name in date_cols_to_mask:
            mapper = self.get_mapper(date_col_name)
            if mapper:
                mapper.mask_df_date_col(result_df, date_col_name)
            else:
                print("Mapper not found for date col", date_col_name)

        col_transformations = {**col_rename_dict, **dict.fromkeys(cols_to_drop)}

        return (result_df, col_transformations)


class IdMapCols:
    """Associates ID and Date columns with an instance of IdMap.

    :param id_cols: ID columns to mask using replacement IDs.
    :param date_cols: Date columns to mask using a day shift value.
    """

    def __init__(self, id_map, id_cols, date_cols=None):
        self.id_map = id_map
        self.id_cols = [id_col.lower() for id_col in id_cols]
        self.date_cols = (
            [date_col_name.lower() for date_col_name in date_cols] if date_cols else []
        )

    def __len__(self):
        return len(self.id_map)

    @property
    def cols(self):
        return self.id_cols + self.date_cols

    def has_col(self, col):
        return col.lower() in self.cols

    def get_id_cols_in_df(self, df):
        """Masking a date column requires at least one id column in the same
        DataFrame from which to retrieve the day_shift value. Given a dataframe,
        this helps find the id columns.
        """
        return [c for c in df.mac.get_col_names(self.id_cols, strict=False) if c]

    def mask_df_id_col(self, df, id_col):
        df[id_col] = df[id_col].apply(
            lambda x: self.id_map.get(x).masked_id if not pd.isnull(x) else None
        )

    def mask_df_date_col(self, df, date_col_name):
        if not df.mac.is_date_col(date_col_name):
            raise TypeError(f"Invalid date column '{date_col_name}'")

        id_cols_in_df = self.get_id_cols_in_df(df)

        if len(id_cols_in_df) < 1:
            print(f"Need id col in df to mask date_col_name '{date_col_name}'. Skipping.")
            return

        id_col = id_cols_in_df[0]  # any will do

        day_shift_helper_col = "__day_shift_" + id_col

        df[day_shift_helper_col] = df[id_col].apply(
            lambda x: pd.Timedelta(self.id_map.get(x).day_shift, unit="d")
            if not pd.isnull(x)
            else None
        )

        df[date_col_name] = df[date_col_name] - df[day_shift_helper_col]

        df.drop(columns=[day_shift_helper_col], inplace=True)

    @classmethod
    def from_ids(cls, ids, id_cols, date_cols=None, random_seed=None):
        id_map = IdMap.from_ids(ids, day_shift=bool(date_cols), random_seed=random_seed)
        return cls(id_map, id_cols, date_cols=date_cols)


# stores the masking data for each unique, original ID
_MaskedData = collections.namedtuple("_MaskedData", "masked_id, day_shift")


class IdMap:
    """Essentially a dict that maps IDs (ints) to instaces of _MaskedData,
    a namedtuple containing the following data used for masking:

    Parameters
    ----------
    masked_id :
        a replacement ID
    day_shift :
        a random number between 365 and 730 used to shift
        date values backwards by
    """

    def __init__(self, id_map=None):
        self.id_map = id_map if id_map else {}

    def __len__(self):
        return len(self.id_map)

    @property
    def headers(self):
        return ["id", "masked", "day_shift"]

    def get(self, id):
        return self.id_map[int(id)]

    def to_flat_rows(self):
        return [(k, v.masked_id, v.day_shift) for k, v in self.id_map.items()]

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
    def from_csv_file(cls, filepath, day_shift=True, headers=False):
        """
        Construct :class:`IdMap` from a csv file.
        """
        with open(filepath, "r") as fh:
            tlset = tl.Dataset().load(fh, headers=headers)

        id_map = {}
        for row in tlset:
            id_map[int(row[0])] = _MaskedData(int(row[1]), int(row[2]) if day_shift else 0)

        return cls(id_map)

    @classmethod
    def from_ids(cls, ids, day_shift=True, random_seed=None):
        """Create a map given a list of IDs (ints)
        :param ids: list of IDs (ints) to generate masked data for
        :param day_shift: whether to also generate a random day_shift value for each id
        :param random_seed: Random seed used to create masking data. Note that pseudo-random
                            number generation always produces the same output given the same
                            seed. So if the same seed and ID ranges are used, you should
                            reliably get the same masking. This is useful if you want to use
                            the same masking across multiple executions of the command,
                            which is often the case.
        """
        # change seed if you want different set of randoms
        # 'None' defaults to current system time
        random.seed(random_seed)

        min_id = min(ids)
        max_id = max(ids)

        # generate masked ids
        masked_ids = list(range(min_id, max_id + 1))
        random.shuffle(masked_ids)

        # generate random day shift value for each id
        if day_shift:
            day_shifts = [random.randint(365, 730) for _ in range(min_id, max_id + 1)]

        id_map: Dict[int, _MaskedData] = {}

        for i in ids:
            if i in id_map:
                continue

            masked_index = i - min_id
            id_map[i] = _MaskedData(
                masked_ids[masked_index], day_shifts[masked_index] if day_shift else 0
            )

        return cls(id_map)
