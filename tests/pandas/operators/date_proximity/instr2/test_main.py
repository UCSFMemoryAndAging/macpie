from pathlib import Path

import pandas as pd
import pytest

from macpie._config import get_option
from macpie.pandas import file_to_dataframe
from macpie.testing import assert_dfs_equal


data_dir = Path("tests/data/").resolve()
current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None

cols_ignore = [
    'PIDN', 'VType', 'DayDiff'
]
cols_ignore_pat = '^' + get_option("column.system.prefix")

dfs_dict = pd.read_excel(
    data_dir / "instr2.xlsx",
    sheet_name=[
        'LINK_INSTR2',
        'INSTR1_linked',
        'INSTR3_linked'
    ]
)

primary = dfs_dict['LINK_INSTR2']


@pytest.mark.slow
def test_secondary_instr1():

    secondary_instr1 = file_to_dataframe(data_dir / "instr1_all.csv")

    # test closest; earlier_or_later; 90 days
    instr1_result = primary.mac.date_proximity(
        secondary_instr1,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid',
        duplicates_indicator=True
    )

    # instr1_result.to_excel(current_dir / "instr1_result.xlsx", index=False)

    instr1_expected_result = dfs_dict['INSTR1_linked']
    assert_dfs_equal(instr1_result,
                     instr1_expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat)


@pytest.mark.slow
def test_secondary_instr3():

    secondary_instr3 = file_to_dataframe(data_dir / "instr3_all.csv")

    # test closest; earlier_or_later; 90 days
    instr3_result = primary.mac.date_proximity(
        secondary_instr3,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid',
        duplicates_indicator=True
    )

    # instr3_result.to_excel(current_dir / "instr3_result.xlsx", index=False)

    instr3_expected_result = dfs_dict['INSTR3_linked']
    assert_dfs_equal(instr3_result,
                     instr3_expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
                     output_dir=output_dir)
