"""
python -m scripts.test_excel_performance
"""

import io
import pathlib
import pkgutil
import tempfile
from timeit import default_timer as timer

import pandas as pd

import macpie as mp


def load_csv():
    rawdata = pkgutil.get_data(__package__, "df_large.csv")
    csvdata = rawdata.decode("utf-8")
    csvstream = io.StringIO(csvdata)
    df = pd.read_csv(csvstream)
    csvstream.close()
    return df


start = timer()
df_orig = load_csv()
end = timer()
print(f"load csv to df: {end - start} sec")


with tempfile.TemporaryDirectory() as tmpdirname:
    tmpdirname = pathlib.Path(tmpdirname)

    dset = mp.Dataset(data=df_orig.copy())
    start = timer()
    dset.to_excel(tmpdirname / "dset_xlsxwriter.xlsx", engine="mp_xlsxwriter")
    end = timer()
    print(f"dset xlsxwriter: {end - start} sec")

    dset = mp.Dataset(data=df_orig.copy())
    start = timer()
    dset.to_excel(tmpdirname / "dset_openpyxl.xlsx", engine="mp_openpyxl")
    end = timer()
    print(f"dset openpyxl: {end - start} sec")

    df = df_orig.copy()
    start = timer()
    df.to_excel(tmpdirname / "df_xlsxwriter.xlsx", engine="xlsxwriter")
    end = timer()
    print(f"df xlsxwriter: {end - start} sec")

    df = df_orig.copy()
    start = timer()
    df.to_excel(tmpdirname / "df_openpyxl.xlsx", engine="openpyxl")
    end = timer()
    print(f"df openpyxl: {end - start} sec")


if __name__ == "__main__":
    pass
