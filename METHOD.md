# The Watchdog noise-measurement protocol

**Version 1.0 (public).** This is the frozen method by which Watchdog measures its own — or any tool's — noise.
It is fixed *before* any measured run, so no methodological choice can be made after seeing a number we like.

Read this with [`REPRODUCE.md`](REPRODUCE.md) (how to check a result) and
[`judge/five-class-judge-prompt.md`](judge/five-class-judge-prompt.md) (the exact judging instruction).

---

## 1. What "noise" means — the five-class taxonomy

A precision or false-positive percentage is meaningless without a stated definition of the event being counted.
We use the strictest available definition — an **effective false positive**: *any finding a user would decline to
act on*, whether or not it is technically correct. Every audited finding is placed in exactly one class:

| Class | Signal? | Rule |
|---|---|---|
| **valid** | signal | Factually true at the cited location, and an informed maintainer of *this* codebase would accept it as a real, non-trivial issue (or an accurate measurement). **Uncertain = valid** — the auditor never manufactures noise; ambiguity is resolved in the tool's favour. |
| **false-positive** | noise | Asserts something factually untrue of the code, or publishes a score/claim with no supporting evidence. The auditor must be able to state the concrete disproof — file, line, mechanism — not merely disagree. |
| **opinion-not-fact** | noise | The measurement is accurate, but the stated conclusion, framing, or quantified promise goes beyond what the measurement supports. |
| **redundant** | noise | True, but — *after the logical-finding collapse below* — still restates another finding such that one remediation clears both and the second adds no separately-actionable information. Multi-lens detection of one issue is **not** redundant (see below). |
| **shape-irrelevant** | noise | Factually grounded, but applies an expectation foreign to the *kind* of software being scanned (a library / CLI / service / desktop app / framework), which an informed maintainer would decline as "not applicable to what this is". |

**A binary true/false rate captures only the first noise class**, so it is a *lower bound* on real noise. The
broad five-class number is at least as high as any binary FP rate on the same findings.

**The unit of measurement is the logical finding, not the rule that fired.** When several lenses (dimensions)
detect the *same issue at the same site*, they are counted as **one** finding annotated with every contributing
lens — counted once, one verdict, decided by the underlying issue. **Corroboration across lenses is signal
(independent confirmation the issue is real), never noise.** A finding is never scored as noise merely for being
seen by more than one lens: a *false positive* means the tool said something **untrue**, whereas two true
measurements of one real issue (e.g. a function's cyclomatic *and* cognitive complexity) are both true — scoring
the second as noise would conflate "reported it twice" with "got it wrong". Where multiple lenses instead fire on
something that should not have been flagged at all (e.g. a generated file read as authored source), the collapsed
single finding is scored **shape-irrelevant** or **false-positive** on its merits — again one finding, not N.

## 2. The noise formula

For a tool *t* on a corpus *C*:

```
noise(t, C) = (#false-positive + #opinion-not-fact + #redundant + #shape-irrelevant)
              ──────────────────────────────────────────────────────────────────────
                                #audited findings of t on C
```

- **The denominator is finding-level records only.** Tool-level summary claims (e.g. "0 vulnerable dependencies"
  asserted as a score) are audited under the same taxonomy but recorded separately, never mixed into this ratio —
  a percentage over a mixed denominator is ill-defined.
- **Two orthogonal flags travel beside the verdict and are published separately, never folded into noise:**
  - *evidence-defect* — the finding is right in substance but wrong in coordinates (line/range/magnitude). If a
    developer can still locate and verify it, the verdict stays *valid* and this flag increments a published
    evidence-defect rate; if the corrupted evidence defeats verification, it falls to *false-positive*.
  - *did-not-clear* — an auditor fixes a sampled finding, rescans, and it fails to clear (a fingerprint/detection
    defect). Published, but kept out of the noise ratio (it measures the fix-verification loop, not precision).

## 3. The publication gates

A number is publishable only when its gates are green. Publication is mechanical, not editorial.

- **G1 — Fresh, sealed holdout.** No published measurement runs on a repository the tool's training/tuning has ever
  seen. The exclusion list is public; the holdout is selected by a pre-registered deterministic rule from a
  candidate pool generated *after* a declared freeze, then **sealed** — the SHA-pinned manifest and its file-hash
  are committed *before the first scan of any tool*. Freshness is checked with fork detection and a code-level
  near-duplicate screen.
- **G2 — Human-validated judging.** A single machine judge (one model, one pinned version, one prompt embedding the
  §1 taxonomy) audits every finding of every tool against the checked-out code, tool identity stripped as far as
  feasible. It is anchored to people: a stratified random sample of **≥ 100 findings per tool** is audited by **two
  independent human raters** under the same taxonomy, blind to the machine and to each other. The gate requires
  **Cohen's κ ≥ 0.8** between raters and machine-vs-human disagreement **≤ 10%** on the noise-vs-valid boundary
  (else the judge is revised and everything re-judged). **At least one rater must not have built the engine.**
  Unresolvable disagreements default **against the tool's own interest**. **All raw verdicts are published.**
- **G4 — Absolute threshold.** Pooled micro-average; green only if the **cluster-aware 95% CI upper bound is below
  10%** *and* no single language's point estimate is ≥ 2× the threshold. (Our internal *target* of < 5% sits inside
  this with margin — but < 5% is a target, not a gate the protocol tests: at G4 the measured number publishes
  wherever it lands in the band.)
- **G3 / G5 — comparators and separation** (for head-to-head claims) and **G6 — the sub-1% add-on** (full dual-human
  adjudication + a judge-misclassification correction) raise the bar further and are not required for an absolute
  < 10% / target-< 5% claim.

## 4. Confidence intervals

Every published proportion carries a **cluster-aware bootstrap 95% confidence interval** as the **primary**
interval — resampling by repository, because findings cluster by repo and by root cause (one detector defect can
emit scores of correlated false positives in one repo), which the independence assumption of a closed-form
interval violates. A **Wilson score interval** and Clopper–Pearson are reported alongside as secondary/sanity
figures. A headline "< X%" requires the interval's **upper** bound below X, not the point estimate.

## 5. Minimum exposure

- **No claim of any kind below 300 audited findings** per tool per published number.
- **Every claim scope** (aggregate or per-language) additionally requires **≥ 10 repositories** in its holdout
  slice, with **no single repository dominating** the audited findings, and ≥ 3 repositories per language.
- Because a "< 1%" upper-bound claim needs a large zero-or-near-zero numerator, **< 5% is the first target and
  < 1% is a later ratchet**.

## 6. Coverage is always published beside noise

A tool that reports almost nothing is trivially "precise". So every noise number ships in the same row as its
**finding density (findings per KLoC)** and its **scope coverage**. A silent tool never wins, and that includes us.

## 7. Fair, out-of-the-box, disclosed

- Every tool runs its **default configuration** — the measured experience is the buyer's first-contact experience,
  and defaults are the only setting nobody can accuse us of tuning to flatter ourselves.
- Versions and container digests are **pinned**; every checkout is identical across tools.
- **Consumption context is disclosed** (all measurements are batch, whole-repo scans; no claim is transferred to
  diff-time behaviour). A noise number is meaningless unless the consumption context is stated alongside it.

## 8. The reproduction package (what publishes with every measured result)

When a result clears G1/G2/G4, the full run publishes into [`data/`](data/):

1. The **sealed holdout manifest** — repo list with pinned SHAs, the committed manifest file-hash, the freshness screen.
2. The **tool pins** — versions and container digests, and the exact default configuration used.
3. The **machine-judge prompt** and pinned **model id** (see [`judge/`](judge/)).
4. The **raw normalized findings** each tool produced (the *output*, not the tool).
5. **Every raw verdict** — machine and human — the human sample, and the inter-rater agreement statistics.
6. The **statistics** — recomputable from the verdicts with [`tools/noise_stats.py`](tools/noise_stats.py).

The standing answer to any challenge is: **run it.**

## 9. The target, and the discipline

Watchdog's official bar is an **effective false-positive rate below 5%** on a sealed fresh holdout under the broad
taxonomy above — a target, and a deliberately demanding one (broad-definition, stricter than the narrow-precision
numbers most tools quote). The ratchet is **< 5% → < 2.5% → < 1%**, each a separate result as the engine earns it.
**No achieved Watchdog noise number is stated as fact until a fresh-holdout run is human-validated** — until then,
the target and this method are the whole claim.
