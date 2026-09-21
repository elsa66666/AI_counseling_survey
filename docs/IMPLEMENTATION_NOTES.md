# Implementation notes

This repository records the executable SFPE protocol, two-stage voting logic, and published consensus results. Site generation copies the structured consensus records without reinterpreting their judgments.

## Deliberate implementation constraints

1. The protocol can describe multiple eligible systems in a paper, but the current consensus implementation accepts at most one system per auditor in each paper folder. All 47 published papers satisfy this constraint. The three auditor names are retained for provenance and do not control matching; records in one paper folder are merged into one canonical system.
2. The majority denominator is fixed at three even when an auditor is unavailable. A GPT-5.5 second-stage judge is called only for `A/B/C`, `A/B/INVALID`, or `A/INVALID/INVALID`; it receives the saved first-stage opinions and evidence. It never substitutes for an unavailable auditor.
3. Schema validation verifies structure and allowed labels. It cannot verify that a quoted passage is faithful or that the scientific interpretation is correct; supporting evidence remains available for human review.
4. Public data contains consensus records and supporting evidence. Raw API envelopes, repeated failed attempts, downloaded papers, and full-text caches are excluded from the public repository.
5. The static site uses browser-native HTML, CSS, and JavaScript. It has no package manager or runtime dependency beyond a static web server.

## Publication checks

Run from the repository root:

```bash
python -m unittest discover -s tests -v
python scripts/build_site_data.py
python -m http.server 8000 --directory docs
```

Verify that the site reports 47 papers, every title opens an original paper URL, filters and sorting work, and Details exposes evidence and votes.

The following tracked-file scan is intentionally conservative. It checks common credential assignments and private key material without reading ignored `.env` files:

```bash
git grep -nEI '(api[_-]?key|token|secret|password)[[:space:]]*[:=][[:space:]]*[^[:space:]]+|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY' -- ':!*.example' ':!docs/IMPLEMENTATION_NOTES.md'
```

Also inspect tracked paths before pushing:

```bash
git status --short
git ls-files
```

This repository currently has no release license. The repository owner should choose and add one before granting reuse rights; making code publicly visible does not itself define a license.
