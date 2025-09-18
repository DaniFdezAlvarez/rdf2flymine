from pyshexc.parser_impl.generate_shexj import parse as parse_shex
from ShExJSG.ShExJ import Shape
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

#  URIS

_RDF_tYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

class Utils(object):

    @staticmethod
    def load_file(file_path: str):
        with open(file_path, encoding="utf-8") as in_stream:
            return in_stream.read()

    @staticmethod
    def uri_to_var_camel_case(uri: str):
        pass  # TODO


    @staticmethod
    def uri_to_readable_label(uri: str):
        pass  # TODO


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
            print(type(a_shape))
            shape_var = Utils.uri_to_var_camel_case(a_shape.id)
            shape_label = Utils.uri_to_readable_label(a_shape.id)
            target_class_node = Shex2Flymine._empty_class_node()
            self._json_model[shape_var] = target_class_node
            target_class_node[_DISPLAY_NAME] = shape_label
            target_class_node[_NAME] = shape_var
            target_class_node[_TERM] = self._look_for_shape_class(a_shape)
            self._fill_class_links(a_shape, target_class_node)

            # print("-----")
            # for exp in a_shape.expression.expressions:
            #     print (exp)

    def _fill_class_links(self, shape: Shape, target_class_node: dict):
        for exp in shape.expression.expressions:
            if self._is_typing_exp(exp):
                pass  # Skip it, do nothing
            elif self._has_literal_object(exp):
                self._add_att_entry(shape, exp)
            elif self._has_unbounded_cardinality(exp):
                self._add_collections_entry(shape,exp)
            else:  # The object is a shape and the max cardinality must be 1
                self._add_reference_entry(shape, exp)

    def _add_reference_entry(self, shape, exp):
        pass

    def _add_collections_entry(self, shape, exp):
        pass

    def _has_unbounded_cardinality(self, exp):
        pass

    def _add_att_entry(self, shape, exp):
        pass

    def _has_literal_object(self, exp):
        pass

    def _is_typing_exp(self, exp):
        pass

    #     print (exp)
    def _look_for_shape_class(self, a_shape: Shape):
        for exp in a_shape.expression.expressions:
            if str(exp.predicate) == _RDF_tYPE:
                return str(exp.valueExpr.values[0])

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
