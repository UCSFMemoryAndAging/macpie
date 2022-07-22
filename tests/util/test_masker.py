import pandas as pd
import pytest

from macpie.util import MaskMap, Masker

# changing this will invalidate most of these tests
RANDOM_SEED = 567


def test_maskmap(tmp_path):
    m = MaskMap()
    assert m == {}

    m = MaskMap.from_id_range(1, 5, day_shift=False, random_seed=RANDOM_SEED)
    assert m.to_flat_rows() == [(1, 4, 0), (2, 1, 0), (3, 5, 0), (4, 3, 0), (5, 2, 0)]

    m = MaskMap.from_id_range(1, 5, random_seed=RANDOM_SEED)
    assert len(m) == 5
    assert m.to_flat_rows() == [(1, 4, 437), (2, 1, 528), (3, 5, 608), (4, 3, 407), (5, 2, 661)]
    assert m[1].masked_id == 4
    assert m[1].day_shift == 437
    assert m[3][0] == 5
    assert m[3][1] == 608
    assert m[5].masked_id == 2
    assert m[5].day_shift == 661

    m.to_csv_file(tmp_path / "m.csv")
    m2 = MaskMap.from_csv_file(tmp_path / "m.csv")
    assert m.to_flat_rows() == m2.to_flat_rows()


# base test data for following tests
data = [
    [1, 11, 6, None, 1, "1/2/2001"],
    [2, 12, 7, "2002-02-02", 2, "2/3/2003"],
    [3, 13, 8, None, 3, "3/4/2003"],
    [4, 14, 9, "2003-03-03", 3, "3/4/2003"],
    [5, 15, 10, "2003-03-03", 3, "3/4/2003"],
]
cols = ["pidn", "instrid", "cdr", "dcdate", "faq", "date2"]
df = pd.DataFrame(data, columns=cols)

m = MaskMap.from_id_range(1, 5, random_seed=RANDOM_SEED)
m2 = MaskMap.from_id_range(11, 15, day_shift=False, random_seed=RANDOM_SEED)
masker = Masker(m, "pidn", date_col_names="dcdate")
masker.add(m2, "instrid")


def test_masker():
    result, _ = masker.mask_df(df)

    # expected masked data
    masked_data = [
        [4, 14, 6, None, 1, "1/2/2001"],
        [1, 11, 7, "2000-08-23", 2, "2/3/2003"],
        [5, 15, 8, None, 3, "3/4/2003"],
        [3, 13, 9, "2002-01-20", 3, "3/4/2003"],
        [2, 12, 10, "2001-05-11", 3, "3/4/2003"],
    ]
    masked_cols = ["pidn", "instrid", "Col1", "dcdate", "Col2", "Col3"]
    masked_df = pd.DataFrame(masked_data, columns=masked_cols)
    masked_df["dcdate"] = pd.to_datetime(masked_df["dcdate"])

    assert result.equals(masked_df)

    # test inplace
    df_inplace = df.copy()
    masker.mask_df(df_inplace, inplace=True)
    assert df_inplace.equals(masked_df)


def test_masker_rename_false():
    result, _ = masker.mask_df(df, rename_cols=False)

    # expected masked data
    masked_data = [
        [4, 14, 6, None, 1, "1/2/2001"],
        [1, 11, 7, "2000-08-23", 2, "2/3/2003"],
        [5, 15, 8, None, 3, "3/4/2003"],
        [3, 13, 9, "2002-01-20", 3, "3/4/2003"],
        [2, 12, 10, "2001-05-11", 3, "3/4/2003"],
    ]
    masked_df = pd.DataFrame(masked_data, columns=cols)
    masked_df["dcdate"] = pd.to_datetime(masked_df["dcdate"])

    assert result.equals(masked_df)


def test_masker_norename():
    result, _ = masker.mask_df(df, norename_cols=["cdr", "faq"])

    # expected masked data
    masked_data = [
        [4, 14, 6, None, 1, "1/2/2001"],
        [1, 11, 7, "2000-08-23", 2, "2/3/2003"],
        [5, 15, 8, None, 3, "3/4/2003"],
        [3, 13, 9, "2002-01-20", 3, "3/4/2003"],
        [2, 12, 10, "2001-05-11", 3, "3/4/2003"],
    ]
    masked_cols = ["pidn", "instrid", "cdr", "dcdate", "faq", "Col1"]
    masked_df = pd.DataFrame(masked_data, columns=masked_cols)
    masked_df["dcdate"] = pd.to_datetime(masked_df["dcdate"])

    assert result.equals(masked_df)


def test_masker_drop_cols():
    result, _ = masker.mask_df(df, drop_cols="faq")

    # expected masked data
    masked_data = [
        [4, 14, 6, None, "1/2/2001"],
        [1, 11, 7, "2000-08-23", "2/3/2003"],
        [5, 15, 8, None, "3/4/2003"],
        [3, 13, 9, "2002-01-20", "3/4/2003"],
        [2, 12, 10, "2001-05-11", "3/4/2003"],
    ]
    masked_cols = ["pidn", "instrid", "Col1", "dcdate", "Col2"]
    masked_df = pd.DataFrame(masked_data, columns=masked_cols)
    masked_df["dcdate"] = pd.to_datetime(masked_df["dcdate"])

    assert result.equals(masked_df)


def test_no_id_col_for_date_col():
    m3 = MaskMap.from_id_range(21, 25, day_shift=False, random_seed=RANDOM_SEED)
    masker.add(m3, "non_existent_id_col", date_col_names="date2")

    with pytest.raises(ValueError):
        masker.mask_df(df)
