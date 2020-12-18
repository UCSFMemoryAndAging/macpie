from pathlib import Path

from macpie import io, util

current_dir = Path("tests/pandas/operators/date_proximity/dupes/").resolve()

# output_dir = current_dir
output_dir = None


def test_dupes():

    primary = io.file_to_dataframe(current_dir / "primary.xlsx")
    secondary = io.file_to_dataframe(current_dir / "secondary.xlsx")

    dupes_result = primary.mac.date_proximity(
        secondary,
        id_on='pidn',
        date_on='dcdate',
        get='closest',
        when='earlier_or_later',
        days=90,
        left_link_id='instrid',
        merge='full'
    )

    # dupes_result.to_excel(current_dir / "dupes_result.xlsx", index=False)
    dupes_expected_result = io.file_to_dataframe(current_dir / "dupes_expected_result.xlsx")
    util.testing.assert_dfs_equal(dupes_result, dupes_expected_result, output_dir=output_dir)
