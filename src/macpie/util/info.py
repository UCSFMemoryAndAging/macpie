import json

from macpie.io.json import MACPieJSONEncoder
from macpie.tools import tablib as tablibtools


class Info(tablibtools.TablibWrapper):
    """Tabular representation of basic information using two columns
    only: a ``Key`` column and a ``Value`` column, using
    a :class:`macpie.tablibtools.TablibWrapper`.

    All ``Value``'s are encoded as JSON. But you can call the ``to_dict()`` method
    to decode the JSON back to native Python objects.

    It is a subclass of :class:`macpie.tablibtools.TablibWrapper`, and therefore
    can be initialized with data the same way.
    """

    def __init__(self, *args, **kwargs):
        headers = kwargs.pop('headers', ('Key', 'Value'))
        super().__init__(*args, headers=headers, **kwargs)

    def append_dict(self, dictionary, tags=[]):
        """Add a dictionary of items. ``json.dumps`` is called on each ``Value``.

        :param dictionary: Dict to add
        :param tags: tags to add to dict items
        """
        for k, v in dictionary.items():
            self.append((k, json.dumps(v, cls=MACPieJSONEncoder)), tags=tags)

    def to_dict(self):
        """Convert to native dict for easy reading/access.
        ``json.loads`` is called on each ``Value``.
        """
        # convert to a native dict for easy reading
        return dict(zip(self.df['Key'],
                        self.df['Value'].apply(json.loads)))

    @classmethod
    def from_dict(cls, dictionary, **kwargs) -> "Info":
        """Construct :class:`Info` from a Python dictionary.
        """
        tags = kwargs.pop('tags', [])
        instance = cls(**kwargs)
        instance.append_dict(dictionary, tags=tags)
        return instance
