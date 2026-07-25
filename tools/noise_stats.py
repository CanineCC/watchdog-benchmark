#!/usr/bin/env python3
"""noise_stats.py — recompute a Watchdog noise measurement from a verdicts file.

Open, dependency-light (Python 3 stdlib only). Given a file of per-finding verdicts, it recomputes the pooled
five-class noise rate, the PRIMARY interval (a cluster-aware bootstrap that resamples by repository), the Wilson
score interval as a secondary/sanity figure, and the minimum-exposure gate checks — exactly the arithmetic behind
any published number (see ../METHOD.md). Run it on our published verdicts, or on your own tool's, and compare.

    python3 noise_stats.py verdicts.csv
    python3 noise_stats.py verdicts.csv --by-language --threshold 10

Input: CSV (or JSONL) with one row per audited finding. Required columns:
    repo      the repository the finding is in  (the bootstrap cluster)
    class     one of: valid | false-positive | opinion-not-fact | redundant | shape-irrelevant
Optional columns: id, dimension, language, evidence_defect.  See verdicts.schema.json.

"noise" = the four non-valid classes. Unknown class values are reported and excluded (never silently counted).
"""
import argparse
import csv
import json
import math
import random
import sys
from collections import defaultdict

VALID = "valid"
NOISE_CLASSES = {"false-positive", "opinion-not-fact", "redundant", "shape-irrelevant"}
KNOWN = {VALID} | NOISE_CLASSES
BOOTSTRAP_RESAMPLES = 10000
SEED = 20260725  # fixed so the interval is itself reproducible


def load(path):
    rows = []
    if path.endswith(".jsonl"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    else:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    out, unknown = [], 0
    for r in rows:
        cls = (r.get("class") or "").strip()
        repo = (r.get("repo") or "").strip()
        if cls not in KNOWN:
            unknown += 1
            continue
        out.append({"repo": repo or "(unspecified)", "class": cls,
                    "language": (r.get("language") or "").strip()})
    return out, unknown


def noise_rate(rows):
    if not rows:
        return 0.0, 0, 0
    n = len(rows)
    noise = sum(1 for r in rows if r["class"] in NOISE_CLASSES)
    return noise / n, noise, n


def wilson(noise, n, z=1.96):
    """Wilson score interval (secondary/sanity figure)."""
    if n == 0:
        return (0.0, 0.0)
    p = noise / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def cluster_bootstrap(rows, resamples=BOOTSTRAP_RESAMPLES, seed=SEED):
    """PRIMARY interval: resample REPOSITORIES with replacement, recompute the pooled rate each time.
    Prices in the correlation of findings within a repo (one detector defect -> many correlated FPs)."""
    by_repo = defaultdict(list)
    for r in rows:
        by_repo[r["repo"]].append(r)
    repos = list(by_repo.values())
    if len(repos) < 2:
        return (float("nan"), float("nan"))  # a bootstrap over <2 clusters is not meaningful
    rng = random.Random(seed)
    estimates = []
    k = len(repos)
    for _ in range(resamples):
        sample = []
        for _ in range(k):
            sample.extend(repos[rng.randrange(k)])
        rate, _, _ = noise_rate(sample)
        estimates.append(rate)
    estimates.sort()
    lo = estimates[int(0.025 * len(estimates))]
    hi = estimates[min(len(estimates) - 1, int(0.975 * len(estimates)))]
    return (lo, hi)


def repo_domination(rows):
    by_repo = defaultdict(int)
    for r in rows:
        by_repo[r["repo"]] += 1
    if not by_repo:
        return 0.0, None
    top_repo, top_n = max(by_repo.items(), key=lambda kv: kv[1])
    return top_n / len(rows), top_repo


def report(label, rows, threshold_pct):
    rate, noise, n = noise_rate(rows)
    repos = {r["repo"] for r in rows}
    boot = cluster_bootstrap(rows)
    wil = wilson(noise, n)
    dom_frac, dom_repo = repo_domination(rows)

    print(f"\n=== {label} ===")
    print(f"  audited findings : {n}   ({noise} noise, {n - noise} valid)")
    print(f"  repositories     : {len(repos)}")
    print(f"  noise (pooled)   : {rate * 100:.2f}%")
    if not math.isnan(boot[0]):
        print(f"  95% CI (cluster bootstrap, PRIMARY) : [{boot[0]*100:.2f}%, {boot[1]*100:.2f}%]")
    else:
        print(f"  95% CI (cluster bootstrap, PRIMARY) : n/a (need >= 2 repositories)")
    print(f"  95% CI (Wilson, secondary)          : [{wil[0]*100:.2f}%, {wil[1]*100:.2f}%]")

    # Minimum-exposure gates (METHOD.md §5) + the absolute-threshold rule (§3, G4).
    print("  exposure & gate checks:")
    def check(ok, text):
        print(f"    [{'PASS' if ok else 'FAIL'}] {text}")
    check(n >= 300, f">= 300 audited findings (have {n})")
    check(len(repos) >= 10, f">= 10 repositories (have {len(repos)})")
    check(dom_frac <= 0.5, f"no single repo dominates (top repo '{dom_repo}' = {dom_frac*100:.0f}% of findings)")
    if not math.isnan(boot[1]):
        ok = boot[1] * 100 < threshold_pct
        check(ok, f'"< {threshold_pct:g}%" claim: cluster-bootstrap CI-upper ({boot[1]*100:.2f}%) < {threshold_pct:g}%')


def main():
    ap = argparse.ArgumentParser(description="Recompute a Watchdog noise measurement from a verdicts file.")
    ap.add_argument("verdicts", help="CSV or JSONL of per-finding verdicts (see verdicts.schema.json)")
    ap.add_argument("--by-language", action="store_true", help="also break the number down per language")
    ap.add_argument("--threshold", type=float, default=10.0, help='the "< X%%" claim to test (default 10; the G4 gate)')
    args = ap.parse_args()

    rows, unknown = load(args.verdicts)
    if unknown:
        print(f"note: {unknown} row(s) had an unrecognised class and were excluded.", file=sys.stderr)
    if not rows:
        print("no usable verdicts.", file=sys.stderr)
        sys.exit(1)

    report("pooled (all repositories)", rows, args.threshold)

    if args.by_language:
        by_lang = defaultdict(list)
        for r in rows:
            by_lang[r["language"] or "(unspecified)"].append(r)
        for lang in sorted(by_lang):
            report(f"language: {lang}", by_lang[lang], args.threshold)


if __name__ == "__main__":
    main()
