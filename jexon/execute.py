import sys
import json
from . import internal
from copy import deepcopy
from string import Template
from jsonschema import Draft7Validator, validators

_SCHEMA_JAYSON_CONFIG = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "jayson config",
    "description": "imports and parameters for jexon",
    "type": "object",
    "default": {},
    "additionalProperties": False,
    "properties": {
        "parameters": {
            "type": "array",
            "default": [],
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "value"],
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "value": {
                    }
                }
            }
        },
        "imports": {
            "type": "array",
            "default": [],
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["import"],
                "properties": {
                    "import": {
                        "type": "string",
                        "pattern": "^[^\\*]"
                    },
                    "as": {
                        "type": "string",
                        "default": ""
                    },
                    "from": {
                        "type": "string",
                        "default": ""
                    }
                }
            }
        }
    }
}

if __name__ == "__main__":

    sys.tracebacklimit = -1

    if len(sys.argv) < 3:
        raise ValueError(
            "Not enough arguments provided to jexon - expected at least two (<input_file_name> <output_file_name>)")

    if len(sys.argv) > 4:
        raise ValueError(
            "Too many arguments provided to jexon - expected at most three (<input_file_name> <output_file_name> [<config_file_name>])")

    ifile, ofile = sys.argv[1], sys.argv[2]

    formats = {}
    configs = {"imports": [], "parameters": []}
    if len(sys.argv) == 4:

        cfile = sys.argv[3]

        with open(cfile) as ifp:
            configs = json.load(ifp)

        class DefaultDraft7Validator():
            def __init__(self, schema):
                self._schema = schema

                def extend_with_default(validator_class):
                    validate_properties = validator_class.VALIDATORS["properties"]

                    def set_defaults(validator, properties, instance, schema):
                        for property, subschema in properties.items():
                            if "default" in subschema and instance != None:
                                instance.setdefault(
                                    property, deepcopy(subschema["default"]))

                        for error in validate_properties(
                            validator, properties, instance, schema,
                        ):
                            yield error

                    return validators.extend(
                        validator_class, {"properties": set_defaults},
                    )

                self._vald7 = extend_with_default(Draft7Validator)

            def validate_defaults(self, me):
                try:
                    self._vald7(self._schema).validate(me)
                except Exception as e:
                    raise ValueError("jexon config validation of '" + '/'.join(
                        [str(_) for _ in e.absolute_path]) + "' failed with: " + e.message) from None

        DefaultDraft7Validator(
            _SCHEMA_JAYSON_CONFIG).validate_defaults(configs)

        formats = {p["name"]: "'" + p["value"] + "'" if isinstance(p["value"], str)
                   else p["value"]
                   for p in configs["parameters"]}

    def load_ipt(ifp):
        try:
            return json.load(ifp)
        except:
            ifp.seek(0)

        try:
            return ifp.readline()
        except:
            ifp.seek(0)

        raise ValueError(
            "jexon input file '" + ifile + "' is invalid.")

    with open(ifile) as ifp:
        ipt = load_ipt(ifp)

    def evaluate(rhs):
        if formats:
            rhs = Template(rhs).safe_substitute(formats)
        return internal.__eval__(rhs)

    def rec(json_input, path):
        if isinstance(json_input, dict):
            for k in json_input.keys():
                if isinstance(json_input[k], str):
                    try:
                        json_input[k] = evaluate(json_input[k])
                    except Exception as e:
                        raise ValueError(
                            str(e) + ". See jexon path '" + path + "/" + k + "'") from None
                elif isinstance(json_input[k], int) or isinstance(json_input[k], float) or isinstance(json_input[k], bool):
                    pass
                else:
                    rec(json_input[k], path + "/" + k)
        elif isinstance(json_input, list):
            for i in range(len(json_input)):
                if isinstance(json_input[i], str):
                    try:
                        json_input[i] = evaluate(json_input[i])
                    except Exception as e:
                        raise ValueError(
                            str(e) + ". See jexon path '" + path + "/" + str(i) + "'") from None
                elif isinstance(json_input[i], int) or isinstance(json_input[i], float) or isinstance(json_input[i], bool):
                    pass
                else:
                    rec(json_input[i], path + "/" + str(i))
        return

    for index, impt in enumerate(configs["imports"]):
        try:
            if impt["as"] and impt["from"]:
                internal.__exec__(
                    "!globals()['{as}'] = getattr(importlib.import_module('{from}'),'{import}')".format(**impt))

            if impt["as"] and not impt["from"]:
                internal.__exec__(
                    "!globals()['{as}'] = importlib.import_module('{import}')".format(**impt))

            if not impt["as"] and impt["from"]:
                internal.__exec__(
                    "!globals()['{import}'] = getattr(importlib.import_module('{from}'),'{import}')".format(**impt))

            if not impt["as"] and not impt["from"]:
                internal.__exec__(
                    "!globals()['{import}'] = importlib.import_module('{import}')".format(**impt))

        except Exception as e:
            raise ValueError(
                str(e) + " - see jexon import at index (" + str(index) + ")") from None

    if isinstance(ipt, str):
        ipt = evaluate(ipt)
    else:
        rec(ipt, "")

    with open(ofile, 'w+') as ofp:
        json.dump(ipt, ofp, indent=4)
