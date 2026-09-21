"""Schema comes from the protocol's section 16; voting paths are explicit."""
import json
import re
import unicodedata

from jsonschema import Draft202012Validator

EDGES = ("S_to_F", "S_to_P", "F_to_P", "P_to_E", "E_to_S", "E_to_F", "E_to_P")
FUNCTION_LABELS = ("Present", "Absent", "Unclear")
PRESENCE_LABELS = ("Explicit", "Inferential", "Absent", "Unclear")
VALIDATION_LABELS = ("V0", "V1", "V2", "NA")
ALLOWED_LABELS = {
    "paper_input_completeness": ("Complete", "PossiblyTruncated"),
    "systems.*.system_input_completeness": ("Complete", "PossiblyTruncated", "NotApplicable"),
    "systems.*.functions.S.label": FUNCTION_LABELS,
    "systems.*.functions.F.label": FUNCTION_LABELS,
    "systems.*.functions.P.label": FUNCTION_LABELS,
    "systems.*.functions.E.label": FUNCTION_LABELS,
    "systems.*.functions.F.mode": ("Static", "Dynamic", "Unclear", "NA"),
    "systems.*.functions.E.relational_adaptation": ("Yes", "No", "Unclear", "NA"),
    **{f"systems.*.dependencies.{edge}.presence": PRESENCE_LABELS for edge in EDGES},
    **{f"systems.*.dependencies.{edge}.validation": VALIDATION_LABELS for edge in EDGES},
}
VOTABLE_FIELDS = tuple(ALLOWED_LABELS)
# Confidence is an auditor's certainty, retained with evidence, not voted.
EVIDENCE_FIELDS = ("evidence", "location", "rationale", "confidence")


class AuditValidationError(ValueError):
    def __init__(self, message, error_type="schema_invalid"):
        super().__init__(message)
        self.error_type = error_type


def system_key(name):
    # No fuzzy name matching: distinct systems must never silently be merged.
    return " ".join(unicodedata.normalize("NFKC", name).casefold().split())


def get_path(obj, path):
    for part in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def extract_template(protocol):
    section = protocol.split("# 16. REQUIRED OUTPUT SCHEMA", 1)[1].split("# 17.", 1)[0]
    return json.JSONDecoder().raw_decode(section[section.index("{"):])[0]


def build_schema(protocol):
    template = extract_template(protocol)
    rules_section = protocol.split("# 14. BORDERLINE RULE IDS", 1)[1].split("# 15.", 1)[0]
    rules = re.findall(r"(?m)^([A-Z][A-Z_]+)\s*$", rules_section)

    def convert(value, path=""):
        if isinstance(value, dict):
            props = {k: convert(v, f"{path}.{k}".strip(".")) for k, v in value.items()}
            return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}
        if isinstance(value, list):
            return {"type": "array", "items": convert(value[0], path + ".*")}
        node = {"type": "string"}
        if "|" in value:
            node["enum"] = value.split("|")
        if path.endswith(".rule_id"):
            node["enum"] = rules
        if path in ALLOWED_LABELS and tuple(node.get("enum", [])) != ALLOWED_LABELS[path]:
            raise ValueError(f"Protocol changed: review VOTABLE_FIELDS for {path}")
        return node

    schema = convert(template)
    for path in VOTABLE_FIELDS:
        current = schema
        for part in path.split("."):
            current = current["items"] if part == "*" else current["properties"][part]
        if tuple(current.get("enum", [])) != ALLOWED_LABELS[path]:
            raise ValueError(f"Protocol label mismatch: {path}")
    Draft202012Validator.check_schema(schema)
    return schema


def validate_audit(data, schema):
    errors = list(Draft202012Validator(schema).iter_errors(data))
    if errors:
        err = errors[0]
        path = ".".join(map(str, err.absolute_path))
        kind = "illegal_label" if err.validator == "enum" else "schema_invalid"
        raise AuditValidationError(f"{path}: {err.message}", kind)
    names = [system_key(s["system_name"]) for s in data["systems"]]
    if any(not name for name in names) or len(names) != len(set(names)):
        raise AuditValidationError("System names must be nonempty and unique")
    if not data["paper_title"].strip():
        raise AuditValidationError("paper_title must be nonempty")
    for system in data["systems"]:
        functions = system["functions"]
        for fn, item in functions.items():
            if item["label"] == "Present" and not item["evidence"].strip():
                raise AuditValidationError(f"{fn}: Present requires evidence")
        for fn, field in (("F", "mode"), ("E", "relational_adaptation")):
            item = functions[fn]
            if (item["label"] == "Present") == (item[field] == "NA"):
                raise AuditValidationError(f"{fn}.{field}: use NA exactly when function is not Present")
        for edge, item in system["dependencies"].items():
            explicit = item["presence"] == "Explicit"
            if explicit == (item["validation"] == "NA"):
                raise AuditValidationError(f"{edge}: validation must be NA exactly when not Explicit")
            if explicit and not item["evidence"].strip():
                raise AuditValidationError(f"{edge}: Explicit requires evidence")
            a, b = edge.split("_to_")
            if any(functions[x]["label"] == "Absent" for x in (a, b)) and item["presence"] != "Absent":
                raise AuditValidationError(f"{edge}: absent endpoint requires Absent dependency")
    return data
