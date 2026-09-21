# SFPE Multi-Agent Audit of LLM-Based Mental Health Counseling Systems

This repository contains a reproducible, evidence-grounded framework for auditing papers about LLM-based mental health counseling systems. Three heterogeneous language-model auditors independently read the same paper and apply a frozen coding protocol. The framework records evidence for four system functions (SFPE), seven directed dependencies, edge-specific validation levels, input completeness, confidence, and borderline cases. Python then computes a strict field-level two-of-three consensus without debate, cross-agent prompting, or a fourth judge model.

The repository also publishes the current 47-paper consensus dataset through a searchable [GitHub Pages audit explorer](docs/index.html). The web data is generated from the structured consensus records; the table does not contain a second hand-maintained copy of the judgments.

## Overview

The audit asks what a system **actually implements**, rather than what the authors present as motivation, clinical aspiration, terminology, or future work. Every positive code requires identifiable paper evidence. Architecture names and the co-occurrence of components are never sufficient on their own.

The four functions are:

- **S — State Sensing and Evidence Elicitation:** obtains or infers counseling-relevant client evidence.
- **F — Formulation and Belief Updating:** organizes client evidence into an explanatory account of difficulties or maintaining mechanisms.
- **P — Intervention Planning:** selects or adapts therapeutic actions using client-specific evidence available at decision time.
- **E — Enactment and Relational Adaptation:** realizes therapeutic intent in client-facing interaction and optionally adapts its delivery to the relationship.

The seven directed dependencies are `S→F`, `S→P`, `F→P`, `P→E`, `E→S`, `E→F`, and `E→P`. Every explicit dependency is assigned validation level `V0`, `V1`, or `V2`.

The frozen, executable specification is [prompts/sfpe_protocol.md](prompts/sfpe_protocol.md). The criteria below document that protocol in repository form; they do not replace or redefine it.

## Audit pipeline

```text
Paper metadata and verified full text
                 ↓
       One shared extracted text
                 ↓
    ┌────────────┼────────────┐
    ↓            ↓            ↓
 Auditor 1    Auditor 2    Auditor 3
    │            │            │
    └── independent schema-valid audits ──┘
                 ↓
       Field-level majority voting
                 ↓
 Cross-field consistency and review flags
                 ↓
      Final structured consensus record
                 ↓
   JSONL / JSON / CSV / GitHub Pages
```

### Paper extraction

Each paper is downloaded or loaded from a verified local source once. PDF or HTML text is cached and supplied unchanged to all three auditors. A source manifest records extraction warnings and a content fingerprint. Missing figures, inaccessible supplements, truncated text, scanned PDFs without OCR, or incomplete methods are handled through the protocol's completeness rules; an abstract is not silently substituted for unavailable full text.

### Independent auditing agents

Each auditor receives the same inputs:

1. the frozen SFPE protocol;
2. the same extracted paper text and source warnings;
3. the same strict JSON schema;
4. a short instruction to work independently and return one complete audit.

Each auditor must identify the eligible implemented system, assess paper and system completeness, code S/F/P/E, code all seven dependencies and applicable validation levels, and provide evidence, location, rationale, and confidence. An auditor never sees another auditor's answer. The default example configuration uses GPT-5.4-mini, Claude Sonnet 5, and DeepSeek V3.2; model IDs and endpoints remain explicit in [configs/auditors.example.json](configs/auditors.example.json).

Raw responses are saved before parsing. The parser removes only leading/trailing whitespace and a single outer Markdown JSON fence. It does not repair quotes, commas, keys, labels, truncated JSON, or schema violations. Rate limits and transient upstream failures use finite exponential backoff and respect `Retry-After` when present. A final auditor failure is recorded as unavailable and does not abort the paper or batch.

### Evidence extraction and classification

For each field, an auditor returns:

- the categorical label;
- a short supporting excerpt or faithful evidence statement;
- a page, section, figure, table, or appendix location when available;
- a one-sentence rationale connecting the evidence to the code;
- self-rated confidence (`High`, `Medium`, or `Low`).

Evidence, rationale, notes, and confidence are preserved as provenance but are not themselves voted.

### Disagreement, majority voting, and adjudication

Consensus is computed independently for every votable field. The denominator is always three auditors:

- `A / A / A` → unanimous `A`;
- `A / A / B` → majority `A`;
- `A / A / INVALID` → majority `A`;
- `A / B / C` → no majority;
- `A / B / INVALID` → no majority;
- `A / INVALID / INVALID` → no majority.

A winner requires at least two matching legal labels. Missing or invalid outputs do not reduce the denominator. No-majority fields receive `label: null`, `status: "no_majority"`, and `needs_review: true`. `Unclear` and `PossiblyTruncated` winners also require review. The system retains vote counts, all agent labels, supporting agents, invalid agents, agreement (`largest legal vote count / 3`), and the evidence supplied by auditors supporting the winner.

The current dataset contains one canonical audited system per paper folder. The three system descriptions in that folder are merged as the same system even when the auditors phrase its name differently; the original names remain in `system_names` for provenance. Cross-field consistency checks flag contradictions but never overwrite a majority label. Human adjudication can review flagged records outside this automatic vote; the published data preserves the unmodified automatic consensus.

## Coding criteria

### General decision rule

Use **Present** when identifiable implementation evidence satisfies the definition. Use **Absent** when the paper is sufficiently complete and no qualifying implementation is found. Use **Unclear** only when relevant functionality may exist but the available implementation evidence is genuinely missing, inaccessible, truncated, or ambiguous. A difficult but decidable case should receive Present or Absent with Low confidence rather than Unclear.

The annotation unit is an implemented counseling system. Annotate the full system rather than its ablations. Baselines are excluded unless explicitly requested. The current consensus implementation expects no more than one eligible system per auditor within a paper folder; see [docs/IMPLEMENTATION_NOTES.md](docs/IMPLEMENTATION_NOTES.md).

### S — State Sensing and Evidence Elicitation

**Definition.** The system acquires, identifies, infers, or updates counseling-relevant evidence about the current client.

**Positive criteria.** S is Present when the implemented system derives client-state information or actively elicits missing information and that representation can be used downstream. The evidence may be obtained from the current utterance, prior interaction, a structured assessment, or targeted questioning.

**Typical positive evidence.** Emotion, risk, need, concern, intention, belief, symptom, motivation, or relational-state inference; structured client-state tracking; active questioning to fill missing information; or an update to a client-state representation from new interaction evidence.

**Negative criteria and typical false positives.** A fixed persona, manually written profile, static demographics, raw conversation history, or retrieval of earlier dialogue is not S by itself. A component named “state tracker,” “memory agent,” or “cognitive agent” does not count unless its actual computation meets the definition.

**Boundary cases.** A prewritten profile becomes relevant to S only if the system derives or updates state from interaction. Classification counts as S when it infers a counseling-relevant state, but merely attaching an existing gold label does not. Active elicitation counts when the system asks questions to acquire missing client evidence.

**Examples.** “The client reports anxiety and insomnia” is client evidence and may support S if the system infers or structures it. Passing that sentence unchanged in a prompt is not sufficient. Inferring elevated suicide risk from the dialogue is S.

**Decision rule.** Ask: *Does the system derive or actively acquire information about the current client that can be used downstream?*

### F — Formulation and Belief Updating

**Definition.** The system organizes client evidence into an explanatory representation of the client's difficulties, mechanisms, causal relationships, maintaining processes, or psychologically meaningful hypotheses. F concerns why or how difficulties arise, persist, or relate to one another.

**Positive criteria.** F is Present only when client evidence is linked into an explanatory structure. The representation may be symbolic, textual, graphical, probabilistic, or latent if the paper shows that it encodes explanatory or maintaining relations.

**Typical positive evidence.** CBT case conceptualization; a client-specific causal graph; a maintaining-mechanism representation; an explanatory hypothesis linking experiences, beliefs, emotions, and behavior; or a structured psychological formulation used to explain the client's difficulties.

**Negative criteria and typical false positives.** Memory, conversation summaries, diagnoses, symptom lists, emotion labels, personality or preference profiles, retrieved facts, simulator hidden state, and descriptive client profiles are not F without explanatory relations. A model that detects *what* is happening has not necessarily represented *why* it happens.

**Boundary cases.** A diagnosis becomes F only if the system also represents client-specific explanatory mechanisms. A summary becomes F only when it constructs explanatory relationships. “Client experienced parental criticism” is evidence; “repeated criticism contributed to a belief of inadequacy that now drives avoidance” is formulation.

**Static versus Dynamic.** `Static` means an explanatory formulation exists but is not shown to change with new evidence. `Dynamic` means new client evidence can revise, replace, update, or refine it. `Unclear` means F exists but its update behavior cannot be determined. Multi-turn interaction alone never establishes Dynamic F. When F is not Present, `F_mode` is `NA`.

**Examples.** “The client has anxiety” is S or diagnosis, not F. “Avoidance reduces anxiety in the short term and thereby maintains the client's anxiety” is F.

**Decision rule.** Ask: *Does the system construct an explanatory account of why or how this client's difficulties arise, persist, or connect?*

### P — Intervention Planning

**Definition.** The system selects, organizes, prioritizes, sequences, or adapts interventions, strategies, goals, or actions based on client-specific evidence or representation available at decision time, such as current state, formulation, goals, or prior interaction, before the selected action is expressed to the client.

**Positive criteria.** There must be an identifiable decision about what therapeutic action to take, and the decision must be conditioned on the current client. A separate neural module is unnecessary; an explicit plan generated within a model call can count if the subsequent response is demonstrably conditioned on it.

**Typical positive evidence.** Intervention or therapeutic-strategy selection; counseling-move selection or prediction used to determine the next therapeutic response; treatment-goal selection; client-conditioned multi-step planning; explicit choice among CBT, supportive, or interviewing strategies; or a decision about what the counselor should do next.

**Negative criteria and typical false positives.** A fixed treatment sequence, static workflow, gold strategy annotation, retrospective response classification, direct response generation without a separable plan, generic reasoning text, hidden chain-of-thought, or “think step by step” prompting is not P.

**Boundary cases.** A predefined `Stage 1 → Stage 2 → Stage 3` sequence applied to every client is not P. A fixed CBT workflow that simply executes the next step is not P. Choosing or revising an intervention because of the current client's state, formulation, goals, or prior response is P. A predicted counseling-move label counts only when it determines the subsequent therapeutic action.

**Examples.** “Always proceed from exploration to comforting to action” is static structure, not P. “Because risk is high, select safety planning rather than cognitive restructuring” is P.

**Decision rule.** Ask: *Before client-facing enactment, does the system form an identifiable, client-conditioned representation of what therapeutic action should be taken?*

### E — Enactment and Relational Adaptation

**Definition.** The system realizes therapeutic intent through client-facing interaction and/or adjusts the manner of interaction to the evolving relational context.

**Positive criteria.** E is Present when the system produces therapeutic behavior addressed to the client. This includes generated responses and questions as well as other implemented client-facing interventions.

**Typical positive evidence.** Counseling response generation; therapeutic questioning; reflection; validation; reframing; interpretation; psychoeducation; or other client-facing intervention. Relational adaptation includes changing response style or delivery in response to resistance, alliance, rupture, trust, engagement, receptivity, or interpersonal reaction.

**Negative criteria and typical false positives.** Predicting a strategy label without realizing it, internal planning, therapist-behavior classification, or evaluator scoring is not E. Generic personalization is not automatically relational adaptation.

**Boundary cases.** `E_relational_adaptation = Yes` only when enactment is explicitly conditioned on a relationally relevant signal. Use `No` when E is Present but no relational adaptation mechanism is shown, `Unclear` when the evidence is insufficient, and `NA` when E is not Present.

**Examples.** Generating an empathic reflection is E. Selecting “reflection” without generating the response is P only. Changing the wording because the client is resisting may support relational adaptation; inserting the client's name does not.

**Decision rule.** Ask: *Does the system realize therapeutic intent for the client, and is its delivery explicitly adapted to the relationship when relational adaptation is claimed?*

### Operational boundary between P and E

P decides **what** therapeutic action to take; E realizes **how** that action appears in interaction. To code P, identify a strategy label, therapeutic goal, planned move, structured intervention plan, or other explicit intermediate decision that conditions enactment. If the system directly generates the client-facing response without such an identifiable decision, code E only. Internal or hidden reasoning is not sufficient evidence.

## Directed dependencies

A dependency `A→B` is coded only when information produced by A is used by B. Component co-occurrence is not a dependency.

- **Explicit:** architecture, algorithm, prompt construction, equation, information-flow diagram, module I/O, implementation detail, or ablation description directly shows that A conditions B. Literal causal wording is unnecessary. Mere availability somewhere in a global context is insufficient unless the method identifies it as downstream conditioning information.
- **Inferential:** the link appears plausible from the system description but direct evidence that A conditions B is missing. Inferential edges are retained for audit but are not counted as present in primary dependency statistics.
- **Absent:** either endpoint is absent, or both functions exist without evidence of directed information flow. Co-occurrence alone is Absent rather than Inferential.
- **Unclear:** relevant implementation information is missing, inaccessible, truncated, or genuinely ambiguous.

The coded edges are:

| Edge | Decision question | Explicit example |
|---|---|---|
| `S→F` | Does sensed evidence construct or update formulation? | Inferred beliefs are inserted into a case formulation. |
| `S→P` | Does sensed state influence intervention selection? | Detected risk changes the selected therapeutic action. |
| `F→P` | Does formulation guide intervention planning? | A maintaining mechanism determines the selected intervention. |
| `P→E` | Does the plan condition client-facing behavior? | A selected strategy is passed to response generation. |
| `E→S` | Does client reaction to enactment update sensed state? | The response to an intervention updates emotional or relational state. |
| `E→F` | Does client feedback revise formulation? | Observed contradiction modifies a causal client hypothesis. |
| `E→P` | Does client feedback alter later planning? | Resistance triggers selection of a different strategy. |

Ordinary multi-turn context is not automatic feedback. Appending the latest utterance to dialogue history does not establish `E→S`, `E→F`, or `E→P`; the paper must show an identifiable update to state, formulation, or planning.

## Dependency validation levels

Validation is coded separately for every **Explicit** edge. Inferential, Absent, and Unclear edges receive `NA`.

- **V0 — Not directly validated:** the edge is implemented or described, but no experiment isolates whether A affects B. An upstream-module ablation that reports only final response quality remains V0.
- **V1 — Transition validated:** an experiment changes, removes, degrades, or replaces A and directly measures or isolates its effect on downstream process B.
- **V2 — Trajectory/outcome validated:** the specific edge is linked to longitudinal behavior, adaptation, therapeutic trajectory, or counseling outcome.

Use the highest demonstrated level. End-output metrics support V1 or V2 only when the design isolates the coded dependency rather than the upstream component or full system as a whole.

## Borderline rules

| Rule | Required boundary |
|---|---|
| `PROFILE_NOT_SENSING` | Fixed personas and prewritten profiles are not S without derived or updated client state. |
| `MEMORY_NOT_FORMULATION` | Facts and memories are not F unless organized into explanatory relationships or hypotheses. |
| `DIAGNOSIS_NOT_FORMULATION` | A diagnostic label is not F without individual explanatory mechanisms. |
| `SUMMARY_NOT_FORMULATION` | A summary remains descriptive unless it constructs explanatory relations. |
| `STRATEGY_LABEL_NOT_AUTOMATICALLY_PLANNING` | A label counts as P only when the system selects it during inference. |
| `RESPONSE_GENERATION_NOT_PLANNING` | Direct response generation is E unless a separable therapeutic decision is identifiable. |
| `MULTITURN_NOT_FEEDBACK` | Multiple turns alone do not establish a feedback edge. |
| `ARCHITECTURE_NAME_NOT_EVIDENCE` | Names such as planner, reflection agent, or CBT agent do not determine codes. |
| `P_VS_E_INTERMEDIATE_PLAN` | P requires an identifiable intended action that conditions enactment. |
| `STATIC_VS_DYNAMIC_FORMULATION` | Dynamic F requires revision from new evidence, not merely multiple turns. |
| `RELATIONAL_ADAPTATION_BOUNDARY` | Relational adaptation requires conditioning on resistance, alliance, rupture, trust, engagement, receptivity, or interpersonal reaction. |
| `COMPONENT_COOCCURRENCE_NOT_DEPENDENCY` | Two present components do not establish directed information flow. |
| `ABSTRACT_METHOD_CONFLICT` | Prefer implemented method evidence over broad abstract claims and record the conflict. |
| `INPUT_TRUNCATION` | Missing relevant content affects completeness and may justify Unclear; do not infer absent functionality from unavailable material. |

## Input completeness, evidence, and confidence

Paper completeness is `Complete` or `PossiblyTruncated`. System completeness is `Complete`, `PossiblyTruncated`, or `NotApplicable`. A complete paper can still omit a particular implementation detail; completeness describes the audit input, while each field label describes the supported judgment.

Evidence must be attributable to the supplied paper and located when possible. Auditor confidence records certainty about applying the threshold; it is not a vote weight and never changes the two-of-three rule.

## Installation

Python 3.11 or later is recommended.

```bash
git clone <repository-url>
cd AI_counseling_survey
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Environment setup

Copy the example and fill it locally:

```bash
cp .env.example .env
```

The checked-in example contains names and placeholder formats only. Never commit `.env`. The example auditor configuration routes all three models through the configured gateway variables; direct-provider users may copy the config and map each auditor to separate environment-variable names.

## Run an audit

The CLI defaults to one paper to prevent accidental full-batch API use.

```bash
python scripts/run_audit.py --paper-id xiao-etal-2024-healme --output outputs --workers 3 --resume
```

To audit the first five records:

```bash
python scripts/run_audit.py --limit 5 --output outputs --workers 3 --resume
```

To audit the complete dataset, explicitly opt in:

```bash
python scripts/run_audit.py --all --output outputs --workers 3 --resume
```

To rebuild consensus from saved, validated auditor outputs without network calls:

```bash
python scripts/run_audit.py --rebuild-consensus --output outputs
```

Use `--papers`, `--prompt`, `--config`, `--env`, `--cache`, and `--sources` to override paths. A sources file maps paper IDs to verified PDFs, extracted text, or alternate URLs; see [examples/sources.example.json](examples/sources.example.json).

## Output schema

Each audit has `paper_title`, `paper_input_completeness`, and a `systems` array. Each system contains its name, completeness, annotation notes, four function objects, seven dependency objects, borderline cases, and overall notes. Function and dependency objects contain evidence, location, rationale, and confidence. The exact generated JSON Schema is checked in at [data/audit_results/audit.schema.json](data/audit_results/audit.schema.json).

The consensus record adds, for every votable field, `votes`, `agent_labels`, `supporting_agents`, `invalid_agents`, `agreement`, `label`, `status`, `needs_review`, and supporting evidence. The published files are:

- `data/audit_results/all_consensus.jsonl` — canonical consensus records;
- `data/audit_results/audits.json` — normalized public JSON with `title`, `paper_url`, and numeric `year`;
- `data/audit_results/audits.csv` — flat main-table export;
- `data/audit_results/audit_summary.json` — batch-level counts.

## Regenerate GitHub Pages

```bash
python scripts/build_site_data.py
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000`. The build validates paper counts, unique IDs, required SFPE/dependency fields, and all public paper URLs before writing the public JSON and CSV. GitHub Actions runs the same builder before deploying `docs/`; see [.github/workflows/pages.yml](.github/workflows/pages.yml).

## Repository structure

```text
.
├── README.md
├── requirements.txt
├── .env.example
├── audit_framework/          # extraction, agents, schema, voting, storage, statistics
├── prompts/
│   └── sfpe_protocol.md      # frozen executable audit specification
├── configs/
│   └── auditors.example.json
├── data/
│   ├── papers/papers.json    # 47 paper records with title, year, and paper_url
│   └── audit_results/        # consensus JSONL and generated public JSON/CSV
├── scripts/
│   ├── run_audit.py
│   ├── probe_models.py
│   └── build_site_data.py
├── docs/                     # dependency-free GitHub Pages application
├── examples/
│   └── sources.example.json
└── tests/
```

## Reproducibility notes

- The protocol, schema, paper input, model configuration, extracted text, and runtime settings are fingerprinted in each experiment directory.
- Resume reuses an audit only when its saved status, schema, and input/configuration signature match.
- Model outputs remain stochastic and provider behavior may change. Report model IDs, endpoints, dates, parameters, and failed auditor calls with any reproduction.
- The repository publishes consensus data and supporting evidence, not copyrighted paper PDFs or local full-text caches.
- Updating a prompt, model, schema, or decoding configuration defines a new experiment and should use a new output directory.
- The current public results are preserved as generated. Repository engineering and the site builder do not recalculate or reinterpret labels.

## Security

`.env`, output directories, downloaded full text, virtual environments, caches, and common key files are ignored. Before publication, run the documented secret scan in [docs/IMPLEMENTATION_NOTES.md](docs/IMPLEMENTATION_NOTES.md). The repository contains no real API keys, tokens, private endpoints, or personal filesystem paths.
