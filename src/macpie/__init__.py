# flake8: noqa

__version__ = "0.7.0"


# let init-time option registration happen
import macpie.core.config_init
from macpie import pandas, testing, util
from macpie._config import get_option, reset_option, set_option
from macpie.core.api import *
from macpie.io.api import *
from macpie.pandas.accessors import MacDataFrameAccessor, MacSeriesAccessor
from macpie.tools.api import *
