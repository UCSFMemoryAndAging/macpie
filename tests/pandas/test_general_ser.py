from datetime import datetime

import macpie as mp
import numpy as np
import pandas as pd
import pytest


def test_remove_trailers():
    ser1 = pd.Series([1, "2", 3, "", None, np.nan])

    with pytest.raises(ValueError):
        mp.pandas.remove_trailers(ser1, remove_na=False)

    expected = pd.Series([1, "2", 3, ""])
    assert ser1.mac.remove_trailers().equals(expected)

    expected = pd.Series([1, "2", 3])
    assert ser1.mac.remove_trailers(predicate=lambda x: x == "").equals(expected)

    ser2 = pd.Series([1, "2", 3, None, 4, np.nan])
    expected = pd.Series([1, "2", 3, None, 4])
    assert ser2.mac.remove_trailers().equals(expected)
