from pathlib import Path

from macpie.pandas import file_to_dataframe
from macpie.testing import assert_dfs_equal


current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None

primary = file_to_dataframe(current_dir / "primary_no_dupes.xlsx")

secondary = file_to_dataframe(current_dir / "secondary.xlsx")

cols_ignore = []


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
    ).reset_index(drop=True)

    # result.to_excel(current_dir / "dropna_true_result.xlsx", index=False)
    expected_result = file_to_dataframe(current_dir / "dropna_true_expected_result.xlsx")
    assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)


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
    ).reset_index(drop=True)

    # result.to_excel(current_dir / "dropna_true_merge_full_result.xlsx", index=False)
    expected_result = file_to_dataframe(current_dir / "dropna_true_merge_full_expected_result.xlsx")
    assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)


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
    expected_result = file_to_dataframe(current_dir / "dropna_false_expected_result.xlsx")
    assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)
