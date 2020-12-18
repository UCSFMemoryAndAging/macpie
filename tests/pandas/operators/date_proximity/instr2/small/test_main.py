from pathlib import Path

import pandas as pd

from macpie import io, util

data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/pandas/operators/date_proximity/instr2/small/").resolve()

# output_dir = current_dir
output_dir = None


def test_instr2_small():

    cols_ignore = ['PIDN_link', 'DCDate_link', 'VType', 'DayDiff', 'link_date']

    dfs_dict = pd.read_excel(
        data_dir / "instr2_small.xlsx",
        sheet_name=[
            'primary',
            'expected_results'
        ],
        engine='openpyxl'
    )

    primary = dfs_dict['primary']
    secondary_instr1 = io.file_to_dataframe(data_dir / "instr1_all.csv")

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

    small_result.drop(columns=['PIDN'], inplace=True)
    small_result.rename(columns={'PIDN_link': 'PIDN', 'InstrID_link': 'link_id'}, inplace=True)
    # small_result.to_excel(current_dir / "small_result.xlsx", index=False)

    small_expected_result = dfs_dict['expected_results']
    util.testing.assert_dfs_equal(small_result, small_expected_result, cols_ignore=cols_ignore)
