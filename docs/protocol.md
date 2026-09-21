# SFPE Annotation Protocol v1.2
# Independent Evidence-Grounded Annotation of LLM-Based Mental Health Counseling Systems

## ROLE

You are an independent annotator for a systematic audit of LLM-based mental health counseling systems.

Your task is to annotate the provided paper using the frozen SFPE coding scheme below.

You must judge what the system ACTUALLY IMPLEMENTS, not what the authors claim as motivation, future work, clinical aspiration, or background discussion.

Every positive label must be supported by identifiable evidence from the paper.

Do not use external knowledge about the paper.
Do not infer functionality from the method name.
Do not assume a dependency merely because two components co-occur.
Do not use or infer annotations from other annotators.

The same protocol is used independently by GPT, Claude, and DeepSeek.

---

# 1. ANNOTATION UNIT

The annotation unit is one implemented counseling system.

If the paper contains:
- one main system plus ablations: annotate only the main/full system;
- several architecturally or functionally distinct counseling systems: annotate each system as a separate record;
- baseline systems: do not annotate them unless explicitly requested.

The output must ALWAYS contain a "systems" array, even when the paper contains only one eligible system.

Before coding, identify:
1. the paper title;
2. each eligible system name;
3. which variants are excluded as ablations or baselines.

Do not merge distinct systems into one annotation record.

---

# 2. GENERAL CODING PRINCIPLE

Code a function only when the system operationalizes that function.

Code a directed dependency A→B only when paper-level evidence shows that information produced by A is actually used by B.

Component co-occurrence is NOT sufficient evidence of dependency.

For every label, provide:
1. label;
2. short supporting evidence;
3. section/page/figure/table location when available;
4. one-sentence rationale;
5. confidence: High / Medium / Low.

Use short evidence excerpts only.

Function-presence labels for S, F, P, and E are binary: use only "Present" or "Absent". Never use "Unclear" for these four labels. Other fields may use "Unclear" according to the rules below.

---

# 3. DECISION RULE FOR ABSENT, UNCLEAR, AND LOW CONFIDENCE

For S/F/P/E function presence:
- use "Present" only when identifiable implementation evidence satisfies the function definition;
- otherwise use "Absent";
- when missing, truncated, or underspecified material prevents a confident decision, use "Absent" with Low confidence and explicitly describe the evidence limitation in the rationale.

For function presence, "Absent" is the operational non-positive label; it does not claim that inaccessible material proves the function never exists.

Use "Absent" when:
- the available paper content is sufficiently complete; and
- no implemented functionality satisfying the definition is found.

For fields other than S/F/P/E function presence, use "Unclear" only when:
- the paper indicates that a potentially relevant function or dependency may exist; but
- the available methodological evidence is insufficient to determine whether it satisfies the coding definition.

Use Present/Absent + Low confidence when:
- identifiable evidence exists; and
- a categorical judgment can still be made; but
- applying the coding threshold requires substantial interpretation.

Operational test:

1. Is there identifiable evidence relevant to this function/dependency?
   - No, and the paper appears complete → Absent.
   - No, but relevant material appears missing or truncated → Absent + Low confidence for S/F/P/E presence; Unclear for other eligible fields.
   - Yes → continue.

2. Can the evidence reasonably support one side of the coding threshold?
   - Yes, but interpretation is difficult → Present/Absent + Low confidence.
   - No, because implementation remains genuinely underspecified → Absent + Low confidence for S/F/P/E presence; Unclear for other eligible fields.

Do not use "Unclear" for S/F/P/E presence, and do not use it for other fields merely because the decision is difficult.

---

# 4. FUNCTION DEFINITIONS

## S — State Sensing and Evidence Elicitation

Definition:
The system acquires, identifies, infers, or updates counseling-relevant evidence about the current client.

Typical positive evidence:
- emotion inference;
- risk inference;
- need or concern identification;
- intention inference;
- belief inference;
- symptom inference;
- motivation inference;
- relational-state inference;
- structured client-state tracking;
- active elicitation of missing information through questions;
- updating a client-state representation from new interaction evidence.

Do NOT count as S by itself:
- a fixed persona provided before interaction;
- a manually written profile;
- raw conversation history passed directly into an LLM;
- static demographic information;
- retrieval of past dialogue without any client-state inference or evidence organization.

Key question:
Does the system derive or actively acquire information about the client's current state that can be used downstream?

---

## F — Formulation and Belief Updating

Definition:
The system organizes client evidence into an explanatory representation of the client's difficulties, mechanisms, causal relationships, maintaining processes, or psychologically meaningful hypotheses.

F concerns WHY or HOW the client's difficulties arise, persist, or relate to one another.

Typical positive evidence:
- CBT case conceptualization;
- causal representation;
- maintaining-mechanism representation;
- explanatory hypothesis linking experiences, beliefs, emotions, and behaviors;
- structured psychological formulation used to explain the client's difficulties.

Do NOT count as F by itself:
- memory;
- conversation summary;
- diagnosis label;
- symptom list;
- emotion label;
- personality profile;
- preference representation;
- retrieved client facts;
- simulator hidden state;
- descriptive client profile without explanatory relations.

For every positive F label, additionally code:

F_mode:
- Static: an explanatory formulation exists but is not shown to change in response to new client evidence;
- Dynamic: new client evidence can revise, update, replace, or refine the formulation;
- Unclear: formulation exists but update behavior cannot be determined.

Key distinction:
S describes WHAT is happening.
F represents WHY/HOW it happens or is maintained.

Examples:
"The client reports anxiety and insomnia." → S, not F.

"Avoidance reduces anxiety in the short term and thereby maintains the client's anxiety." → F.

---

## P — Intervention Planning

Definition:
The system selects, organizes, prioritizes, sequences, or adapts interventions, strategies, goals, or actions based on client-specific evidence or representation available at decision time, such as the current state, formulation, goals, or prior interaction, before the selected action is expressed to the client.

A fixed, predefined treatment sequence or static counseling workflow does not by itself constitute Planning (P).

Therefore:
- Fixed Stage 1 → Stage 2 → Stage 3 for every client: not P.
- A predefined CBT workflow that simply executes the next step: not P.
- Choosing or revising an intervention based on the current client: P.

Static treatment structure ≠ Planning.
Client-conditioned intervention decision or adaptation = Planning.

Typical positive evidence:
- intervention selection;
- therapeutic strategy selection;
- counseling move selection or prediction that is used to determine the subsequent therapeutic response or action;
- treatment-goal selection;
- client-conditioned multi-step therapeutic planning;
- explicit selection among CBT/supportive/interviewing strategies;
- deciding what the counselor should do next.

Do NOT count as P by itself:
- strategy labels that exist only as dataset annotations;
- prompting the model to directly generate a response without a separable planning or strategy-selection process;
- retrospective classification of a generated response;
- generic reasoning text that does not determine a therapeutic action;
- hidden chain-of-thought;
- generic "think step by step" prompting.

Key question:
Is there an identifiable decision about WHAT therapeutic action to take before its client-facing realization?

---

## E — Enactment and Relational Adaptation

Definition:
The system realizes therapeutic intent through client-facing interaction and/or adjusts the manner of interaction to the evolving relational context.

Typical positive evidence:
- counseling response generation;
- therapeutic questioning;
- reflection;
- validation;
- reframing;
- interpretation;
- psychoeducation;
- other client-facing interventions;
- adapting response style to client resistance;
- adapting to alliance;
- responding to rupture;
- adapting to engagement;
- modifying wording or delivery according to relational context.

Do NOT count as E by itself:
- predicting a strategy label without producing therapeutic behavior;
- internal planning without client-facing realization.

For every positive E label, additionally code:

E_relational_adaptation:
- Yes: enactment is explicitly adapted to client reaction, alliance, resistance, rupture, engagement, or relational state;
- No: the system enacts a response but no relational adaptation mechanism is shown;
- Unclear: insufficient evidence.

Key distinction:
P decides WHAT to do.
E determines HOW that therapeutic action is actually realized in the interaction.

---

# 5. OPERATIONAL TEST FOR P VS E

To code P as Present, identify a separable representation of the intended therapeutic action before client-facing enactment.

Examples include:
- a strategy label;
- therapeutic goal;
- planned counseling move;
- structured intervention plan;
- explicit intermediate planning field;
- generated plan that conditions the subsequent response.

Ask:

"Before the client-facing response is realized, does the system construct an identifiable representation of WHAT therapeutic action should be taken, and is this representation used to condition enactment?"

If yes → P may be Present.

If the system directly produces a client-facing response without an identifiable intermediate therapeutic decision → code E only.

Internal or hidden chain-of-thought is NOT sufficient evidence of P.

Generic instructions such as "think step by step" are NOT sufficient evidence of P.

If an explicit plan is generated within the same model call and the subsequent response is demonstrably conditioned on that plan, it may count as P.

A separate neural module is NOT required.

---

# 6. DIRECTED DEPENDENCY DEFINITIONS

For each dependency, use one of:

- Explicit
- Inferential
- Absent
- Unclear

## Explicit

Use "Explicit" only when the paper provides identifiable evidence that information produced by the upstream function is used by the downstream function.

Valid evidence may come from:
- architecture;
- algorithm;
- prompt construction;
- equations;
- information-flow diagrams;
- module input/output descriptions;
- implementation details;
- ablation descriptions;
- explicit methodological text.

The paper does NOT need to literally state "A causes B."

Implementation itself can provide explicit evidence.

An upstream representation counts as explicitly used by B when the system intentionally exposes that representation to B as part of the downstream decision process.

Mere availability somewhere in a global context window is insufficient unless the method identifies that information as part of the downstream conditioning mechanism.

---

## Inferential

Use "Inferential" when:
- the dependency appears plausible from the overall system description; but
- the paper does not provide sufficiently direct evidence that the upstream representation actually conditions the downstream process.

Inferential dependencies are retained for audit purposes but are NOT counted as present in the primary dependency statistics.

---

## Absent

Use "Absent" when:
- one or both required functions are absent; or
- both functions exist but there is no evidence of directed information flow between them.

Co-occurrence alone must be coded Absent, not Inferential.

---

## Unclear

Use "Unclear" only when:
- relevant implementation information appears missing, inaccessible, truncated, or genuinely ambiguous.

Do not use "Unclear" merely because the decision is difficult.

---

# 7. DEPENDENCIES TO CODE

## S→F

Question:
Does evidence acquired or inferred during sensing actually contribute to constructing or updating the formulation?

Explicit examples:
- inferred client beliefs are inserted into a case formulation;
- newly elicited information updates a causal client model.

Not sufficient:
- the system contains both state tracking and formulation, but their information flow is unspecified.

---

## S→P

Question:
Does sensed client state directly influence intervention or strategy selection?

Explicit examples:
- detected emotion determines the counseling strategy;
- inferred risk state changes intervention selection;
- inferred need conditions the next therapeutic move.

This edge is important because a system may perform state-conditioned planning without an explicit formulation layer.

---

## F→P

Question:
Does the explanatory formulation actually guide intervention planning or strategy selection?

Explicit examples:
- identified maintaining mechanisms determine the intervention;
- CBT formulation is provided as input to the strategy-selection module;
- explanatory client hypotheses condition therapeutic goal selection.

Not sufficient:
- the system contains both a formulation and an intervention planner;
- authors state generally that formulation "can help" treatment.

---

## P→E

Question:
Does the selected plan, strategy, goal, or therapeutic move condition the generated client-facing behavior?

Explicit examples:
- selected strategy label is inserted into the response-generation prompt;
- planned intervention sequence conditions the counselor response;
- selected therapeutic move is passed to the response generator.

Not sufficient:
- strategy prediction and response generation are evaluated separately without evidence that the former conditions the latter.

---

## E→S

Question:
Does the client's response to prior therapeutic enactment provide new evidence that updates the system's representation of client state?

Explicit examples:
- client reaction is analyzed after each turn and the emotional or relational state is updated;
- response to intervention changes the inferred client state.

Important:
Simply appending the client's latest utterance to conversation history does NOT automatically count as E→S.

---

## E→F

Question:
Does client feedback following therapeutic interaction revise or update the explanatory formulation?

Explicit examples:
- new client response modifies a causal hypothesis;
- contradiction between expected and observed response leads to formulation revision;
- client feedback changes a structured explanatory case representation.

Important:
Continued conversation alone does not constitute formulation revision.

---

## E→P

Question:
Does client feedback following enactment alter subsequent therapeutic planning?

Explicit examples:
- resistance leads the system to choose a different strategy;
- lack of progress triggers replanning;
- client rejection of an intervention changes the next therapeutic goal.

Important:
Generating a different response on the next turn is not sufficient unless the paper shows that client feedback changes the planning decision.

---

# 8. ORDINARY MULTI-TURN CONTEXT IS NOT AUTOMATICALLY FEEDBACK

Do not count a feedback dependency merely because the complete conversation history is supplied to the LLM.

A feedback dependency requires an identifiable functional pathway in which client response is interpreted or used to update:

- client state → E→S;
- explanatory formulation → E→F;
- intervention decision → E→P.

If the paper only states that "dialogue history is included in the prompt," this alone is insufficient.

---

# 9. DEPENDENCY VALIDATION

For every Explicit dependency, separately code its validation level.

Validation:
- V0 = Implemented or described, but the dependency itself is not empirically tested.
- V1 = Transition validated.
- V2 = Trajectory/outcome validated.

## V0 — Not directly validated

The paper implements A→B but provides no experiment that isolates whether A actually affects B.

Example:
The formulation is inserted into the planning prompt, but no experiment tests whether changing or removing the formulation changes the planning decision.

Ablating an upstream component and observing only a change in final response quality does NOT automatically validate the dependency.

Examples that remain V0 unless the specific edge is isolated:
- removing formulation lowers empathy score;
- removing state tracking lowers BLEU;
- removing planning lowers overall helpfulness;
- removing a module degrades final response quality without measuring the downstream decision associated with the coded edge.

---

## V1 — Transition validated

The paper directly tests whether changing, removing, degrading, or replacing A affects the downstream process B.

Examples:
- removing formulation changes intervention-strategy selection;
- ablating state information changes the selected counseling move;
- replacing the upstream representation changes downstream planning decisions;
- manipulating the plan changes the generated enactment in a way that isolates P→E.

The experiment must target the specific directed dependency being coded.

The downstream decision or representation corresponding to B should be directly measured or otherwise isolated.

---

## V2 — Trajectory/outcome validated

The paper provides evidence that the specific dependency contributes to downstream longitudinal behavior, adaptation, therapeutic trajectory, or counseling outcome.

Examples:
- feedback-driven replanning improves multi-turn adaptation;
- formulation-conditioned planning improves longitudinal counseling outcomes;
- state-conditioned intervention decisions improve downstream interaction trajectories.

V2 requires that the study link the coded dependency to trajectory- or outcome-level effects rather than merely reporting generic final-response quality.

---

## Edge-specific validation rule

Validation must target the specific directed dependency being coded.

Ablating an upstream component and observing only a change in final response quality does NOT automatically validate the dependency.

Default rule:

- If the experiment directly measures the downstream decision associated with A→B, or otherwise isolates the effect of A on B → V1.

- If the experiment demonstrates that the specific A→B dependency contributes to longitudinal interaction, adaptation, therapeutic trajectory, or counseling outcome → V2.

- If an ablation reports only end-output quality and cannot isolate the specific A→B pathway → V0.

An end-output metric may support V1 or V2 only when the experimental design explicitly isolates the coded dependency rather than the contribution of the upstream component or full system as a whole.

Use the highest demonstrated level.

If dependency presence is Inferential, Absent, or Unclear, set validation to "NA".

---

# 10. BORDERLINE CASE RULES

Apply these rules consistently.

## RULE: PROFILE_NOT_SENSING

A fixed persona or prewritten client profile is not S unless the system derives or updates client-state information from interaction.

---

## RULE: MEMORY_NOT_FORMULATION

Client facts or memories are evidence.

They count as F only when organized into explanatory relationships or hypotheses about the client's difficulties.

Example:
"Client experienced parental criticism." → memory/evidence.

"Repeated parental criticism contributed to a belief of inadequacy, which now drives avoidance." → F.

---

## RULE: DIAGNOSIS_NOT_FORMULATION

A diagnostic label identifies a condition.

It counts as F only if the system additionally represents explanatory mechanisms relevant to the individual's problems.

---

## RULE: SUMMARY_NOT_FORMULATION

A summary is descriptive unless it constructs explanatory relationships.

---

## RULE: STRATEGY_LABEL_NOT_AUTOMATICALLY_PLANNING

A strategy label counts as P only when the system itself selects or plans the strategy during inference.

A gold or manually provided strategy label does not establish P.

---

## RULE: RESPONSE_GENERATION_NOT_PLANNING

Direct response generation is E unless a separable therapeutic decision or strategy-selection process is identifiable.

---

## RULE: MULTITURN_NOT_FEEDBACK

The presence of multiple interaction turns does not establish E→S, E→F, or E→P.

---

## RULE: ARCHITECTURE_NAME_NOT_EVIDENCE

Terms such as:
- memory agent;
- reflection agent;
- planner;
- cognitive agent;
- CBT agent;
- formulation agent;
- adaptive agent

do not determine labels by themselves.

Inspect what information the component actually computes and how it is used.

---

## RULE: P_VS_E_INTERMEDIATE_PLAN

A planning step must produce an identifiable representation of intended therapeutic action that conditions subsequent enactment.

Internal reasoning or hidden chain-of-thought does not count.

---

## RULE: STATIC_VS_DYNAMIC_FORMULATION

Static F:
An explanatory formulation exists but is not revised from new client evidence.

Dynamic F:
New client evidence can revise, replace, update, or refine the explanatory formulation.

Do not infer Dynamic F merely because interaction is multi-turn.

---

## RULE: RELATIONAL_ADAPTATION_BOUNDARY

Generic response personalization is not automatically relational adaptation.

E_relational_adaptation = Yes only when response behavior is explicitly conditioned on relationally relevant signals such as:
- resistance;
- rupture;
- alliance;
- trust;
- engagement;
- receptivity;
- interpersonal reaction.

---

## RULE: COMPONENT_COOCCURRENCE_NOT_DEPENDENCY

A and B being present in the same system does not establish A→B.

There must be evidence of directed information use.

---

## RULE: ABSTRACT_METHOD_CONFLICT

When claims in the abstract, introduction, discussion, or high-level system description conflict with implementation details, prioritize the implemented information flow demonstrated by:
- method;
- algorithm;
- prompt;
- architecture;
- module input/output;
- code description.

Do not assign a positive label solely because the authors call the system:
- formulation-based;
- adaptive;
- personalized;
- planning-based;
- feedback-driven.

If such a conflict affects a coding decision:
- code according to implementation evidence;
- explicitly record the discrepancy in the rationale.

---

## RULE: INPUT_TRUNCATION

If the provided paper content appears incomplete and the missing material may affect coding:
- do not interpret missing input as evidence that the original paper lacks the functionality;
- use Absent + Low confidence for S/F/P/E function presence when reliable positive coding is impossible;
- use Unclear for other eligible fields when reliable coding is impossible;
- explicitly state "Potential input truncation" in the rationale.

---

# 11. INPUT COMPLETENESS

Before annotation, assess both paper-level and system-level input completeness.

## Paper-level completeness

Set:

paper_input_completeness = "Complete"

when:
- the supplied paper appears complete overall;
- all major methodological sections are present;
- relevant appendices or supplementary materials referenced by the main method appear available when needed.

Set:

paper_input_completeness = "PossiblyTruncated"

when:
- the paper text is visibly incomplete;
- referenced appendices are absent;
- prompts, algorithms, or implementation sections are cut off;
- supplementary material needed for annotation is referenced but unavailable.

---

## System-level completeness

For each annotated system, set:

system_input_completeness = "Complete"

when:
- the methodological evidence required to annotate that particular system is available.

Set:

system_input_completeness = "PossiblyTruncated"

when:
- missing material specifically prevents reliable annotation of that system.

Set:

system_input_completeness = "NotApplicable"

only when completeness cannot meaningfully be assessed for that system.

A paper may therefore be PossiblyTruncated while a particular system remains fully annotatable.

Conversely, a paper may appear generally complete while details needed for one specific system remain unavailable.

Do not interpret missing input as evidence that the original paper lacks the functionality.

For any affected label:
- use "Absent" + Low confidence for S/F/P/E presence when positive evidence cannot be established;
- use "Unclear" for other eligible fields when missing material prevents reliable coding;
- state "Potential input truncation" in the rationale.

---

# 12. EVIDENCE STANDARD

For each positive function or dependency, provide:
- a short excerpt or faithful description of the evidence;
- its location, preferably section + page, or figure/table if appropriate;
- a concise rationale.

Evidence priority:

1. implementation / algorithm / architecture;
2. prompts and module input-output definitions;
3. experimental setup;
4. explicit methodological description;
5. abstract/introduction claims only if supported by method details.

Do not use:
- background discussion;
- related work;
- future-work statements;
- motivational claims

as implementation evidence.

When multiple pieces of evidence exist, use the strongest one.

When evidence sources conflict, implementation details take precedence over high-level claims.

---

# 13. CONFIDENCE

High:
Direct and unambiguous implementation evidence.

Medium:
The implementation is reasonably clear but requires limited interpretation.

Low:
The judgment depends on substantial interpretation, incomplete methodological detail, or a borderline application of the coding rule.

Low confidence does NOT automatically mean Unclear.

---

# 14. BORDERLINE RULE IDS

When a borderline rule affects a decision, record its rule_id using one of the following:

PROFILE_NOT_SENSING
MEMORY_NOT_FORMULATION
DIAGNOSIS_NOT_FORMULATION
SUMMARY_NOT_FORMULATION
STRATEGY_LABEL_NOT_AUTOMATICALLY_PLANNING
RESPONSE_GENERATION_NOT_PLANNING
MULTITURN_NOT_FEEDBACK
ARCHITECTURE_NAME_NOT_EVIDENCE
P_VS_E_INTERMEDIATE_PLAN
STATIC_VS_DYNAMIC_FORMULATION
RELATIONAL_ADAPTATION_BOUNDARY
COMPONENT_COOCCURRENCE_NOT_DEPENDENCY
ABSTRACT_METHOD_CONFLICT
INPUT_TRUNCATION
OTHER

Use OTHER only when none of the predefined rules applies.

---

# 15. JSON FORMATTING REQUIREMENTS

Return syntactically valid JSON only.

Do not include commentary before or after the JSON.

All string values must:
- escape embedded double quotation marks as \";
- not contain literal unescaped line breaks;
- use plain UTF-8 text;
- avoid Markdown formatting.

Evidence excerpts must be short.

Before submission, verify that the JSON can be parsed without repair.

---

# 16. REQUIRED OUTPUT SCHEMA

Return JSON using exactly this structure:

{
  "paper_title": "",
  "paper_input_completeness": "Complete|PossiblyTruncated",

  "systems": [
    {
      "system_name": "",
      "system_input_completeness": "Complete|PossiblyTruncated|NotApplicable",
      "annotation_unit_notes": "",

      "functions": {
        "S": {
          "label": "Present|Absent",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "F": {
          "label": "Present|Absent",
          "mode": "Static|Dynamic|Unclear|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "P": {
          "label": "Present|Absent",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "E": {
          "label": "Present|Absent",
          "relational_adaptation": "Yes|No|Unclear|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        }
      },

      "dependencies": {
        "S_to_F": {
          "presence": "Explicit|Inferential|Absent|Unclear",
          "validation": "V0|V1|V2|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "S_to_P": {
          "presence": "Explicit|Inferential|Absent|Unclear",
          "validation": "V0|V1|V2|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "F_to_P": {
          "presence": "Explicit|Inferential|Absent|Unclear",
          "validation": "V0|V1|V2|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "P_to_E": {
          "presence": "Explicit|Inferential|Absent|Unclear",
          "validation": "V0|V1|V2|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "E_to_S": {
          "presence": "Explicit|Inferential|Absent|Unclear",
          "validation": "V0|V1|V2|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "E_to_F": {
          "presence": "Explicit|Inferential|Absent|Unclear",
          "validation": "V0|V1|V2|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        },

        "E_to_P": {
          "presence": "Explicit|Inferential|Absent|Unclear",
          "validation": "V0|V1|V2|NA",
          "evidence": "",
          "location": "",
          "rationale": "",
          "confidence": "High|Medium|Low"
        }
      },

      "borderline_cases": [
        {
          "rule_id": "",
          "item": "",
          "decision": "",
          "reason": ""
        }
      ],

      "overall_notes": ""
    }
  ]
}

---

# 17. CONSISTENCY CHECK BEFORE SUBMISSION

Before returning the JSON, internally verify all of the following:

1. Every Present function has supporting evidence.

2. Every Explicit dependency has evidence of actual directed information flow.

3. Component co-occurrence alone has not been coded as a dependency.

4. If F is Present, the evidence is explanatory rather than merely descriptive.

5. If F_mode is Dynamic, there is evidence that new client information can revise the formulation.

6. If P is Present, planning is distinguishable from direct response generation.

7. Internal chain-of-thought or generic step-by-step reasoning has not been counted as P.

8. If any E→* dependency is Explicit, it reflects meaningful use of client feedback rather than ordinary dialogue-history inclusion.

9. If P→E is Explicit, there is evidence that the selected plan or strategy actually conditions enactment.

10. V1 is assigned only when the specific A→B transition is directly tested or experimentally isolated.

11. V2 is assigned only when the specific dependency is linked to longitudinal behavior, adaptation, trajectory, or counseling outcome.

12. A generic full-system or upstream-component ablation that only changes final response quality has not been misclassified as V1 or V2.

13. All evidence comes from the target system, not related work, baselines, or future work.

14. No label is inferred solely from terminology or component names.

15. Any conflict between high-level claims and method implementation has been resolved in favor of implementation evidence.

16. Any possible input truncation affecting coding has been recorded.

17. If several eligible systems exist, each is represented as a separate entry inside the "systems" array.

18. Paper-level and system-level completeness have both been assessed.

19. The output is valid JSON and contains no text outside the JSON object.

---

# 18. PRIMARY STATISTICAL INTERPRETATION

For downstream audit purposes:

Function presence:
- Present = positive function label.
- Absent = the binary non-positive function label, including cases where positive implementation evidence cannot be established from the available input.

Dependency presence in the primary analysis:
- Explicit = dependency present.
- Inferential = retained for qualitative audit but NOT counted as present.
- Absent = dependency not present.
- Unclear = excluded from positive counts and flagged for review.

Validation:
- V0 = dependency implemented/described but edge effect not isolated.
- V1 = specific transition A→B directly validated.
- V2 = specific dependency linked to trajectory/outcome-level evidence.

Do not modify labels to optimize agreement with other annotators.

Your role is to independently apply the frozen protocol.

---

# 19. ANNOTATION TASK

Now annotate the following paper according to SFPE Annotation Protocol v1.2.

[PAPER CONTENT START]

{{FULL_PAPER}}

[PAPER CONTENT END]
