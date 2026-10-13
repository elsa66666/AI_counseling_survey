"""Validate released eligibility evidence, generated data and accounting consistency."""
import csv,hashlib,json
from pathlib import Path
from screening_ledger import summarize
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'data/selection/2026-10-13-reviewed'
rows=json.loads((folder/'screening.json').read_text());summary=summarize(folder/'screening.json');published=json.loads((folder/'screening_summary.json').read_text())
assert summary==published,'Saved summary differs from recomputation'
assert summary['record_outcomes']=={'Included':35,'Supporting':12,'Excluded':0,'Pending':0,'Duplicate':0}
assert summary['counselor_or_support_model_n']+summary['client_simulation_n']-summary['included_exclusive_roles']['BOTH']==35
assert all(r['screening_votes']==[] and r['screening_model_versions']==[] for r in rows),'Uncollected eligibility votes'
assert all(r['role_evidence'] and r['boundary_note'] and r['role_evidence_location'] for r in rows)
assert sum(r['review_source']['format']=='PDF' for r in rows)==46
for r in rows:
 src=r['review_source'];assert src['fulltext_url']==r['role_evidence_url']
 if src['format']=='PDF':
  assert len(src['source_sha256'])==64 and src['evidence_pdf_pages']
  assert all(1<=p<=src['page_count'] for p in src['evidence_pdf_pages'])
 else:assert src['source_sha256'] is None and src['hash_note']
payload=json.loads((ROOT/'docs/data/selection.json').read_text());assert payload['summary']==summary
assert [r['paper_id'] for r in rows]==[r['paper_id'] for r in payload['papers']]
assert payload['reproduction']['legacy_sfpe_sha256']==hashlib.sha256((ROOT/'data/audit_results/all_consensus.jsonl').read_bytes()).hexdigest()
with (folder/'screening.csv').open(newline='') as f:csv_rows=list(csv.DictReader(f))
assert len(csv_rows)==47 and {x['paper_id'] for x in csv_rows}=={x['paper_id'] for x in rows}
assert (ROOT/'docs/data/selection.csv').read_bytes()==(folder/'screening.csv').read_bytes()
assert (ROOT/'docs/data/selection.js').read_text().startswith('window.SFPE_SELECTION_DATA = ')
import re
for path in [ROOT/'docs/selection.html',ROOT/'docs/selection.js',ROOT/'docs/data/selection.json',ROOT/'docs/index.html',ROOT/'docs/app.js',ROOT/'docs/data/audits.json']:
 assert not re.search('[\u3400-\u9fff]',path.read_text()),f'Non-English display text in {path}'
print('PASS: English-only web content, 47 evidence-backed decisions, 35 core / 12 supporting, role overlap, 46 source hashes, CSV/JSON consistency and preserved SFPE provenance')
