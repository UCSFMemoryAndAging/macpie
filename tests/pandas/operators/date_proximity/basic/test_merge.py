from pathlib import Path

from macpie.pandas import file_to_dataframe
from macpie.testing import assert_dfs_equal


current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None

primary = file_to_dataframe(current_dir / "primary.xlsx")

secondary = file_to_dataframe(current_dir / "secondary.xlsx")

cols_ignore = []


def test_merge_partial():
    # partial merge

    merge_partial_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid',
        merge='partial'
    )

    # merge_partial_result.to_excel(current_dir / "merge_partial_result.xlsx", index=False)
    merge_partial_expected_result = file_to_dataframe(current_dir / "merge_partial_expected_result.xlsx")
    assert_dfs_equal(merge_partial_result,
                     merge_partial_expected_result,
                     cols_ignore=cols_ignore,
                     output_dir=output_dir)

    # test that results are same when using equivalent id and date params
    test_id_on_params = primary.mac.date_proximity(
        secondary,
        id_left_on='pidn',
        id_right_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid',
        merge='partial'
    )

    test_date_on_params = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_left_on='dcdate',
        date_right_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid',
        merge='partial'
    )

    # test using id_left_on and id_right_on params
    assert merge_partial_result.equals(test_id_on_params)

    # test using date_left_on and date_right_on params
    assert merge_partial_result.equals(test_date_on_params)


def test_merge_full():
    # full merge

    merge_full_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid',
        merge='full'
    )

    # merge_full_result.to_excel(current_dir / "merge_full_result.xlsx", index=False)
    merge_full_expected_result = file_to_dataframe(current_dir / "merge_full_expected_result.xlsx")
    assert_dfs_equal(merge_full_result, merge_full_expected_result, cols_ignore=cols_ignore, output_dir=output_dir)
