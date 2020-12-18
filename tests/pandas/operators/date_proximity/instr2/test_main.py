from pathlib import Path

import pandas as pd
import pytest

from macpie import io, util


data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/pandas/operators/date_proximity/instr2/").resolve()

# output_dir = current_dir
output_dir = None

cols_ignore = ['PIDN_link', 'DCDate_link', 'VType', 'DayDiff', 'link_date']

dfs_dict = pd.read_excel(
    data_dir / "instr2.xlsx",
    sheet_name=[
        'LINK_INSTR2',
        'INSTR1_linked',
        'INSTR3_linked'
    ],
    engine='openpyxl'
)

primary = dfs_dict['LINK_INSTR2']


@pytest.mark.slow
def test_secondary_instr1():

    secondary_instr1 = io.file_to_dataframe(data_dir / "instr1_all.csv")

    # test closest; earlier_or_later; 90 days
    instr1_result = primary.mac.date_proximity(
        secondary_instr1,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid'
    )

    instr1_result.drop(columns=['PIDN'], inplace=True)
    instr1_result.rename(columns={'PIDN_link': 'PIDN', 'InstrID_link': 'link_id'}, inplace=True)
    # instr1_result.to_excel(current_dir / "instr1_result.xlsx", index=False)

    instr1_expected_result = dfs_dict['INSTR1_linked']
    util.testing.assert_dfs_equal(instr1_result, instr1_expected_result, cols_ignore=cols_ignore)


@pytest.mark.slow
def test_secondary_instr3():

    secondary_instr3 = io.file_to_dataframe(data_dir / "instr3_all.csv")

    # test closest; earlier_or_later; 90 days
    instr3_result = primary.mac.date_proximity(
        secondary_instr3,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid'
    )

    instr3_result.drop(columns=['PIDN'], inplace=True)
    instr3_result.rename(columns={'PIDN_link': 'PIDN', 'InstrID_link': 'link_id'}, inplace=True)
    # instr3_result.to_excel(current_dir / "instr3_result.xlsx", index=False)

    instr3_expected_result = dfs_dict['INSTR3_linked']
    util.testing.assert_dfs_equal(instr3_result, instr3_expected_result, cols_ignore=cols_ignore)
