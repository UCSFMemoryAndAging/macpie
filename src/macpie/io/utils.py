import pandas as pd
import tablib as tl


def detect_csv(stream, **kwargs):
    """Return True if given stream is valid CSV.

    Parameters
    ----------
    stream : file-like object
    **kwargs :
        All keyword arguments are passed through to the underlying
        :func:`detect_csv_delimiter` function.
    """
    try:
        detect_csv_delimiter(stream, **kwargs)
        return True
    except Exception:
        return False


def detect_csv_delimiter(stream, **kwargs):
    """If given stream is valid CSV, return the detected delimiter.

    Parameters
    ----------
    stream : file-like object
    **kwargs :
        All keyword arguments are passed through to the underlying
        :func:`pandas.read_csv` function.
    """

    # Use pandas code to sniff out the delimiter.
    # Specifically, execute the following block of code:
    # URL: https://github.com/pandas-dev/pandas/blob/50c119dce9005cb3e49c0cfb89f396aeecab94f1/pandas/io/parsers/python_parser.py#L201-L222

    # In order to do that:
    #   1. engine="python" ensures the PythonParser class is used
    #   2. sep=None branches to the proper block of code
    #   3. iterator=True makes sure a TextFileReader object is returned
    #   4. remove any kwargs that might interfere with the branching logic

    # If any exception is raised, then you can assume stream is not valid CSV.
    kwargs.pop("sep", None)
    kwargs.pop("delimiter", None)
    kwargs.pop("delim_whitespace", None)
    kwargs.pop("iterator", None)
    kwargs.pop("engine", None)

    reader = pd.read_csv(stream, engine="python", iterator=True, sep=None, **kwargs)
    delimiter = reader._engine.data.dialect.delimiter

    return delimiter


def detect_format_from_stream(stream):
    """Return a file's format given its stream.

    Parameters
    ----------
    stream : file-like object
    """

    try:
        csv_delimiter = detect_csv_delimiter(stream)
        if csv_delimiter == ",":
            return "csv"
        if csv_delimiter == "\t":
            return "tsv"
    except Exception:
        pass

    return tl.detect_format(stream)


def detect_format_from_filepath(filepath):
    """Return a file's format given its file path.

    Parameters
    ----------
    filepath : str, Path
    """

    with open(filepath, "r") as fh:
        fmt = detect_format_from_stream(fh)

    if fmt is None:
        with open(filepath, "rb") as fh:
            fmt = tl.detect_format(fh)

    return fmt


def detect_format(filepath_or_buffer):
    """Return a file's format.

    Parameters
    ----------
    filepath_or_buffer : various
        Path to a file or a file-like object
    """

    if pd.core.dtypes.common.is_file_like(filepath_or_buffer):
        return detect_format_from_stream(filepath_or_buffer)
    else:
        return detect_format_from_filepath(filepath_or_buffer)
