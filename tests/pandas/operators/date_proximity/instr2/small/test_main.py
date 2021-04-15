from pathlib import Path

import pandas as pd

from macpie.pandas import file_to_dataframe
from macpie.testing import assert_dfs_equal

data_dir = Path("tests/data/").resolve()
current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None

cols_ignore = []


def test_instr2_small():

    dfs_dict = pd.read_excel(
        current_dir / "instr2_small.xlsx",
        sheet_name=[
            'primary',
            'expected_results'
        ]
    )

    primary = dfs_dict['primary']
    secondary_instr1 = file_to_dataframe(data_dir / "instr1_all.csv")

    # test closest; earlier_or_later; 90 days
    small_result = primary.mac.date_proximity(
        secondary_instr1,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid'
    )

    small_expected_result = dfs_dict['expected_results']
    assert_dfs_equal(small_result, small_expected_result, cols_ignore=cols_ignore)
