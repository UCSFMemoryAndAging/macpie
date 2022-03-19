import datetime
import decimal
import json
from pathlib import Path


class MACPieJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json_dict"):
            return obj.to_json_dict()

        if hasattr(obj, "to_dict"):
            return obj.to_dict()

        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.isoformat(),
            }

        if isinstance(obj, datetime.date):
            return {"_type": "date", "value": obj.isoformat()}

        if isinstance(obj, decimal.Decimal):
            return str(obj)

        if isinstance(obj, Path):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


class MACPieJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "_type" not in obj:
            return obj

        type = obj["_type"]
        if type == "datetime":
            return datetime.datetime.fromisoformat(obj["value"])

        if type == "date":
            return datetime.date.fromisoformat(obj["value"])

        return obj
