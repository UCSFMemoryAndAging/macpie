class MacpieException(Exception):
    """Macpie common exception."""


class UnsupportedFormat(MacpieException, NotImplementedError):
    """Format not supported."""
