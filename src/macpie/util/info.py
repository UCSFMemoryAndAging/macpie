import json

from macpie.io.json import MACPieJSONEncoder
from macpie.tools import tablib as tablibtools


class Info(tablibtools.TablibWrapper):

    def __init__(self, *args, **kwargs):
        headers = kwargs.pop('headers', ('Key', 'Value'))
        super().__init__(*args, headers=headers, **kwargs)

    def append_dict(self, dictionary, tags=[]):
        for k, v in dictionary.items():
            self.append((k, json.dumps(v, cls=MACPieJSONEncoder)), tags=tags)

    def to_dict(self):
        # convert to native dict for easy reading
        return dict(zip(self.df['Key'],
                        self.df['Value'].apply(json.loads)))

    def print(self):
        print(self.export("cli", tablefmt="grid"))

    @classmethod
    def from_dict(cls, dictionary, **kwargs) -> "Info":
        tags = kwargs.pop('tags', [])
        instance = cls(**kwargs)
        instance.append_dict(dictionary, tags=tags)
        return instance
