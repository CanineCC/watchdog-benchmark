# data/

Measured runs land here — **one directory per run** — once a result clears the gates in
[`../METHOD.md`](../METHOD.md) §3 (a sealed fresh holdout, human-validated judging at κ ≥ 0.8, the absolute
threshold). It is mostly empty today **on purpose**: publishing an unmeasured or un-validated number would break
the discipline the whole method exists to enforce (see the honesty gate in [`../README.md`](../README.md)).

## What a run directory will contain

```
data/<run-id>/
  manifest.json     the sealed holdout: repos + pinned SHAs, the committed manifest file-hash, the freshness screen
  README.md         tool pins (versions + container digests) and default configs; the judge model id; consumption context
  <tool>/
    findings.jsonl  the tool's raw normalized findings (the OUTPUT — not the tool)
    verdicts.csv    every raw verdict, machine and human (see ../tools/verdicts.schema.json)
  human-sample.csv  the stratified sample the two human raters audited
  agreement.json    inter-rater κ and machine-vs-human agreement on the noise-vs-valid boundary
```

Recompute any published number straight from `verdicts.csv` with [`../tools/noise_stats.py`](../tools/noise_stats.py),
or re-derive it the other two ways in [`../REPRODUCE.md`](../REPRODUCE.md).

## Status

_No measured run is published yet._ Watchdog's first result publishes here when a sealed fresh-holdout run is
human-validated under the target (see `../METHOD.md` §9). Until then the method, the judge, and the tooling above
are the claim — and the target is **< 5% effective false-positive rate**, not an achieved figure.
