from pyshexc.parser_impl.generate_shexj import parse as parse_shex
import os.path as pth

_PTH_SEP = pth.sep

# KEYS

_MODEL = "model"
_PACKAGE = "package"
_CLASSES = "classes"
_EXTENDS = "extends"
_REFERENCES = "references"
_ATTS = "attributes"
_COLLECTIONS = "collections"
_DISPLAY_NAME = "displayName"
_NAME = "name"
_REVERSE_REF = "reverseReference"
_REF_TYPE = "referenceType"
_COUNT = "count"
_TERM = "term"
_TYPE = "type"
_IS_INTERFACE = ""
_TAGS = "tags"
_EXECUTION_TIME = "executionTime"
_WAS_SUCCESFUL = "wasSuccessful"
_ERROR = "error"
_STATUS_CODE = "statusCode"

_TODO = "WARNING! TO-DO"


class Utils(object):

    @staticmethod
    def load_file(file_path: str):
        with open(file_path, encoding="utf-8") as in_stream:
            return in_stream.read()


class Shex2Flymine(object):

    def __init__(self, shex_content_path: str, out_path: str):
        self._shex_str = Utils.load_file(shex_content_path)
        self._out_path = out_path

        self._shex_model = None
        self._json_model = None

    def run(self):
        self._parse_shex()
        self._map_to_model()
        # self._write_results()

    def _parse_shex(self):
        self._shex_model = parse_shex(self._shex_str)

    def _map_to_model(self):
        self._json_model = Shex2Flymine._empty_skeleton_model()
        self._map_shapes()

    def _map_shapes(self):
        for a_shape in self._shex_model.shapes:
            print("-----")
            for exp in a_shape.expression.expressions:
                print (exp)

    @staticmethod
    def _empty_skeleton_model():
        return {
            _MODEL: {
                _PACKAGE: _TODO,
                _CLASSES: {},
                _EXECUTION_TIME: _TODO,
                _WAS_SUCCESFUL: _TODO,
                _ERROR: _TODO,
                _STATUS_CODE: _TODO
            }
        }

    @staticmethod
    def _empty_class_node():
        return {
            _EXTENDS: [],
            _REFERENCES: {},
            _COLLECTIONS: {},
            _ATTS: {},
            _DISPLAY_NAME: _TODO,
            _NAME: _TODO,
            _COUNT: _TODO,
            _TERM: _TODO,
            _IS_INTERFACE: _TODO,
            _TAGS: []
        }


    @staticmethod
    def _empty_ref_or_collection_node():
        return {
            _DISPLAY_NAME : _TODO,
            _NAME : _TODO,
            _REVERSE_REF : _TODO,
            _REF_TYPE : _TODO
        }

    @staticmethod
    def _empty_att_node():
        return {
            _DISPLAY_NAME: _TODO,
            _NAME: _TODO,
            _TERM: _TODO,
            _TYPE: _TODO
        }


if __name__ == "__main__":
    s2f = Shex2Flymine(shex_content_path=_PTH_SEP.join(("files",
                                                        "flymine_3_instances_all_classes_no_annotations.shex")),
                       out_path=_PTH_SEP.join(("files",
                                               "model.json")))
    s2f.run()
