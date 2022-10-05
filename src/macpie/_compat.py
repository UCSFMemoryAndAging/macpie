from packaging.version import Version

import pandas as pd


# -----------------------------------------------------------------------------
# pandas compat
# -----------------------------------------------------------------------------

PANDAS_GE_15 = Version(pd.__version__) >= Version("1.5.0")
