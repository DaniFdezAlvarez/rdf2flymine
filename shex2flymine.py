from pyshexc.parser_impl.generate_shexj import parse as parse_shex
from ShExJSG.ShExJ import Shape, TripleConstraint, NodeConstraint, IRIREF
import os.path as pth
import json
import re
from shexer.shaper import Shaper
from shexer.consts import MIXED_INSTANCES, ALL_EXAMPLES

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
_IS_INTERFACE = "isInterface"
_TAGS = "tags"
_EXECUTION_TIME = "executionTime"
_WAS_SUCCESFUL = "wasSuccessful"
_ERROR = "error"
_STATUS_CODE = "statusCode"

_TODO = "WARNING! TO-DO"

#  URIS

_RDF_tYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

# MACROS pyshex
_IRI = "iri"

# Type mappings

_JAVA_STRING = "java.lang.String"
_TYPE_MAP = {
    "http://www.w3.org/2001/XMLSchema#string": "java.lang.String",
    "http://www.w3.org/2001/XMLSchema#boolean": "java.lang.Boolean",
    "http://www.w3.org/2001/XMLSchema#decimal": "java.math.BigDecimal",
    "http://www.w3.org/2001/XMLSchema#integer": "java.math.Integer",
    "http://www.w3.org/2001/XMLSchema#int": "java.lang.Integer",
    "http://www.w3.org/2001/XMLSchema#long": "java.lang.Long",
    "http://www.w3.org/2001/XMLSchema#short": "java.lang.Short",
    "http://www.w3.org/2001/XMLSchema#byte": "java.lang.Byte",
    "http://www.w3.org/2001/XMLSchema#float": "java.lang.Float",
    "http://www.w3.org/2001/XMLSchema#double": "java.lang.Double",
    "http://www.w3.org/2001/XMLSchema#date": "java.time.LocalDate",
    "http://www.w3.org/2001/XMLSchema#time": "java.time.LocalTime",
    "http://www.w3.org/2001/XMLSchema#dateTime": "java.time.LocalDateTime",
    "http://www.w3.org/2001/XMLSchema#anyURI": "java.net.URI",
}


class Utils(object):

    @staticmethod
    def load_file(file_path: str):
        with open(file_path, encoding="utf-8") as in_stream:
            return in_stream.read()

    @staticmethod
    def write_json(target_obj: dict, out_path: str):
        with open(out_path, "w", encoding="utf-8") as out_stream:
            json.dump(target_obj, out_stream, indent=4)

    @staticmethod
    def uri_to_var_camel_case(uri: str, capitalize=False):
        """
            Extract the last part of a URI and convert it into camelCase,
            while preserving acronyms (e.g., 'DNATrace' -> 'DNATrace').

            Examples:
                http://example.org/PersonName      -> personName
                http://example.org/person_name     -> personName
                http://example.org/person-name     -> personName
                http://example.org/PERSON_NAME     -> personName
                http://example.org#Person          -> person
                http://example.org/AnalysisOfDNATrace -> analysisOfDNATrace
            """

        fragment = re.split(r'[#/:]', uri)[-1]

        # Regex to split words, keeping acronyms intact
        words = re.findall(r'[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+', fragment)

        if not words:
            return ""

        # First word lowercased, others capitalize first letter (unless acronym)
        result_words = [words[0].lower()]
        for w in words[1:]:
            if w.isupper():  # acronym
                result_words.append(w)
            else:
                result_words.append(w.capitalize())

        candidate = "".join(result_words)
        if capitalize:
            return candidate[0].upper() + candidate[1:]
        return candidate

    @staticmethod
    def uri_to_readable_label(uri: str):
        """
            Extract the last part of a URI and convert it into a readable label
            with spaces between words.
            First word capitalized, subsequent words lowercase (unless acronym).

            Examples:
                http://example.org/PersonName        -> "Person name"
                http://example.org/person_name       -> "Person name"
                http://example.org/person-name       -> "Person name"
                http://example.org/PERSON_NAME       -> "Person name"
                http://example.org/AnalysisOfDNATrace -> "Analysis of DNA trace"
            """

        fragment = re.split(r'[#/:]', uri)[-1]

        # Regex to split words, keeping acronyms intact
        words = re.findall(r'[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+', fragment)

        if not words:
            return ""

        result_words = []
        for i, w in enumerate(words):
            if i == 0:
                # First word: capitalize first letter only
                result_words.append(w.capitalize())
            else:
                if w.isupper():  # keep acronyms
                    result_words.append(w)
                else:  # lowercase otherwise
                    result_words.append(w.lower())

        return " ".join(result_words)

    @staticmethod
    def map_xsd_to_java(xsd_type: str):
        if xsd_type in _TYPE_MAP:
            return _TYPE_MAP[xsd_type]
        return ""




class RDF2ShEx(object):

    def __init__(self, endpoint_url: str, out_shex_file: str, instance_limits: int):
        self._endpoint_url = endpoint_url,
        self._out_shex_file = out_shex_file
        self._instance_limits = instance_limits

    def run(self):
        namespaces = {
            "http://example.org/": "ex",
            "http://www.w3.org/XML/1998/namespace/": "xml",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
            "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
            "http://www.w3.org/2001/XMLSchema#": "xsd",
            "http://bio2rdf.org/": "bio2rdf"
        }

        shaper = Shaper(all_classes_mode=True,
                        url_endpoint=self._endpoint_url,
                        namespaces_dict=namespaces,
                        disable_comments=False,
                        depth_for_building_subgraph=1,
                        track_classes_for_entities_at_last_depth_level=True,
                        instances_cap=self._instance_limits,
                        instances_report_mode=MIXED_INSTANCES,
                        examples_mode=ALL_EXAMPLES
                        )
        shaper.shex_graph(output_file=self._out_shex_file)


class Shex2Flymine(object):

    def __init__(self, shex_content_path: str, out_path: str):
        self._shex_str = Utils.load_file(shex_content_path)
        self._out_path = out_path

        self._shex_model = None
        self._json_model = None

    def run(self):
        self._parse_shex()
        self._map_to_model()
        self._write_results()

    def _parse_shex(self):
        self._shex_model = parse_shex(self._shex_str)

    def _map_to_model(self):
        self._json_model = Shex2Flymine._empty_skeleton_model()
        self._map_shapes()

    def _write_results(self):
        Utils.write_json(target_obj=self._json_model,
                         out_path=self._out_path)

    def _map_shapes(self):
        for a_shape in self._shex_model.shapes:
            shape_var = Utils.uri_to_var_camel_case(a_shape.id)
            shape_label = Utils.uri_to_readable_label(a_shape.id)
            target_class_node = Shex2Flymine._empty_class_node()
            self._json_model[_MODEL][_CLASSES][shape_var] = target_class_node
            target_class_node[_DISPLAY_NAME] = shape_label
            target_class_node[_NAME] = shape_var
            target_class_node[_TERM] = self._look_for_shape_class(a_shape)
            self._fill_class_links(a_shape, target_class_node)

    def _fill_class_links(self, shape: Shape, target_class_node: dict):
        for exp in shape.expression.expressions:
            if self._is_typing_exp(exp):
                pass  # Skip it, do nothing
            elif self._has_literal_object(exp):
                self._add_att_entry_natural_att(target_class_node, exp)
            elif self._has_IRI_object(exp):
                self._add_att_entry_IRI(target_class_node, exp)
            elif self._has_shape_ref_unbounded_cardinality(exp):
                self._add_collections_entry(target_class_node, exp)
            else:  # The object is a shape and the max cardinality must be 1
                self._add_reference_entry(target_class_node, exp)

    def _add_link_with_shape_entry(self, class_node: dict, exp: TripleConstraint, dict_key: str):
        var_name_predicate = Utils.uri_to_var_camel_case(str(exp.predicate))
        if var_name_predicate in class_node[dict_key]:
            var_name_predicate = Shex2Flymine.gen_non_ambiguous_var_name(original=var_name_predicate,
                                                                         target_node=class_node[_REFERENCES])
        label_predicate = Utils.uri_to_readable_label(str(exp.predicate))
        class_node[dict_key][var_name_predicate] = Shex2Flymine._empty_ref_or_collection_node()
        class_node[dict_key][var_name_predicate][_DISPLAY_NAME] = label_predicate
        class_node[dict_key][var_name_predicate][_NAME] = var_name_predicate

        var_name_ref_type = Utils.uri_to_var_camel_case(str(exp.valueExpr),
                                                        capitalize=True)
        class_node[dict_key][var_name_predicate][_REF_TYPE] = var_name_ref_type

    def _add_reference_entry(self, class_node: dict, exp: TripleConstraint):
        self._add_link_with_shape_entry(class_node=class_node,
                                        exp=exp,
                                        dict_key=_REFERENCES)

    def _add_collections_entry(self, class_node: dict, exp: TripleConstraint):
        self._add_link_with_shape_entry(class_node=class_node,
                                        exp=exp,
                                        dict_key=_COLLECTIONS)

    def _add_att_entry(self, class_node: dict, exp: TripleConstraint, java_type: str):
        var_name_predicate = Utils.uri_to_var_camel_case(str(exp.predicate))
        if var_name_predicate in class_node[_ATTS]:
            var_name_predicate = Shex2Flymine.gen_non_ambiguous_var_name(original=var_name_predicate,
                                                                         target_node=class_node[_REFERENCES])
        label_predicate = Utils.uri_to_readable_label(str(exp.predicate))
        class_node[_ATTS][var_name_predicate] = Shex2Flymine._empty_att_node()
        class_node[_ATTS][var_name_predicate][_DISPLAY_NAME] = label_predicate
        class_node[_ATTS][var_name_predicate][_NAME] = var_name_predicate
        class_node[_ATTS][var_name_predicate][_TYPE] = java_type

    def _add_att_entry_natural_att(self, class_node: dict, exp: TripleConstraint):
        self._add_att_entry(class_node=class_node,
                            exp=exp,
                            java_type=Utils.map_xsd_to_java(str(exp.valueExpr.datatype)))

    def _add_att_entry_IRI(self, class_node: dict, exp: TripleConstraint):
        self._add_att_entry(class_node=class_node,
                            exp=exp,
                            java_type=_JAVA_STRING)

    @staticmethod
    def _has_shape_ref_unbounded_cardinality(exp: TripleConstraint):
        return type(exp.valueExpr) == IRIREF and exp.max == -1

    @staticmethod
    def _has_shape_ref_bounded_cardinality(exp: TripleConstraint):
        return type(exp.valueExpr) == IRIREF and (exp.max is None or exp.max == 1)

    @staticmethod
    def _has_literal_object(exp: TripleConstraint):
        return type(exp.valueExpr) == NodeConstraint and exp.valueExpr.datatype is not None

    @staticmethod
    def _has_IRI_object(exp: TripleConstraint):
        return type(exp.valueExpr) == NodeConstraint and exp.valueExpr.nodeKind == _IRI

    @staticmethod
    def _is_typing_exp(exp: TripleConstraint):
        return str(exp.predicate) == _RDF_tYPE

    @staticmethod
    def _look_for_shape_class(a_shape: Shape):
        for exp in a_shape.expression.expressions:
            if Shex2Flymine._is_typing_exp(exp):
                return str(exp.valueExpr.values[0])

    @staticmethod
    def gen_non_ambiguous_var_name(original: str, target_node: dict):
        count = 1
        candidate = original + str(count)
        while candidate in target_node:
            count += 1
            candidate = original + str(count)
        return candidate

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
            _DISPLAY_NAME: _TODO,
            _NAME: _TODO,
            _REVERSE_REF: _TODO,
            _REF_TYPE: _TODO
        }

    @staticmethod
    def _empty_att_node():
        return {
            _DISPLAY_NAME: _TODO,
            _NAME: _TODO,
            _TERM: _TODO,
            _TYPE: _TODO
        }

class RDF2Flymine(object):
    def __init__(self, endpoint_url: str, out_shex_file: str, instance_limits: int, out_model_file: str):
        self._r2s = RDF2ShEx(endpoint_url=endpoint_url,
                       out_shex_file=out_shex_file,
                       instance_limits=instance_limits)
        self._s2f = Shex2Flymine(shex_content_path=out_shex_file,
                           out_path=out_model_file)

    def run(self):
        self._r2s.run()
        self._s2f.run()



if __name__ == "__main__":

    #  ShEx to FlyMine model
    s2f = Shex2Flymine(shex_content_path=_PTH_SEP.join(("files",
                                                        "flymine_3_instances_all_classes_no_annotations.shex")),
                       out_path=_PTH_SEP.join(("files",
                                               "model.json"))
                       )
    s2f.run()

    # #  RDF to ShEx
    # r2s = RDF2ShEx(endpoint_url="https://dx.dbcls.jp/qlever-flymine/sparql",
    #                out_shex_file=_PTH_SEP.join(("files",
    #                                             "flymine_schema.shex")),
    #                instance_limits=3)
    # r2s.run()

    # # RDF to FlyMine
    # r2f = RDF2Flymine(endpoint_url="https://dx.dbcls.jp/qlever-flymine/sparql",
    #                   out_shex_file=_PTH_SEP.join(("files",
    #                                             "flymine_schema.shex")),
    #                   instance_limits=3,
    #                   out_model_file=_PTH_SEP.join(("files",
    #                                            "model.json"))
    #                   )