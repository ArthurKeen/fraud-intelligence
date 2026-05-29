#!/usr/bin/env python3
"""
One-command demo database setup.

Runs all three phases in sequence against the REMOTE ArangoDB instance:
  Phase 1: generate data, ingest, define graphs, install themes + saved queries
  Phase 2: entity resolution (GoldenRecords, resolvedTo edges)
  Phase 3: analytics + risk scoring

Usage:
    python scripts/setup_demo.py                  # full setup
    python scripts/setup_demo.py --from-phase 2   # resume from Phase 2 (skip data gen/ingest)
    python scripts/setup_demo.py --skip-phase3     # skip analytics/risk (faster)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import get_arango_config, load_dotenv, sanitize_url  # noqa: E402


def run_step(label: str, cmd: list[str]) -> bool:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}\n")
    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(ROOT))
    elapsed = time.time() - t0
    ok = result.returncode == 0
    status = "OK" if ok else "FAILED"
    print(f"\n  [{status}] {label}  ({elapsed:.1f}s)")
    return ok


def main() -> None:
    load_dotenv()

    p = argparse.ArgumentParser(description="Set up a complete demo database (Phases 1-3).")
    p.add_argument("--from-phase", type=int, choices=[1, 2, 3], default=1,
                    help="Start from this phase (default: 1). Use 2 or 3 to skip earlier phases.")
    p.add_argument("--skip-phase3", action="store_true",
                    help="Skip Phase 3 (analytics + risk scoring) for a faster setup.")
    p.add_argument("--data-dir", default="data/sample", help="Dataset directory (Phase 1)")
    args = p.parse_args()

    cfg = get_arango_config(forced_mode="REMOTE")
    print(f"Target: {sanitize_url(cfg.url)}  db={cfg.database}\n")

    py = sys.executable
    results: list[tuple[str, bool]] = []

    if args.from_phase <= 1:
        ok = run_step(
            "Phase 1: Generate + Ingest + Graphs + Visualizer",
            [py, "scripts/test_phase1.py", "--remote-only", "--install-visualizer",
             "--data-dir", args.data_dir],
        )
        results.append(("Phase 1", ok))
        if not ok:
            print("\nPhase 1 failed — aborting.")
            sys.exit(1)

    if args.from_phase <= 2:
        ok = run_step(
            "Phase 2: Entity Resolution",
            [py, "scripts/test_phase2.py", "--remote-only"],
        )
        results.append(("Phase 2", ok))
        if not ok:
            print("\nPhase 2 failed — aborting.")
            sys.exit(1)

    if args.from_phase <= 3 and not args.skip_phase3:
        ok = run_step(
            "Phase 3: Analytics + Risk Scoring",
            [py, "scripts/test_phase3.py", "--remote-only"],
        )
        results.append(("Phase 3", ok))
        if not ok:
            print("\nPhase 3 failed — aborting.")
            sys.exit(1)

    print(f"\n{'='*60}")
    print("  Demo Setup Summary")
    print(f"{'='*60}")
    for label, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    print(f"\nDatabase: {sanitize_url(cfg.url)} / {cfg.database}")
    print("Done.\n")


if __name__ == "__main__":
    main()
