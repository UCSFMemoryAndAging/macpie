from pathlib import Path
from typing import ClassVar, List

import pandas as pd

from macpie.classes import DataObject


class LavaDataObject(DataObject):

    FIELD_ID_COL_VALUE_DEFAULT : ClassVar[str] = 'instrid'
    FIELD_ID2_COL_VALUE_DEFAULT : ClassVar[str] = 'pidn'
    FIELD_ID_COL_VALUES_POSSIBLE : ClassVar[List[str]] = ['ID', 'PIDN', 'VID', 'INSTRID', 'SPECID']
    FIELD_DATE_COL_VALUE_DEFAULT : ClassVar[str] = 'dcdate'
    FIELD_DATE_COL_VALUES_POSSIBLE : ClassVar[List[str]] = ['DATE', 'DCDATE']

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        id_col: str = None,
        date_col: str = None,
        id2_col: str = None,
        filepath: Path = None
    ):
        super().__init__(
            name,
            df,
            id_col if id_col is not None else LavaDataObject.FIELD_ID_COL_VALUE_DEFAULT,
            date_col if date_col is not None else LavaDataObject.FIELD_DATE_COL_VALUE_DEFAULT,
            id2_col if id2_col is not None else LavaDataObject.FIELD_ID2_COL_VALUE_DEFAULT,
            filepath
        )
