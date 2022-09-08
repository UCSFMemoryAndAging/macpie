"""
Table Schema builders

https://specs.frictionlessdata.io/json-table-schema/
"""
from pandas.io.json._table_schema import (
    build_table_schema as pd_build_table_schema,
    parse_table_schema as pd_parse_table_schema,
)

from macpie.core.api import Dataset


TABLE_SCHEMA_VERSION = "0.6"


def build_table_schema(
    data: Dataset,
    index: bool = True,
    primary_key: bool | None = None,
    version: bool = True,
) -> dict:
    schema = pd_build_table_schema(data, index=index, primary_key=primary_key, version=version)
    schema["className"] = type(data).__name__
    schema["idColName"] = data.id_col_name
    schema["dateColName"] = data.date_col_name
    schema["id2ColName"] = data.id2_col_name
    schema["name"] = data.name
    schema["displayName"] = data.display_name
    schema["excelSheetname"] = data.excel_sheetname
    schema["tags"] = data.tags

    if version:
        schema["macpieVersion"] = TABLE_SCHEMA_VERSION

    return schema


def parse_table_schema(json, precise_float):

    df = pd_parse_table_schema(json, precise_float)

    table = loads(json, precise_float=precise_float)
    col_order = [field["name"] for field in table["schema"]["fields"]]
    df = DataFrame(table["data"], columns=col_order)[col_order]

    dtypes = {
        field["name"]: convert_json_field_to_pandas_type(field)
        for field in table["schema"]["fields"]
    }

    # No ISO constructor for Timedelta as of yet, so need to raise
    if "timedelta64" in dtypes.values():
        raise NotImplementedError('table="orient" can not yet read ISO-formatted Timedelta data')

    df = df.astype(dtypes)

    if "primaryKey" in table["schema"]:
        df = df.set_index(table["schema"]["primaryKey"])
        if len(df.index.names) == 1:
            if df.index.name == "index":
                df.index.name = None
        else:
            df.index.names = [None if x.startswith("level_") else x for x in df.index.names]

    return df
