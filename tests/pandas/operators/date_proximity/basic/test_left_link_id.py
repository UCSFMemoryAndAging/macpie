from pathlib import Path

from macpie.io import import_file
from macpie.testing import assert_dfs_equal


current_dir = Path("tests/pandas/operators/date_proximity/basic/")

# output_dir = current_dir
output_dir = None

primary = import_file(current_dir / "primary_no_dupes.xlsx")

secondary = import_file(current_dir / "secondary.xlsx")


def test_left_link_id_blank_merge_partial():
    # partial merge

    result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        merge='partial'
    )

    # result.to_excel(current_dir / "left_link_id_blank_merge_partial_result.xlsx", index=False)
    expected_result = import_file(current_dir / "left_link_id_blank_merge_partial_expected_result.xlsx")
    assert_dfs_equal(result, expected_result, output_dir=output_dir)


def test_left_link_id_blank_merge_full():
    # full merge

    result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        merge='full'
    )

    # result.to_excel(current_dir / "left_link_id_blank_merge_full_result.xlsx", index=False)
    expected_result = import_file(current_dir / "left_link_id_blank_merge_full_expected_result.xlsx")
    assert_dfs_equal(result, expected_result, output_dir=output_dir)
