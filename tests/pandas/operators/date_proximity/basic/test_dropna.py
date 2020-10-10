from pathlib import Path

from macpie.io import import_file
from macpie.testing import assert_dfs_equal


current_dir = Path("tests/pandas/operators/date_proximity/basic/")

# output_dir = current_dir
output_dir = None

primary = import_file(current_dir / "primary_no_dupes.xlsx")

secondary = import_file(current_dir / "secondary.xlsx")


def test_dropna_true():

    result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        dropna=True,
        merge='partial'
    )

    # result.to_excel(current_dir / "dropna_true_result.xlsx", index=False)
    expected_result = import_file(current_dir / "dropna_true_expected_result.xlsx")
    assert_dfs_equal(result, expected_result, output_dir=output_dir)


def test_dropna_true_merge_full():

    result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        dropna=True,
        merge='full'
    )

    # result.to_excel(current_dir / "dropna_true_merge_full_result.xlsx", index=False)
    expected_result = import_file(current_dir / "dropna_true_merge_full_expected_result.xlsx")
    assert_dfs_equal(result, expected_result, output_dir=output_dir)


def test_dropna_false():

    result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        dropna=False,
        merge='partial'
    )

    # result.to_excel(current_dir / "dropna_false_result.xlsx", index=False)
    expected_result = import_file(current_dir / "dropna_false_expected_result.xlsx")
    assert_dfs_equal(result, expected_result, output_dir=output_dir)
