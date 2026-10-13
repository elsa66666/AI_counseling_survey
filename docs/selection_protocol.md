# Literature selection and update protocol (selection-v1.0)

Protocol frozen on 2026-10-13 for retrospective screening of the existing candidates and future updates. It does not imply that these rules, queries, or steps were used in the original GPT-assisted discovery.

## Eligibility rules

1. **Formal publication.** A journal article or paper in official conference/workshop proceedings, confirmed against the publisher/proceedings record. Online-first publication qualifies. An arXiv-only manuscript, repository, or acceptance announcement alone does not establish formal publication. Record the venue, date, DOI or official identifier, source URL, and supporting metadata. Unverified status stays pending.
2. **Modeled counseling role.** The work implements either (a) a counselor or mental-health-support process that generates, selects, or adapts supportive responses or interventions, including components explicitly used in that process; or (b) a simulated client/help seeker/standardized patient whose utterances, behavior, or internal state are generated for counseling interaction. A paper doing both is counted once, with role BOTH. An abstract label alone is insufficient: retain evidence from the method, algorithm, prompt, or experiment.
3. **Separate supporting literature.** Papers providing only a dataset, standalone detection/annotation method, or evaluation metric/benchmark are SUPPORT rather than core role-modeling papers. If a resource paper also implements an eligible counselor or simulator, assess that implementation rather than exclude the paper because it releases data.

Generic empathy without an explicit mental-health-support purpose does not automatically qualify. Offline symptom prediction without a link to counseling behavior is not counselor-process modeling. Human-in-the-loop support is eligible when the computational model directly produces or adapts support. No minimum number of turns, S/F/P/E positives, complete loop, positive outcome, or human-evaluation score is required.

Technology is tagged separately. Historical non-LLM work can provide context; it must not be interpreted as contemporary LLM coverage. Do not silently add an LLM-only filter to the author's two scope criteria.

## Discovery and screening stages

The following are registered query templates for future batches, not claims of an executed search. Each database run must retain its actual platform-specific syntax, fields, filters, cutoff, and export:

```text
Q1 = ("large language model" OR "language model" OR "conversational agent"
      OR chatbot OR "dialogue system")
     AND ("mental health" OR psychotherap* OR counsel* OR "emotional support"
          OR "motivational interviewing")

Q2 = ("client simulation" OR "patient simulation" OR "simulated client"
      OR "simulated patient" OR "standardized patient" OR "help seeker")
     AND ("mental health" OR psychotherap* OR counsel*
          OR "emotional support" OR "motivational interviewing")
```

For an official proceedings-list batch, archive the complete published list first and record the exact title/abstract query or screening method applied to that list. Preserve list-size and post-filter counts separately from the 47 seed papers. Do not report an unexecuted template's result as zero hits.

1. Freeze the existing GPT-assisted list as a seed input. Preserve its file hash. Original prompts, search results, and intermediate exclusions are not recoverable from a bibliography and must not be reconstructed as invented counts.
2. For a new retrieval run, register the exact source, query, searched fields, cutoff, filters, execution date, and export. Search NLP, clinical, and relevant HCI/AI sources; fixed database queries can be supplemented by official proceedings lists, reference chasing, and community nominations. A run is counted only after it actually occurs. Suggested concepts are language-model/conversational-agent terms combined with counseling, psychotherapy, mental-health-support, emotional-support, motivational-interviewing, or client-simulation terms. Do not require S/F/P/E terminology in the search query.
3. Deduplicate versions by DOI/official identifier and normalized title, inspect near matches, and map every duplicate to a canonical work. Title/URL equality is a candidate-pool check, not proof that all publication versions have been resolved.
4. Verify formal publication; record Published, NotPublished, or Pending with evidence.
5. Screen title/abstract conservatively, then consult the method/full text to assign COUNSELOR, CLIENT, BOTH, SUPPORT, OUTSIDE, or UNRESOLVED. Keep the decision method, evidence quotation/paraphrase, location, URL, and any agent votes/model versions. Missing text or an ambiguous role remains unresolved, not silently excluded.
6. Apply the existing three-agent SFPE annotation to the eligible audited configurations. Eligibility decisions are a separate stage; existing SFPE votes do not establish scope eligibility. A three-agent eligibility implementation would require new independent judgments and their provenance; this repository does not yet claim such a run.
7. Recompute outcome counts from the ledger, report pending cases, and release a versioned snapshot. The current 47-record SFPE export is a legacy mixed-candidate snapshot; it is not a completed core-eligibility cohort.

## Quantitative accounting

The script emits counts for Included, Supporting, Excluded, Pending, and Duplicate; their sum equals the frozen input size. Each excluded work has one primary exclusion reason for the flow diagram; additional reasons can remain in evidence notes. Report publication-stage pass/fail/pending counts separately. A BOTH paper contributes once to the core-paper total and to each applicable role count, so role columns must not be summed without subtracting BOTH.

Report actual per-stage input, retained, excluded, and pending counts; counts need not decrease at every stage. With no human gold set, eligibility agreement and disagreement are not accuracy, precision, or recall. Archived inputs, decisions, protocol/model versions, and aggregation code reproduce a snapshot's accounting; a later live API/search/LLM run need not return identical text or ranking.

## Community corrections and conference updates

Community members can nominate missing papers or suggest corrections through the public GitHub issue templates. A nomination requires an official publication URL and evidence of one modeled role. Treat it as a new candidate, not an automatic inclusion. Apply the same rules to community and database candidates.

After every relevant conference publishes its official proceedings/paper list, maintainers should perform an update batch: archive the list and date, add new candidates, merge duplicate versions, check publication and modeled role, run SFPE for eligible additions, and recompute counts. The list's release is the trigger; an acceptance list can be archived as discovery evidence but does not by itself satisfy formal publication. Journal papers and older missed work remain eligible through periodic queries and community nominations.

Each release should record the candidate/ledger hashes, protocol and code commit, model/prompt/input fingerprints for newly run annotations, exclusions and pending cases, changed decisions, and the reason for each change. Release tags such as `survey-YYYY-MM-DD` distinguish the frozen submission snapshot from later living updates. Preserve earlier releases; do not overwrite their results with the latest corpus.

During anonymous review, the anonymous mirror provides readable snapshots; it is not a GitHub issue interface. Community nominations use the public project repository when that channel is available. Do not expose its owner URL in an anonymous manuscript to create a feedback link.

## Recompute this snapshot

```sh
python scripts/screening_ledger.py summarize data/selection/2026-10-13/screening.json --output data/selection/2026-10-13/screening_summary.json
```

The published summary explicitly marks whether screening is complete. It cannot turn Pending into a completed eligibility decision.
