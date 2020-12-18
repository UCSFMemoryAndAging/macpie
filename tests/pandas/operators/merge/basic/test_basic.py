from pathlib import Path

import pandas as pd

from macpie import io, util


current_dir = Path("tests/pandas/operators/merge/basic/").resolve()

# output_dir = current_dir
output_dir = None

primary = io.file_to_dataframe(current_dir / "small.xlsx")


dfs_dict = pd.read_excel(
    current_dir / "small.xlsx",
    sheet_name=[
        'small_anchor',
        'instr2_all_linked',
        'instr3_all_linked'
    ],
    engine='openpyxl'
)

small_anchor = dfs_dict['small_anchor']
instr2_all_linked = dfs_dict['instr2_all_linked']
instr3_all_linked = dfs_dict['instr3_all_linked']


def test_add_suffixes_false():
    result = small_anchor.mac.merge(
        instr2_all_linked,
        left_on=['pidn', 'dcdate', 'instrid'],
        right_on=['pidn_link', 'dcdate_link', 'instrid_link'],
        merge_suffixes=('_a', '_b'),
        add_suffixes=False
    ).mac.merge(
        instr3_all_linked,
        left_on=['pidn_a', 'dcdate_a', 'instrid_a'],
        right_on=['pidn_link', 'dcdate_link', 'instrid_link'],
        merge_suffixes=(None, '_c'),
        add_suffixes=False,
    )

    # result.to_excel(current_dir / "add_suffixes_false_result.xlsx", index=False)
    expected_result = pd.read_excel(current_dir / "add_suffixes_false_expected_result.xlsx", engine='openpyxl')
    util.testing.assert_dfs_equal(result, expected_result, output_dir=output_dir)


def test_add_suffixes_true():
    result = small_anchor.mac.merge(
        instr2_all_linked,
        left_on=['pidn', 'dcdate', 'instrid'],
        right_on=['pidn_link', 'dcdate_link', 'instrid_link'],
        merge_suffixes=('_a', '_b'),
        add_suffixes=True
    ).mac.merge(
        instr3_all_linked,
        left_on=['pidn_a', 'dcdate_a', 'instrid_a'],
        right_on=['pidn_link', 'dcdate_link', 'instrid_link'],
        merge_suffixes=(None, '_c'),
        add_suffixes=True,
    )

    # result.to_excel(current_dir / "add_suffixes_true_result.xlsx", index=False)
    expected_result = pd.read_excel(current_dir / "add_suffixes_true_expected_result.xlsx", engine='openpyxl')
    util.testing.assert_dfs_equal(result, expected_result, output_dir=output_dir)


def test_with_index():
    result = small_anchor.mac.merge(
        instr2_all_linked,
        left_on=['pidn', 'dcdate', 'instrid'],
        right_on=['pidn_link', 'dcdate_link', 'instrid_link'],
        merge_suffixes=('_a', '_b'),
        add_suffixes=False,
        add_indexes=('small_anchor', 'instr2_all_linked')
    ).mac.merge(
        instr3_all_linked,
        left_on=[('small_anchor', 'pidn'), ('small_anchor', 'dcdate'), ('small_anchor', 'instrid')],
        right_on=['pidn_link', 'dcdate_link', 'instrid_link'],
        merge_suffixes=('_a', '_b'),
        add_suffixes=False,
        add_indexes=(None, 'instr3_all_linked')
    )

    expected_result = pd.read_excel(
        current_dir / "with_index_expected_result.xlsx",
        index_col=0,
        header=[0, 1],
        engine='openpyxl'
    )

    assert(result.columns.equals(expected_result.columns))

    util.testing.assert_dfs_equal(result, expected_result, output_dir=output_dir)
