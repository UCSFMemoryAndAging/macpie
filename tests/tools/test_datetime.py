import dateutil
import pandas as pd
import pytest

from macpie import datetimetools


def test_reformat_datetime_str():
    assert datetimetools.reformat_datetime_str("1/1/2022") == "2022-01-01"

    assert datetimetools.reformat_datetime_str("1/1/2022", format="%Y") == "2022"

    with pytest.raises(dateutil.parser._parser.ParserError):
        datetimetools.reformat_datetime_str("zzzz")

    assert pd.isnull(datetimetools.reformat_datetime_str("zzzz", errors="coerce")) is True

    assert datetimetools.reformat_datetime_str("zzzz", errors="ignore") == "zzzz"
