# flake8: noqa

try:
    import networkx as nx

    _has_networkx = True
except ImportError:
    _has_networkx = False

if not _has_networkx:
    raise ImportError("The 'graph' module requires the 'networkx' library.")

from .basicgraph import BasicGraph
from .executablegraph import ExecutableGraph
