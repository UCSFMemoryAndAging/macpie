import re

import click


def execute_multiline_query(cnx, query, echo=True):
    cur = cnx.cursor()
    iterator = cur.execute(query, params=None, multi=True)
    for result in iterator:
        if result.with_rows:
            # if statement produces a result set, need to fetch rows
            fetch_result = result.fetchall()
            if echo:
                click.echo(result)
                click.echo(fetch_result)
        elif result.rowcount > 0:
            # return number of rows affected by DML statements such as INSERT and UPDATE
            if echo:
                click.echo(f"Affected {result.rowcount} rows")
        else:
            if echo:
                click.echo(result)
    cnx.commit()


def show_create_procedure(cnx, procname):
    cur = cnx.cursor()
    cur.execute(f"SHOW CREATE PROCEDURE {procname}")
    result = cur.fetchall()
    result = result[0]
    (
        procname,
        sql_mode,
        proc_code,
        character_set_client,
        collation_connection,
        database_collation,
    ) = result

    if proc_code is None:
        raise ValueError("No proc code retrieved. Perhaps you don't have proper permissions.")

    return proc_code


def show_create_table(cnx, tablename):
    cur = cnx.cursor()
    cur.execute(f"SHOW CREATE TABLE {tablename}")
    result = cur.fetchall()
    create_table_str = result[0][1]
    return create_table_str


def transform_table(orig_table_str, col_transformations, new_tablename):
    """Transform a table definition into a masked table definition using
    column transformations defined in `col_transformations`.
    """

    new_table_str_lines = []

    for line in orig_table_str.splitlines(keepends=True):
        line = transform_col_in_line(line, col_transformations)
        if line:
            new_table_str_lines.append(line)
    new_table_str_lines.append(";")
    new_table_str_lines[0] = f"CREATE TABLE `{new_tablename}` (\n"
    new_table_str_lines.insert(0, f"DROP TABLE IF EXISTS `{new_tablename}`;\n")
    new_table_str = "".join(new_table_str_lines)
    return new_table_str


def transform_col_in_line(line, col_transformations):
    """Given a line in a table definition, transform any column names
    for which a transformation is defined in `col_transformations`.
    """

    col_patterns = [
        "^\s*`([a-zA-Z0-9_]+)`.*,$",  # fields
        "^\s*PRIMARY KEY \(`([a-zA-Z0-9_]+)`\)$",  # primary key
    ]
    for pat in col_patterns:
        match = re.search(pat, line)
        if match:
            colname = match[1]
            if colname in col_transformations:
                new_colname = col_transformations[colname]
                if new_colname is None:  # drop the field
                    return ""
                else:
                    return line.replace(colname, new_colname)
    return line
