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
    'PIDN_x', 'VType', 'DayDiff', 'link_id'
]
cols_ignore_pat = '^' + get_option("column.system.prefix")


@pytest.mark.slow
def test_instr1():

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
        ]
    )

    primary = dfs_dict['primary']
    secondary = file_to_dataframe(data_dir / "instr1_all.csv")

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
    assert_dfs_equal(closest_earlier_or_later_90_result,
                     closest_earlier_or_later_90_expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
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
    assert_dfs_equal(closest_later_90_result,
                     closest_later_90_expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
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
    assert_dfs_equal(closest_earlier_90_result,
                     closest_earlier_90_expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
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
    assert_dfs_equal(all_earlier_or_later_90_result,
                     all_earlier_or_later_90_expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
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
    assert_dfs_equal(all_later_90_result,
                     all_later_90_expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
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
    assert_dfs_equal(all_earlier_90_result,
                     all_earlier_90_expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
                     output_dir=output_dir)
