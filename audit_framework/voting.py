from collections import Counter

from .config import AUDITOR_IDS
from .schema import ALLOWED_LABELS, EDGES, EVIDENCE_FIELDS, VOTABLE_FIELDS, get_path


def majority_vote(values, allowed_labels):
    """Exactly three slots; INVALID/missing votes never reduce the denominator."""
    if len(values) != 3:
        raise ValueError("Exactly three auditor slots are required")
    labels = dict(zip(AUDITOR_IDS, values))
    valid = {a: value for a, value in labels.items() if isinstance(value, str) and value in allowed_labels}
    counts = Counter(valid.values())
    winner, count = counts.most_common(1)[0] if counts else (None, 0)
    if count < 2:
        winner = None
    status = "unanimous" if count == 3 else "majority" if count == 2 else "no_majority"
    return {"label": winner, "votes": dict(sorted(counts.items())), "agent_labels": labels,
            "supporting_agents": [a for a in AUDITOR_IDS if winner is not None and valid.get(a) == winner],
            "invalid_agents": [a for a in AUDITOR_IDS if a not in valid],
            "agreement": round(count / 3, 4), "status": status,
            "needs_review": winner is None or winner in {"Unclear", "PossiblyTruncated"}}


def field_vote(records, path, allowed, adjudication=None):
    result = majority_vote([get_path(records.get(a), path) for a in AUDITOR_IDS], allowed)
    result["supporting_evidence"] = []
    if "." in path:
        parent_path = path.rsplit(".", 1)[0]
        for agent in result["supporting_agents"]:
            parent = get_path(records[agent], parent_path)
            evidence = {k: parent[k] for k in EVIDENCE_FIELDS if k in parent}
            result["supporting_evidence"].append({"auditor": agent, **evidence})
    if result["status"] == "no_majority" and adjudication:
        result["pre_adjudication"] = {key: result[key] for key in
                                      ("label", "status", "needs_review", "supporting_agents", "supporting_evidence")}
        result["label"] = adjudication["label"]
        result["status"] = "adjudicated"
        result["supporting_agents"] = [agent for agent, label in result["agent_labels"].items()
                                       if label == adjudication["label"]]
        result["supporting_evidence"] = adjudication["evidence"]
        result["needs_review"] = adjudication["label"] in {"Unclear", "PossiblyTruncated"}
        result["adjudication"] = adjudication
    return result


def consistency_issues(fields):
    issues = []
    label = lambda path: fields[path]["label"]
    for fn, detail in (("F", "mode"), ("E", "relational_adaptation")):
        present, extra = label(f"functions.{fn}.label"), label(f"functions.{fn}.{detail}")
        if present is not None and extra is not None and ((present == "Present") == (extra == "NA")):
            issues.append(f"functions.{fn}.{detail}: majority conflicts with function label")
    for edge in EDGES:
        presence, validation = label(f"dependencies.{edge}.presence"), label(f"dependencies.{edge}.validation")
        if presence is not None and validation is not None and ((presence == "Explicit") == (validation == "NA")):
            issues.append(f"{edge}: presence/validation majorities conflict")
        endpoints = [label(f"functions.{fn}.label") for fn in edge.split("_to_")]
        if "Absent" in endpoints and presence not in (None, "Absent"):
            issues.append(f"{edge}: dependency majority conflicts with absent endpoint")
    return issues


def build_consensus(paper_metadata, audits, adjudications=None, judge=None):
    adjudications = adjudications or {}
    audits = {a: audits.get(a) for a in AUDITOR_IDS}
    paper_field = field_vote(audits, "paper_input_completeness", ALLOWED_LABELS["paper_input_completeness"],
                             adjudications.get("paper_input_completeness"))
    if any(audit is not None and len(audit["systems"]) > 1 for audit in audits.values()):
        raise ValueError("Paper-folder consensus expects at most one system per auditor")
    records = {a: audit["systems"][0] if audit is not None and audit["systems"] else None
               for a, audit in audits.items()}
    inventories = {a: [s["system_name"] for s in audit["systems"]] if audit is not None else None
                   for a, audit in audits.items()}
    inventory_agreement = all(audits[a] is not None for a in AUDITOR_IDS) and len({bool(records[a]) for a in AUDITOR_IDS}) == 1
    systems = []
    if any(records.values()):
        fields = {}
        for template in VOTABLE_FIELDS:
            if template.startswith("systems.*."):
                path = template.removeprefix("systems.*.")
                fields[path] = field_vote(records, path, ALLOWED_LABELS[template], adjudications.get(template))
        issues = consistency_issues(fields)
        names = {a: record["system_name"] if record else None for a, record in records.items()}
        systems.append({"system_key": paper_metadata["paper_id"], "system_names": names, "fields": fields,
                        "alignment_status": "matched" if all(records.values()) else "needs_review",
                        "consistency_issues": issues,
                        "needs_review": bool(issues) or not all(records.values()) or any(f["needs_review"] for f in fields.values())})
    missing = [a for a in AUDITOR_IDS if audits[a] is None]
    needs_review = bool(missing) or not inventory_agreement or paper_field["needs_review"] or any(s["needs_review"] for s in systems)
    all_fields = [paper_field] + [f for s in systems for f in s["fields"].values()]
    full_agreement = inventory_agreement and all(f["status"] == "unanimous" for f in all_fields)
    return {"paper_id": paper_metadata["paper_id"], "metadata": paper_metadata,
            "paper_input_completeness": paper_field, "systems": systems,
            "system_inventories": inventories, "inventory_agreement": inventory_agreement,
            "failed_auditors": missing, "completed": not missing,
            "full_agreement": full_agreement, "needs_review": needs_review,
            "status": "needs_review" if needs_review else "unanimous" if full_agreement else "majority",
            "adjudication": judge or {"status": "not_needed", "disputed_fields": [], "resolved_fields": []}}
