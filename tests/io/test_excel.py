import pandas as pd
import pytest

import macpie as mp


data = [
    [1, 4, 7, "1/1/2001", 1, "1/2/2001"],
    [2, 5, 8, "2/2/2002", 2, "2/3/2003"],
    [3, 6, 9, "3/3/2003", 3, "3/4/2003"],
]

reg_columns = ["col1", "col2", "col3", "date", "ids", "date2"]

reg_index = [1, 2, 3]

reg_df = pd.DataFrame(data, index=reg_index, columns=reg_columns)

reg_dset = mp.Dataset(reg_df, id_col_name="ids", date_col_name="date")

mi_columns = pd.MultiIndex.from_product([["level"], reg_columns])

mi_index = pd.MultiIndex.from_tuples([("a", 1), ("b", 2), ("c", 3)])

mi_df = pd.DataFrame(data=data, index=mi_index, columns=mi_columns)

mi_dset = mp.Dataset(
    mi_df, id_col_name=("level", "ids"), date_col_name=("level", "date"), name="mi_test_name"
)


@pytest.mark.parametrize("engine", ["openpyxl", "xlsxwriter"])
class TestPandasExcel:
    def test_dfs(self, tmp_path, engine):
        reg_df.to_excel(tmp_path / "reg_df.xlsx", engine=engine)
        reg_df_parsed = pd.read_excel(tmp_path / "reg_df.xlsx", index_col=0)
        pd.testing.assert_frame_equal(reg_df_parsed, reg_df)

        mi_df.to_excel(tmp_path / "mi_df.xlsx", engine=engine)
        mi_df_parsed = pd.read_excel(tmp_path / "mi_df.xlsx", index_col=[0, 1], header=[0, 1])
        pd.testing.assert_frame_equal(mi_df_parsed, mi_df)


@pytest.mark.parametrize("engine", ["mp_openpyxl", "mp_xlsxwriter"])
class TestMACPieExcel:
    def test_1_1_permutations(self, tmp_path, engine):
        df_1_1 = pd.DataFrame(data, columns=reg_columns, index=reg_index)

        dset_1_1 = mp.Dataset(df_1_1)

        dset_1_1.to_excel(tmp_path / "dset_1_0.xlsx", engine=engine, header=True, index=False)
        dset_1_1.to_excel(tmp_path / "dset_0_1.xlsx", engine=engine, header=False, index=True)
        dset_1_1.to_excel(tmp_path / "dset_1_1.xlsx", engine=engine, header=True, index=True)
        dset_1_1.to_excel(tmp_path / "dset_0_0.xlsx", engine=engine, header=False, index=False)

        # 1_1: test 1 header 1 index
        dset_1_1_parsed = mp.read_excel(tmp_path / "dset_1_1.xlsx")
        pd.testing.assert_frame_equal(dset_1_1, dset_1_1_parsed)

        # 1_0: test 1 header 0 index
        dset_1_1_parsed = mp.read_excel(tmp_path / "dset_1_0.xlsx")
        dset_1_1_parsed.index = reg_index
        pd.testing.assert_frame_equal(dset_1_1, dset_1_1_parsed)

        # 0_1: test 0 header 1 index
        dset_1_1_parsed = mp.read_excel(tmp_path / "dset_0_1.xlsx")
        dset_1_1_parsed.index.name = None  # if no header, pandas inserts a default index name of 0
        dset_1_1_parsed.columns = reg_columns
        pd.testing.assert_frame_equal(dset_1_1, dset_1_1_parsed)

        # 0_0: test 0 header 0 index
        dset_1_1_parsed = mp.read_excel(tmp_path / "dset_0_0.xlsx")
        dset_1_1_parsed.index = reg_index
        dset_1_1_parsed.columns = reg_columns
        pd.testing.assert_frame_equal(dset_1_1, dset_1_1_parsed)

    def test_2_2_permutations(self, tmp_path, engine):
        df_2_2 = pd.DataFrame(data, columns=mi_columns, index=mi_index)

        dset_2_2 = mp.Dataset(df_2_2)

        dset_2_2.to_excel(tmp_path / "dset_2_2.xlsx", engine=engine, header=True, index=True)
        dset_2_2.to_excel(tmp_path / "dset_2_0.xlsx", engine=engine, header=True, index=False)
        dset_2_2.to_excel(tmp_path / "dset_0_2.xlsx", engine=engine, header=False, index=True)
        dset_2_2.to_excel(tmp_path / "dset_0_0.xlsx", engine=engine, header=False, index=False)

        # 2_2: test 2 header 2 index
        dset_2_2_parsed = mp.read_excel(tmp_path / "dset_2_2.xlsx")
        pd.testing.assert_frame_equal(dset_2_2, dset_2_2_parsed)

        # 2_0: test 2 header 0 index
        dset_2_2_parsed = mp.read_excel(tmp_path / "dset_2_0.xlsx")
        dset_2_2_parsed.index = mi_index
        pd.testing.assert_frame_equal(dset_2_2, dset_2_2_parsed)

        # 0_2: test 0 header 2 index
        dset_2_2_parsed = mp.read_excel(tmp_path / "dset_0_2.xlsx")
        dset_2_2_parsed.index.names = mi_index.names
        dset_2_2_parsed.columns = mi_columns
        pd.testing.assert_frame_equal(dset_2_2, dset_2_2_parsed)

        # 0_0: test 0 header 0 index
        dset_2_2_parsed = mp.read_excel(tmp_path / "dset_0_0.xlsx")
        dset_2_2_parsed.index = mi_index
        dset_2_2_parsed.columns = mi_columns
        pd.testing.assert_frame_equal(dset_2_2, dset_2_2_parsed)

        # test legacy format of merge_cells=False
        dset_2_2.to_excel(
            tmp_path / "dset_2_2_no_merge.xlsx",
            engine=engine,
            merge_cells=False,
            header=True,
            index=True,
        )
        dset_2_2.to_excel(
            tmp_path / "dset_2_0_no_merge.xlsx",
            engine=engine,
            merge_cells=False,
            header=True,
            index=False,
        )
        dset_2_2.to_excel(
            tmp_path / "dset_0_2_no_merge.xlsx",
            engine=engine,
            merge_cells=False,
            header=False,
            index=True,
        )
        dset_2_2.to_excel(
            tmp_path / "dset_0_0_no_merge.xlsx",
            engine=engine,
            merge_cells=False,
            header=False,
            index=False,
        )

        # 2_2: test 2 header 2 index
        dset_2_2_parsed = mp.read_excel(tmp_path / "dset_2_2_no_merge.xlsx")
        dset_2_2_parsed.columns = mi_columns
        pd.testing.assert_frame_equal(dset_2_2, dset_2_2_parsed)

        # 2_0: test 2 header 0 index
        dset_2_2_parsed = mp.read_excel(tmp_path / "dset_2_0_no_merge.xlsx")
        dset_2_2_parsed.index = mi_index
        dset_2_2_parsed.columns = mi_columns
        pd.testing.assert_frame_equal(dset_2_2, dset_2_2_parsed)

        # 0_2: test 0 header 2 index
        dset_2_2_parsed = mp.read_excel(tmp_path / "dset_0_2_no_merge.xlsx")
        dset_2_2_parsed.index.names = mi_index.names
        dset_2_2_parsed.columns = mi_columns
        pd.testing.assert_frame_equal(dset_2_2, dset_2_2_parsed)

        # 0_0: test 0 header 0 index
        dset_2_2_parsed = mp.read_excel(tmp_path / "dset_0_0_no_merge.xlsx")
        dset_2_2_parsed.index = mi_index
        dset_2_2_parsed.columns = mi_columns
        pd.testing.assert_frame_equal(dset_2_2, dset_2_2_parsed)

    def test_1_2(self, tmp_path, engine):
        df_1_2 = pd.DataFrame(data, columns=reg_columns, index=mi_index)
        dset_1_2 = mp.Dataset(df_1_2)
        dset_1_2.to_excel(tmp_path / "dset_1_2.xlsx", engine=engine, header=True, index=True)

        # 1_2: test 1 header 2 index
        dset_1_2_parsed = mp.read_excel(tmp_path / "dset_1_2.xlsx")
        pd.testing.assert_frame_equal(dset_1_2, dset_1_2_parsed)

    def test_2_1(self, tmp_path, engine):
        df_2_1 = pd.DataFrame(data, columns=mi_columns, index=reg_index)
        dset_2_1 = mp.Dataset(df_2_1)
        dset_2_1.to_excel(tmp_path / "dset_2_1.xlsx", engine=engine, header=True, index=True)

        # 2_1: test 2 header 1 index
        dset_2_1_parsed = mp.read_excel(tmp_path / "dset_2_1.xlsx")
        pd.testing.assert_frame_equal(dset_2_1, dset_2_1_parsed)

    def test_basic_collection(self, tmp_path, engine):
        basic_list = mp.BasicList([reg_dset, mi_dset])

        with mp.MACPieExcelWriter(tmp_path / "basic_list.xlsx", engine=engine) as writer:
            basic_list.to_excel(writer)

        basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx")
        basic_list_from_file.index = reg_index
        pd.testing.assert_frame_equal(basic_list_from_file, reg_dset)

        basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx", sheet_name=0)
        basic_list_from_file.index = reg_index
        pd.testing.assert_frame_equal(basic_list_from_file, reg_dset)

        basic_list_from_file = mp.read_excel(
            tmp_path / "basic_list.xlsx", sheet_name="mi_test_name"
        )
        basic_list_from_file.index = mi_index
        pd.testing.assert_frame_equal(basic_list_from_file, mi_dset)

        basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx", sheet_name=[0, 1])
        reg_dset_parsed = basic_list_from_file[0]
        reg_dset_parsed.index = reg_index
        pd.testing.assert_frame_equal(reg_dset_parsed, reg_dset)
        mi_dset_parsed = basic_list_from_file[1]
        mi_dset_parsed.index = mi_index
        pd.testing.assert_frame_equal(mi_dset_parsed, mi_dset)

        basic_list_from_file = mp.read_excel(
            tmp_path / "basic_list.xlsx", sheet_name=[0, "mi_test_name"]
        )
        reg_dset_parsed = basic_list_from_file[0]
        reg_dset_parsed.index = reg_index
        pd.testing.assert_frame_equal(reg_dset_parsed, reg_dset)
        mi_dset_parsed = basic_list_from_file["mi_test_name"]
        mi_dset_parsed.index = mi_index
        pd.testing.assert_frame_equal(mi_dset_parsed, mi_dset)

        basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx", sheet_name=None)
        reg_dset_parsed = basic_list_from_file["NO_NAME"]
        reg_dset_parsed.index = reg_index
        pd.testing.assert_frame_equal(reg_dset_parsed, reg_dset)
        mi_dset_parsed = basic_list_from_file["mi_test_name"]
        mi_dset_parsed.index = mi_index
        pd.testing.assert_frame_equal(mi_dset_parsed, mi_dset)
