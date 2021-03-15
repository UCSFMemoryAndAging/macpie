from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import macpie as mp
from macpie import errors
from macpie.core import DataObject, LavaDataObject


current_dir = Path("tests/core/reshape/root_merge/").resolve()


def test_root_merge():

    d1 = {
        'PIDN': [1, 1, 1],
        'DCDate': [datetime(2001, 3, 2), None, datetime(2001, 8, 1)],
        'InstrID': [7, 8, 9]
    }
    df1 = pd.DataFrame(data=d1)
    do1 = LavaDataObject('do1', df1, id_col='InstrID')

    d2 = {
        'PIDN': [2, 2, 2],
        'DCDate': [datetime(2001, 3, 2), None, datetime(2001, 8, 1)],
        'InstrID': [7, 8, 9]
    }
    df2 = pd.DataFrame(data=d2)
    do2 = LavaDataObject('do2', df2, id_col='InstrID')

    d3 = {
        'PIDN': [3, 3, 3],
        'DCDate': [datetime(2001, 3, 2), None, datetime(2001, 8, 1)],
        'InstrID': [7, 8, 9]
    }
    df3 = pd.DataFrame(data=d3)
    do3 = LavaDataObject('do3', df3, id_col='InstrID')

    print(do1)
    (x, y) = mp.core.root_merge(do1, [do2, do3])
    print('x:')
    print(x)
    print(x.df)
    print('y:')
    print(y)