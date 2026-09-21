import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audit_framework.config import ROOT, load_configs
from audit_framework.runner import rebuild_consensus, run_batch


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description="Three independent SFPE auditors; default run is ONE paper.")
    parser.add_argument("--papers", type=Path, default=ROOT / "data/papers/papers.json")
    parser.add_argument("--prompt", type=Path, default=ROOT / "prompts/sfpe_protocol.md")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/auditors.example.json")
    parser.add_argument("--env", type=Path, default=ROOT / ".env")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs")
    parser.add_argument("--cache", type=Path, default=ROOT / "data/fulltext")
    parser.add_argument("--sources", type=Path, help="Optional JSON mapping paper IDs to verified local full text/PDF or URLs")
    parser.add_argument("--paper-id")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--limit", type=positive)
    scope.add_argument("--all", action="store_true", help="Explicitly opt into the full dataset")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--resume", action="store_true", help="Default: reuse validated results")
    modes.add_argument("--overwrite", action="store_true", help="Rerun selected auditors, preserving attempt history")
    parser.add_argument("--workers", type=positive, default=1, help="Auditors in parallel within each paper (maximum 3)")
    parser.add_argument("--num-auditors", type=int, choices=[3], default=3)
    parser.add_argument("--rebuild-consensus", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.rebuild_consensus:
            result = rebuild_consensus(args.output, paper_id=args.paper_id, limit=args.limit)
        else:
            result = run_batch(papers_path=args.papers, prompt_path=args.prompt, output=args.output,
                               cache=args.cache, configs=load_configs(args.config, args.env),
                               limit=None if args.all else args.limit or 1, paper_id=args.paper_id,
                               overwrite=args.overwrite, workers=args.workers, sources_path=args.sources)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["failed_papers"] else 0
    except (ValueError, OSError, RuntimeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
