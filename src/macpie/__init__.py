# flake8: noqa

__version__ = "0.5.0"


from macpie._config import get_option, set_option, reset_option

# let init-time option registration happen
import macpie.core.config_init

from macpie.core.api import *

from macpie.io.api import *

from macpie.tools.api import *

from macpie.pandas.accessors import MacDataFrameAccessor, MacSeriesAccessor

from macpie import pandas

from macpie import testing

from macpie import util
