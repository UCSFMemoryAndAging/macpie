# flake8: noqa

__version__ = "0.5.0"


from macpie._config import get_option, set_option, reset_option


# let init-time option registration happen
import macpie.core.config_init

# top-level api. ordering matters
from macpie import datetimetools
from macpie import itertools
from macpie import lltools
from macpie import openpyxltools
from macpie import pathtools
from macpie import shelltools
from macpie import strtools
from macpie import tablibtools
from macpie import xlsxwritertools
from macpie import validatortools

from macpie.core.api import *

from macpie.collections import *

from macpie.io import *

from macpie.operators import *

from macpie.pandas.accessor_ser import MacSeriesAccessor
from macpie.pandas.accessor_df import MacDataFrameAccessor


# sub-level api
from macpie import pandas

from macpie import testing

from macpie import util
