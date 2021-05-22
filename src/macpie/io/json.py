"""
Base and utility classes for macpie objects.
"""

import datetime
from dateutil import parser
import json
from pathlib import Path


class MACPieJSONEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, obj):
        if hasattr(obj, 'to_json_dict'):
            return obj.to_json_dict()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.strftime("%s %s" % (
                    self.DATE_FORMAT, self.TIME_FORMAT
                ))
            }
        if isinstance(obj, Path):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class MACPieJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' not in obj:
            return obj
        type = obj['_type']
        if type == 'datetime':
            return parser.parse(obj['value'])
        return obj
