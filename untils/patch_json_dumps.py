from bson.objectid import ObjectId


def patch_json_dumps(package, encoder):
    """function for reset dumps cls JsonEncoder with handle ObjectId

    :param package: the model need patch
    :param encoder: the JSONEncoder of model
    :return:
    """
    package._base_dumps = package.dumps

    class JsonEncoder(encoder):
        """
        cls for handle dumps ObjectId
        return str(ObjectId()) when dumps ObjectId()
        """

        def default(self, o):
            if isinstance(o, ObjectId):  # 替换需要指定的类型
                return str(o)  # 返回指定的操作方法
            encoder.default(self, o)

    package.dumps = lambda *args, **kwargs: package._base_dumps(*args, cls=JsonEncoder, **kwargs)


"""
hook json.dumps and simplejson.dumps to handler ObjectId
specially, ujson and tornado.escape.json_encode will be patched with orjson.dumps in py3
or simplejson.dumps in py2

"""

# patch json
import json

patch_json_dumps(json, json.JSONEncoder)

# patch simplejson
try:
    import simplejson

    patch_json_dumps(simplejson, simplejson.JSONEncoder)
except:
    simplejson = json

"""
json.dumps datetime 类型
import json
import datetime


class MyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, o)
        # return supper().default(self, o)


result = json.dumps(datetime.date.today(), cls=MyEncoder)
print(result)
"""
