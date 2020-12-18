from pathlib import Path

import pandas as pd
import pytest

from macpie import io, util


data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/pandas/operators/date_proximity/instr1/").resolve()

# output_dir = current_dir
output_dir = None


@pytest.mark.slow
def test_instr1():

    cols_ignore = ['_duplicates', 'link_id', 'link_date', 'DayDiff', 'VType', 'PIDN_link', 'DCDate_link']

    dfs_dict = pd.read_excel(
        data_dir / "instr1.xlsx",
        sheet_name=[
            'primary',
            'closest_earlier_or_later_90',
            'closest_later_90',
            'closest_earlier_90',
            'all_earlier_or_later_90',
            'all_later_90',
            'all_earlier_90'
        ],
        engine='openpyxl'
    )

    primary = dfs_dict['primary']
    secondary = io.file_to_dataframe(data_dir / "instr1_all.csv")

    # test closest; earlier_or_later; 90 days
    closest_earlier_or_later_90_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90
    )
    # closest_earlier_or_later_90_result.to_excel(current_dir / "closest_earlier_or_later_90_result.xlsx", index=False)
    closest_earlier_or_later_90_expected_result = dfs_dict['closest_earlier_or_later_90']
    util.testing.assert_dfs_equal(closest_earlier_or_later_90_result,
                                  closest_earlier_or_later_90_expected_result,
                                  cols_ignore=cols_ignore,
                                  output_dir=output_dir)

    # test closest; later; 90 days
    closest_later_90_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='later',
        days=90
    )
    # closest_later_90_result.to_excel(current_dir / "closest_later_90_result.xlsx", index=False)
    closest_later_90_expected_result = dfs_dict['closest_later_90']
    util.testing.assert_dfs_equal(closest_later_90_result,
                                  closest_later_90_expected_result,
                                  cols_ignore=cols_ignore,
                                  output_dir=output_dir)

    # test closest; earlier; 90 days
    closest_earlier_90_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier',
        days=90
    )

    # closest_earlier_90_result.to_excel(current_dir / "closest_earlier_90_result.xlsx", index=False)
    closest_earlier_90_expected_result = dfs_dict['closest_earlier_90']
    util.testing.assert_dfs_equal(closest_earlier_90_result,
                                  closest_earlier_90_expected_result,
                                  cols_ignore=cols_ignore,
                                  output_dir=output_dir)

    # test all; earlier_or_later; 90 days
    all_earlier_or_later_90_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='all',
        when='earlier_or_later',
        days=90
    )

    # all_earlier_or_later_90_result.to_excel(current_dir / "all_earlier_or_later_90_result.xlsx", index=False)
    all_earlier_or_later_90_expected_result = dfs_dict['all_earlier_or_later_90']
    util.testing.assert_dfs_equal(all_earlier_or_later_90_result,
                                  all_earlier_or_later_90_expected_result,
                                  cols_ignore=cols_ignore,
                                  output_dir=output_dir)

    # test all; later; 90 days
    all_later_90_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='all',
        when='later',
        days=90
    )

    # all_later_90_result.to_excel(current_dir / "all_later_90_result.xlsx", index=False)
    all_later_90_expected_result = dfs_dict['all_later_90']
    util.testing.assert_dfs_equal(all_later_90_result,
                                  all_later_90_expected_result,
                                  cols_ignore=cols_ignore,
                                  output_dir=output_dir)

    # test all; earlier; 90 days
    all_earlier_90_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='all',
        when='earlier',
        days=90
    )

    # all_earlier_90_result.to_excel(current_dir / "all_earlier_90_result.xlsx", index=False)
    all_earlier_90_expected_result = dfs_dict['all_earlier_90']
    util.testing.assert_dfs_equal(all_earlier_90_result,
                                  all_earlier_90_expected_result,
                                  cols_ignore=cols_ignore,
                                  output_dir=output_dir)
