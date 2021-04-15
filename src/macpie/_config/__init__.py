"""
macpie._config is considered explicitly upstream of everything else in macpie.

Should have no intra-macpie dependencies.
"""

__all__ = [
    "config",
    "get_option",
    "reset_option",
    "set_option"
]

from macpie._config import config
from macpie._config.config import (
    get_option,
    reset_option,
    set_option,
)
