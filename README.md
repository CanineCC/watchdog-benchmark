# watchdog-benchmark

The public **method, evidence, and tooling** behind Watchdog's code-quality and noise claims — so a stranger
with no access to us can check the numbers. "Ask the other tools for theirs."

Watchdog (by [canine.dev](https://watchdog.canine.dev)) runs a scheduled codebase survey and produces one
reproducible 0–100 Codebase Assurance Index with a ranked "what to fix next". This repository is where we publish
**how we measure our own signal-to-noise**, the **data** a published result rests on, and the **open scripts** to
recompute it. If Watchdog says its noise is *X%*, everything you'd need to audit that claim lives here.

## This is not CAI, on purpose

Two different things, kept at arm's length in two repositories:

- **[CAI](https://github.com/CanineCC/CAI)** ([cai.canine.dev](https://cai.canine.dev)) — the open **standard**:
  how *any* Codebase Assurance Index score is made and verified. Vendor-neutral by design; anyone can implement it.
- **This repo (`watchdog-benchmark`)** — **one product's self-measurement**: how noisy *Watchdog* is, measured
  against a published protocol. This is Watchdog's evidence, not the standard.

Folding a vendor's self-measurement into the neutral standard would quietly make "open standard" mean "Watchdog's
home turf". So they stay separate. The *score's* reproducibility is a CAI matter; the *noise measurement* is here.

## What's here

| | |
|---|---|
| [`METHOD.md`](METHOD.md) | The frozen measurement protocol — the five-class noise taxonomy, the noise formula, the publication gates, the statistics, the exposure floors. |
| [`judge/five-class-judge-prompt.md`](judge/five-class-judge-prompt.md) | The exact prompt a machine judge is given to classify a finding, so the judging is reproducible. |
| [`tools/noise_stats.py`](tools/noise_stats.py) | Open, dependency-light: recompute the noise %, the cluster-aware bootstrap confidence interval, and the exposure-gate checks **from a verdicts file** — ours or your own. |
| [`REPRODUCE.md`](REPRODUCE.md) | How to re-derive a published number three independent ways. |
| [`data/`](data/) | Where the published draws, raw findings, and every verdict land — **with the first measured result** (see below). |

## What's deliberately **not** here

- **The engine / analyzer / scanner.** That is the product, and it stays private. You don't need it: we publish the
  engine's *findings* as data, and you check the number against those.
- Any customer or private code, and any repository with a rater conflict of interest.
- **Any unmeasured or internal number.** See the honesty gate.

## The honesty gate (why `data/` is mostly empty today)

A noise rate is only worth publishing if it was **measured on a blind holdout and validated by humans**.
Until a result clears that bar we publish the **method** and the **target**, never an achieved figure:

- **Target:** an **audited broad-noise rate (ABN)** **below 5%** over scored dimensions, measured under the broad
  five-class taxonomy on a **blind rotating holdout** — a ratchet of **< 5% → < 2.5% → < 1%** as the engine earns
  each. (ABN was called an "effective false-positive rate" through protocol 1.0; the ratio is unchanged, but that
  term denotes an observed user-behaviour event we do not measure. See `METHOD.md` §12.)
- **No achieved Watchdog noise number** appears anywhere here (or in our marketing) until a fresh-holdout run is
  human-validated. When it is, the full run — the published draw, raw findings, every verdict, agreement statistics —
  publishes into `data/` and you can re-run the arithmetic yourself with `tools/noise_stats.py`.

The published literature we measure *against* (independent measurements of mainstream tools) is summarised in
`METHOD.md`; the verbatim-quote evidence archive for those third-party figures is added after a citation/legal pass.

## License

[Apache-2.0](LICENSE). (Data files added later may additionally carry a data license; noted per directory.)
