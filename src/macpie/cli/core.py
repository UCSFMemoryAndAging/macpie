from pathlib import Path
from typing import Any, Optional

import click

from macpie.tools import io as iotools


class ClickPath(click.Path):
    """A Click path argument that returns a ``Path``, not a string.
    """
    def convert(
        self,
        value: str,
        param: Optional[click.core.Parameter],
        ctx: Optional[click.core.Context],
    ) -> Any:
        """
        Return a ``Path`` from the string ``click`` would have created with
        the given options.
        """
        return Path(super().convert(value=value, param=param, ctx=ctx)).resolve(strict=True)


def allowed_file(p):
    """Determines if a file is considered allowed
    """
    stem = p.stem
    if stem.startswith('~'):
        return False
    if iotools.has_csv_extension(p) or iotools.has_excel_extension(p):
        return True
    return False
