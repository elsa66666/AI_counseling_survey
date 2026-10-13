# Eligibility evidence checklist (selection-v1.1)

This checklist documents the operational instructions used to resolve the retrospective eligibility review. It is not a transcript of the complete interactive review session and is not represented as an originally executed API prompt. The decision provenance is a single Codex AI review; exact model identity, a fixed API seed, and independent eligibility votes were not recorded. Future multi-agent eligibility runs must archive their actual prompts, model versions, parameters, input hashes and raw outputs.

For each frozen candidate:

1. Match the title and official identifier to its journal/proceedings record. Record formal-publication evidence separately from the method source. A preprint may supply readable method evidence after formal publication is independently verified.
2. Read the method, algorithm, prompts and relevant experiments. Identify the computational output and the role of the proposed or specifically adapted model. Do not infer a role from the paper title or from its saved SFPE positives.
3. COUNSELOR: the model generates, selects or adapts mental-health-support/counseling responses or interventions, including a component explicitly used to control those outputs. Explicit MI counseling is within scope. Generic empathy or general physical-activity advice without a counseling/support purpose is not sufficient.
4. CLIENT: a dedicated model or specifically adapted client setup generates utterances, behavior or internal state during interactive counseling. A client-policy contribution can appear in an evaluation paper. Unchanged reused simulators are auxiliary tools; whole-transcript generation and offline cloze reconstruction are corpus construction, not interactive clients.
5. BOTH: both qualifying contributions are implemented in the same paper. Count once in the unique total.
6. SUPPORT: relevant standalone resources, retrospective detectors/annotators, benchmarks without a qualifying model, or foundational background whose implemented purpose does not meet the core boundary. Resource papers with a trained counselor model must be assessed through that implementation.
7. OUTSIDE: no core or supporting relevance. UNRESOLVED: evidence is insufficient or genuinely ambiguous. Do not silently replace missing evidence with a confident exclusion.
8. Record an evidence paraphrase, section and PDF page (or HTML heading), source URL, source version, applicable boundary, date, reviewer method and actual votes if any. Distinguish paper-level inclusion from the canonical target of an existing SFPE audit.
9. Tag technology separately; do not silently introduce an LLM-only eligibility filter. Neither positive outcomes, human evaluation, nor a complete SFPE chain is required.
10. Inspect candidate identifiers, titles and contribution descriptions for duplicate versions. Summarize with the deterministic script; preserve the prior snapshot and the unchanged SFPE source.

Saved output fields are defined by the JSON ledger. Their aggregation is executable through `scripts/screening_ledger.py`; the webpage is generated through `scripts/build_selection_site.py`. `scripts/validate_selection.py` checks the completed frozen release. Evidence-based corrections create a new dated release rather than overwrite this one.
