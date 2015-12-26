from json import dump, dumps, load, loads, JSONEncoder
import pickle


class PythonObjectEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}


def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct


def save_map_to_file(filename, json):
    with open(filename, "w") as outfile:
        dump(dumps(json), outfile, indent=2)


def load_map_from_file(infile):
    return loads(load(infile), object_hook=as_python_object)
