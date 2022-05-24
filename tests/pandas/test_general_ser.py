from datetime import datetime

import macpie as mp
import numpy as np
import pandas as pd
import pytest


def test_count_trailers():
    ser1 = pd.Series([1, "2", 3, "", None, np.nan])

    with pytest.raises(ValueError):
        mp.pandas.count_trailers(ser1, count_na=False, count_empty_string=False)

    assert ser1.mac.count_trailers(count_empty_string=False) == 2

    assert ser1.mac.count_trailers() == 3

    ser2 = pd.Series([1, "2", 3, None, 4, np.nan])

    assert ser2.mac.count_trailers() == 1

    assert ser2.mac.count_trailers(predicates=lambda x: x == 4) == 3


def test_remove_trailers():
    ser1 = pd.Series([1, "2", 3, "", None, np.nan])

    with pytest.raises(ValueError):
        mp.pandas.remove_trailers(ser1, remove_na=False, remove_empty_string=False)

    expected = pd.Series([1, "2", 3, ""])
    assert ser1.mac.remove_trailers(remove_empty_string=False).equals(expected)

    expected = pd.Series([1, "2", 3])
    assert ser1.mac.remove_trailers().equals(expected)

    ser2 = pd.Series([1, "2", 3, None, 4, np.nan])

    expected = pd.Series([1, "2", 3, None, 4])
    assert ser2.mac.remove_trailers().equals(expected)

    expected = pd.Series([1, "2", 3])
    assert ser2.mac.remove_trailers(predicates=lambda x: x == 4).equals(expected)


def test_rtrim():
    ser1 = pd.Series([1, "2", 3, "", None, np.nan])

    expected = pd.Series([1, "2", 3, ""])
    assert ser1.mac.rtrim(trim_empty_string=False).equals(expected)

    expected = pd.Series([1, "2", 3])
    assert ser1.mac.rtrim(trim_empty_string=True).equals(expected)

    ser2 = pd.Series([1, "2", 3, None, 4, np.nan])

    expected = pd.Series([1, "2", 3, None, 4])
    assert ser2.mac.rtrim().equals(expected)
