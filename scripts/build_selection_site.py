"""Recompute eligibility accounting and package the frozen review for the static site.

No retrieval or model calls occur here. The 47 saved SFPE labels are left intact.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from collections import Counter
from screening_ledger import summarize
ROOT=Path(__file__).resolve().parents[1]
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--snapshot',default='2026-10-13-reviewed');args=parser.parse_args()
 folder=ROOT/'data/selection'/args.snapshot
 rows=json.loads((folder/'screening.json').read_text());summary=summarize(folder/'screening.json')
 write(folder/'screening_summary.json',summary)
 audits=json.loads((ROOT/'docs/data/audits.json').read_text());idx={p['paper_id']:p for p in audits['papers']}
 groups={}
 for name,subset in [('included',[r for r in rows if r['outcome']=='Included']),('included_unflagged',[r for r in rows if r['outcome']=='Included' and not idx[r['paper_id']]['needs_review']]),('counselor_role',[r for r in rows if r['role'] in ['COUNSELOR','BOTH']]),('supporting',[r for r in rows if r['role']=='SUPPORT']),('legacy_all',rows)]:
  ps=[idx[r['paper_id']] for r in subset]
  groups[name]={'n':len(ps),'nodes':{k:sum(p['sfpe'][k]=='Present' for p in ps) for k in 'SFPE'},'review_flags':sum(p['needs_review'] for p in ps),'explicit_edges':{e:sum(p['dependencies'][e]['presence']=='Explicit' for p in ps) for e in ps[0]['dependencies']},'validation_instances':dict(Counter(v['validation'] for p in ps for v in p['dependencies'].values() if v['presence']=='Explicit'))}
 write(folder/'sfpe_subsets.json',groups)
 for r in rows:r['legacy_audit']={k:idx[r['paper_id']][k] for k in ['sfpe','needs_review','system_names','dependencies','consistency_issues']}
 payload={'snapshot_id':args.snapshot,'summary':summary,'manifest':json.loads((folder/'manifest.json').read_text()),'sfpe_subsets':groups,'papers':rows,'reproduction':{'count_script':'scripts/screening_ledger.py','site_script':'scripts/build_selection_site.py','site_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'legacy_sfpe_sha256':hashlib.sha256((ROOT/'data/audit_results/all_consensus.jsonl').read_bytes()).hexdigest()}}
 data=ROOT/'docs/data';write(data/'selection.json',payload)
 (data/'selection.js').write_text('window.SFPE_SELECTION_DATA = '+json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')+';\n')
 (data/'selection.csv').write_bytes((folder/'screening.csv').read_bytes())
 print(json.dumps({'snapshot':args.snapshot,'outcomes':summary['record_outcomes'],'roles':summary['included_exclusive_roles'],'subsets':groups},indent=2))
if __name__=='__main__':main()
