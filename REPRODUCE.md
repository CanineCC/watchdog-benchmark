# Reproduce a published number

When a measured result is published into [`data/`](data/), you can check it **three independent ways** — none of
which needs Watchdog's engine. (The engine is private; we publish its *findings* as data, and you audit those.)

Each published run is a directory `data/<run-id>/` containing: the published `draw.json` (seed, sampler version,
the drawn repos with the commit each was measured at, recency strata, and every discard with its reason), each
tool's raw normalized `findings.jsonl`, every `verdicts.csv` (machine and human), the human sample, the
inter-rater agreement stats, the dimension classification in force (which dimensions were scored and which
advisory), and the run's `README.md` (tool pins, judge model id, consumption context).

**Re-run the draw yourself.** The sampler is `SHA-256(seed ␟ language ␟ samplerVersion ␟ repoId)` ascending,
keeping the first `max(reserveFloor, ⌈reserveFraction × eligible⌉)`. Same seed and same eligible pool must give
the identical set — that check is the point of publishing the seed.

## 1. Recompute the arithmetic (seconds)

Trust nothing about our reported percentage — recompute it from the raw verdicts:

```bash
python3 tools/noise_stats.py data/<run-id>/verdicts.csv --by-language --threshold 5
```

This re-derives the pooled noise %, the cluster-aware bootstrap CI (the primary interval), the Wilson interval, and
the exposure-gate checks. It should match the published number to the last digit. Try it now on the synthetic
sample (clearly fake data, for exercising the script only):

```bash
python3 tools/noise_stats.py tools/example-verdicts.synthetic.csv
```

## 2. Re-run the judge on our findings

Take our published `findings.jsonl`, hand each finding to the [published judge prompt](judge/five-class-judge-prompt.md)
with any capable model (the run records the model we pinned), against the repository at the manifest's pinned SHA,
and produce your *own* verdicts. Then compare to ours with `noise_stats.py`. Disagreement is the interesting part —
G2 (`METHOD.md` §3) is exactly the discipline that anchors the machine judge to two independent humans, and every
raw human verdict is published so you can see where we split.

## 3. Audit our findings by hand

Pick any repository from the manifest, check it out at the pinned SHA, and classify our findings on it yourself
under the five-class taxonomy. This is the human audit G2 requires — done in the open. Unresolvable calls in a
Watchdog self-measurement default *against* Watchdog, so if you and we disagree on a boundary case and you can't
resolve it, count it as noise on us.

## …and the full end-to-end

To go all the way — clone the drawn repos at the commits they were measured at, run **your own** scanner over
them, judge its
findings with the same prompt, and compute its noise the same way. That is the head-to-head the method is built
for. We publish *our* findings, not our engine, so you can't re-run Watchdog itself — but you can hold any tool,
including ours, to the identical, published standard. Ask the other tools for theirs.
