# The Watchdog noise-measurement protocol

**Version 2.0 (public).** This is the frozen method by which Watchdog measures its own — or any tool's — noise.
It is fixed *before* any measured run, so no methodological choice can be made after seeing a number we like.

Read this with [`REPRODUCE.md`](REPRODUCE.md) (how to check a result) and
[`judge/five-class-judge-prompt.md`](judge/five-class-judge-prompt.md) (the exact judging instruction).

> **What changed in 2.0, and what did not.** The construct is renamed to **audited broad-noise (ABN)**; the
> binding precedence order and collapse-then-classify sequence are stated explicitly; the holdout design moves
> from *sealed once* to *rotating per cycle*; and **ABN is now defined over a stated dimension scope**, with
> the committed number being **ABN(scored)** and the advisory rate published beside it (§2, §3).
> **No class boundary, no denominator and no precedence rule changed** — §11 records this in full.

---

## 1. What "noise" means — the five-class taxonomy

A precision or false-positive percentage is meaningless without a stated definition of the event being counted.
We use the strictest available definition. The ratio below is the **audited broad-noise rate (ABN)**: the share of
audited findings an informed maintainer would decline to act on, as classified by an auditor.

> **ABN is an auditor classification, not an observed user behaviour.** Earlier versions of this protocol called
> it an *effective false-positive rate*. That term denotes a measured user-behaviour event in the Tricorder
> literature; we do not measure user behaviour, so the name is withdrawn. The ratio, the classes and their
> boundaries are unchanged.

Every audited finding is placed in exactly one class:

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

### 1.1 Collapse, then classify — and the binding precedence order

Two findings can satisfy two class definitions at once. The decision procedure is therefore fixed, so that two
auditors reaching the same conclusion cannot record different classes.

**Step 1 — collapse.** Reduce same-issue-same-site detections to one logical finding, annotated with every
contributing lens, *before* any class is assigned.

**Step 2 — classify, in this precedence.** The first rule that applies decides the class:

1. **false-positive** — a finding whose factual premise is untrue is false-positive **even if** its
   recommendation would also be inapplicable. A false premise outranks everything below it.
2. **opinion-not-fact** — a correct measurement carrying a conclusion, framing or quantified promise beyond what
   it supports is opinion-not-fact **before** redundancy or applicability is considered.
3. **redundant** — among separately retained findings, redundancy is tested **before** shape or context
   applicability. Corroborating measurements are *not* redundant when they support independent propositions or
   materially different decisions.
4. **shape-irrelevant** — a retained finding that is neither untrue, over-claimed nor redundant, but applies an
   obligation foreign to the kind of software scanned.
5. **valid** — everything else, including everything uncertain.

**Evidence defects do not move the verdict by themselves.** A minor location defect leaves a substantively valid
finding *valid* and raises the evidence-defect flag (§2). A **material** evidence defect that prevents reasonable
verification does change the primary verdict to false-positive.

## 2. The ABN formula

★ **ABN is defined over a stated dimension scope, and the scope is part of the number.** A rate quoted without
one is not an ABN; it is an average of two different questions.

For a tool *t* on a corpus *C* over a dimension set *D*:

```
ABN(t, C, D) = (#false-positive + #opinion-not-fact + #redundant + #shape-irrelevant)
               ──────────────────────────────────────────────────────────────────────
                        #audited findings of t on C from dimensions in D
```

Two scopes are published, always together, and neither is published alone:

| | scope | what it answers |
|---|---|---|
| **ABN(scored)** — *the committed number* | dimensions that can move a user's score | the noise in what a user is actually scored on |
| **ABN(advisory)** | dimensions that cannot | how much we should trust the detectors we already declined to price with |

**Every published headline, gate and target in this protocol refers to ABN(scored)** unless it says otherwise.
There is no third, merged figure: an ABN over `scored ∪ advisory` is not defined here, because it averages a
measurement of the product with a measurement of detectors the product does not rely on, and — see §3 — it is not
comparable across languages.

- **The denominator is finding-level records only.** Tool-level summary claims (e.g. "0 vulnerable dependencies"
  asserted as a score) are audited under the same taxonomy but recorded separately, never mixed into this ratio —
  a percentage over a mixed denominator is ill-defined.
- **Two orthogonal flags travel beside the verdict and are published separately, never folded into ABN:**
  - *evidence-defect* — the finding is right in substance but wrong in coordinates (line/range/magnitude). If a
    developer can still locate and verify it, the verdict stays *valid* and this flag increments a published
    evidence-defect rate; if the corrupted evidence defeats verification, it falls to *false-positive*.
  - *did-not-clear* — an auditor fixes a sampled finding, rescans, and it fails to clear (a fingerprint/detection
    defect). Published, but kept out of the ABN ratio (it measures the fix-verification loop, not precision).

## 3. What the committed rate covers — scored and advisory dimensions

A tool's dimensions divide into two kinds, and the distinction is a **product** decision that predates any
measurement:

- **Scored dimensions** contribute to the score a user is given. They price something.
- **Advisory dimensions** do not, and cannot. They are surfaced to the user and explicitly cannot move the score,
  because the detector is not trusted enough to price with.

§2 fixes the arithmetic; this section fixes *which dimensions are in which scope*, and why the split is not an
accounting preference but a condition of the number meaning anything.

Three reasons, in order of importance:

1. **A merged rate describes something no user is scored on.** Mixing a measurement of the product with a
   measurement of detectors we have already declared untrusted answers no question anyone asked.
2. **★ A merged rate is not comparable across languages.** Advisory coverage is uneven: a dimension family that
   only analyses one language contributes advisory findings for that language and none for the others. A merged
   cross-language table can therefore rank languages in the **wrong order** — not merely imprecisely — because one
   language carries a whole category the other does not. Publishing merged numbers side by side is a
   comparability defect, not a rounding one.
3. **The advisory figure is what justifies the category.** Advisory exists *because* those detectors are not
   trusted. Showing that they are also the noisier ones is the distinction doing its job.

### 3.1 ★ Reclassification must be published — the rule that keeps this honest

If the commitment covers only scored dimensions, then "advisory" becomes a place to put a noisy detector and keep
the headline down. That is the same defect as choosing a holdout by the outcome it produces, and this protocol
exists to make such choices impossible or visible.

Therefore:

- **A dimension is advisory because of what it is permitted to do — price, or not price — never because of how it
  measured.** Classification is a product decision, taken and recorded before a measurement.
- **A dimension moved into or out of the advisory set after it has been measured is named in the next
  publication, with the rate before and after the move.** A reclassification that silently changes a published
  number is indistinguishable from tuning the number.

Without the second rule the commitment validates itself: we would be promising to publish the noise in whatever
we chose to count.

## 4. The publication gates

A number is publishable only when its gates are green. Publication is mechanical, not editorial.

- **G1 — Blind, rotating holdout.** No published measurement is taken on repositories chosen after their results
  were known. Each **cycle** draws a fresh reserve per language, **before** any of that cycle's outcomes exist,
  by a **published seeded sampler**: repositories are ranked by `SHA-256(seed ␟ language ␟ samplerVersion ␟
  repoId)` ascending and the reserve is the first N eligible, where `N = max(reserveFloor, ⌈reserveFraction ×
  eligible⌉)`. **The seed is generated, not chosen**, and published at cycle open with the sampler version, the
  full drawn set (owner / name / commit measured) and every discard with its reason. A third party re-runs the
  ranking and confirms we did not pick our repositories.
  - **Nothing is permanently consumed.** Closing a cycle releases the reserve back to the pool; the next cycle
    draws again from a new seed. This is what makes the holdout *rotating* rather than sealed, and it is why a
    repository's measurement is anchored to the commit that cycle measured it at rather than pinned for ever.
  - **Eligibility is a boolean, and health only.** A repository is eligible when it clones, builds and completes
    a scan non-degraded. No score, verdict or noise figure of any kind is reachable by the sampler.
  - **Recency strata** are recorded per drawn repository and published with the draw, so a reader can see how
    much of the reserve had been seen before.
  - **A language that cannot assemble a clean reserve is published as not validated for that cycle, with its
    reason and counts** — it is never silently omitted, and it never blocks the other languages.
- **G2 — Human-validated judging.** A single machine judge (one model, one pinned version, one prompt embedding
  the §1 taxonomy and the §1.1 precedence order) audits every finding of every tool against the checked-out code,
  tool identity stripped as far as feasible. It is anchored to people: a stratified random sample of **≥ 100
  findings per tool** is audited by **two independent human raters** under the same taxonomy, blind to the machine
  and to each other. The gate requires **Cohen's κ ≥ 0.8** between raters and machine-vs-human disagreement
  **≤ 10%** on the noise-vs-valid boundary (else the judge is revised and everything re-judged). **At least one
  rater must not have built the engine.** Unresolvable disagreements default **against the tool's own interest**.
  **All raw verdicts are published.**

  **★ The human sample is drawn ONCE PER CYCLE, across every language, not once per language.** κ measures
  whether a human agrees with the machine judge, and that judge is one model with one pinned prompt applied to
  every language — so its reliability is a property of the *judge*, not of any language. Sampling per language
  buys only the detection of *uneven* reliability, and buys it badly: at 100 items per language a judge agreeing
  95% of the time yields κ = 0.835 with a 95% interval of **[0.69, 0.98]**, which can neither clear nor miss a
  0.8 bar. A single balanced sample of **500 findings** spread across the measured languages puts that interval
  inside **±0.04**.

  **The human sample is balanced on the machine's verdict — roughly half findings it called noise — rather than
  drawn to match the measured noise rate.** This is not a softer test. Cohen's κ discounts the agreement expected
  by chance, and where noise is rare that discount is severe: at a 19% noise rate the expected agreement is 0.70,
  against 0.50 in a balanced sample, so identical raw agreement scores markedly lower. A representative sample
  would be a harsher test of the *rate*, which G1 already measures directly, and a weaker test of the thing this
  gate is for — whether a human and the judge separate noise from valid the same way. **Two κ are therefore
  published, never one: κ on the sample as drawn, and κ re-weighted onto the measured prevalence, together with
  the confusion matrix they are both computed from.** The re-weighted figure is lower by construction; a reader
  can recompute at any prevalence they choose.

  **Disagreement is additionally reported per dimension and per language.** Per dimension is the primary cut: a
  judge's difficulty lives in the question a dimension asks rather than in the language it was asked about — the
  same dimension has ranged from **2.6% to 75.7%** noise across languages in one cycle, so a language's apparent
  unreliability is substantially its dimension mix. A slice carrying **≥ 4 disagreements at more than twice the
  overall rate** is named and re-sampled. **That threshold is fixed before the cycle's numbers are seen**, for
  the same reason the reserve is drawn before it is measured: a trigger chosen afterwards is a description, not
  a test. A pooled figure catches a judge that fails badly on one language — it drags the gate down — but not one
  that fails *mildly*; the per-slice screen exists for that case, and it is a trigger to investigate, never a
  per-language gate.
- **G4 — Absolute threshold.** Pooled micro-average over **scored dimensions** (§3); green only if the
  **cluster-aware 95% CI upper bound is below 10%** *and* no single language's point estimate is ≥ 2× the
  threshold. (Our internal *target* of < 5% sits inside this with margin — but < 5% is a target, not a gate the
  protocol tests: at G4 the measured number publishes wherever it lands in the band.)
- **G3 / G5 — comparators and separation** (for head-to-head claims) and **G6 — the sub-1% add-on** (full dual-human
  adjudication + a judge-misclassification correction) raise the bar further and are not required for an absolute
  < 10% / target-< 5% claim.

### 4.1 Pre-registration and the frozen engine

- **Pre-registration precedes the numbers.** Before a cycle's measurement begins we record, publicly, the
  commitment to publish the result in whichever direction it lands. A run whose result is published only if
  favourable is not a measurement.
- **The engine is frozen for the measurement.** A cycle names the exact build every pass must measure at, and no
  measurement of that cycle may ship engine code. A pass reporting a different build is refused, by name, rather
  than folded in — otherwise a published rate describes no particular version of the tool.
- **Two arms and the overfitting gap.** Where a cycle measures both a trained-on corpus and the blind reserve,
  both are published, and so is the gap between them. The gap is the quantity that says how much of an
  improvement was learning rather than fitting.

## 5. Confidence intervals

Every published proportion carries a **cluster-aware bootstrap 95% confidence interval** as the **primary**
interval — resampling by repository, because findings cluster by repo and by root cause (one detector defect can
emit scores of correlated false positives in one repo), which the independence assumption of a closed-form
interval violates. A **Wilson score interval** and Clopper–Pearson are reported alongside as secondary/sanity
figures. A headline "< X%" requires the interval's **upper** bound below X, not the point estimate.

## 6. Minimum exposure

- **No claim of any kind below 300 audited findings** per tool per published number.
- **Every claim scope** (aggregate or per-language) additionally requires **≥ 10 repositories** in its holdout
  slice, with **no single repository dominating** the audited findings, and ≥ 3 repositories per language.
- Because a "< 1%" upper-bound claim needs a large zero-or-near-zero numerator, **< 5% is the first target and
  < 1% is a later ratchet**.

## 7. Coverage is always published beside noise

A tool that reports almost nothing is trivially "precise". So every ABN number ships in the same row as its
**finding density (findings per KLoC)** and its **scope coverage**. A silent tool never wins, and that includes us.

## 8. ★ Concentration: when one detector carries the number

A pooled rate can be dominated by a single detector. When that happens the number is still correct, but it is no
longer a statement about the tool as a whole — it is a statement about that detector, and publishing it as the
former would mislead in both directions.

Concentration is therefore detected **mechanically**, not by eye:

- Per-dimension noise rates are reduced to their **median** and **median absolute deviation (MAD)** — robust
  statistics, chosen because a mean and standard deviation are themselves distorted by the outlier being looked
  for.
- A dimension is an **outlier** when its modified z-score `0.6745 × (rate − median) / MAD` exceeds **3.5**, and it
  produced at least **10 audited findings**. The findings floor exists because a dimension with three findings at
  100% is a coincidence, not a detector defect, and without the floor those crowd out the one that matters.
- **A published number whose outlier carries more than 50% of all noise must name it** — the dimension, its rate,
  its share, and what is being done about it. The outlier is published as a result, not smoothed away.

**MAD is the diagnostic, not the metric.** The published rate remains the pooled ratio of §2. A median-per-dimension
headline would quietly down-weight whichever detector is loudest, which is precisely the arithmetic this protocol
exists to prevent; and a user experiences findings, not dimensions.

## 9. Fair, out-of-the-box, disclosed

- Every tool runs its **default configuration** — the measured experience is the buyer's first-contact experience,
  and defaults are the only setting nobody can accuse us of tuning to flatter ourselves.
- Versions and container digests are **pinned**; every checkout is identical across tools.
- **Consumption context is disclosed** (all measurements are batch, whole-repo scans; no claim is transferred to
  diff-time behaviour). A noise number is meaningless unless the consumption context is stated alongside it.
- **A cap on findings per dimension per repository, where one applies, is declared before the cycle** and
  published with the result. An uncapped and a capped measurement are different measurements.

## 10. The reproduction package (what publishes with every measured result)

When a result clears G1/G2/G4, the full run publishes into [`data/`](data/):

1. The **published draw** — seed, sampler version, the drawn set with owner / name / measured commit, recency
   strata, and every discard with its reason.
2. The **tool pins** — versions and container digests, and the exact default configuration used.
3. The **machine-judge prompt** and pinned **model id** (see [`judge/`](judge/)).
4. The **raw normalized findings** each tool produced (the *output*, not the tool).
5. **Every raw verdict** — machine and human — the human sample, and the inter-rater agreement statistics.
6. The **dimension classification** in force for the run — which dimensions were scored and which advisory — and
   any reclassification since the previous published run (§3.1).
7. The **statistics** — recomputable from the verdicts with [`tools/noise_stats.py`](tools/noise_stats.py),
   including the scored/advisory split and the concentration analysis of §8.

The standing answer to any challenge is: **run it.**

## 11. The target, and the discipline

Watchdog's official bar is **ABN(scored) below 5%** — audited broad noise over the dimensions that can move a
user's score — on a blind rotating
holdout under the broad taxonomy above — a target, and a deliberately demanding one (broad-definition, stricter
than the narrow-precision numbers most tools quote). The ratchet is **< 5% → < 2.5% → < 1%**, each a separate
result as the engine earns it.

**No achieved Watchdog noise number is stated as fact until a fresh-holdout run is human-validated** — until then,
the target and this method are the whole claim.

## 12. Version history

**2.0 — terminology, decision procedure, holdout design, and the scored/advisory split.**

| Changed | Not changed |
|---|---|
| The construct is named **audited broad-noise (ABN)**. "Effective false-positive rate" is withdrawn because it denotes an observed user-behaviour event we do not measure. | The ratio itself, its numerator and its denominator. |
| The **binding precedence order** and the collapse-then-classify sequence are stated explicitly (§1.1). | The five class boundaries. The precedence was always the intended decision procedure; it was previously left implicit, which is a clarification, not a revision. |
| The holdout is **rotating and drawn per cycle from a published generated seed** (§4 G1), replacing a once-sealed manifest. Nothing is permanently consumed. | That no published measurement runs on repositories chosen after their results were known — the property the sealed design existed to guarantee. |
| **ABN carries its dimension scope in the definition** (§2): the committed number is **ABN(scored)**, the advisory rate publishes beside it, and no merged figure is defined. §3.1 requires reclassification to be published. | The denominator's definition *within* a given scope — the arithmetic is identical, only the scope is now named. |
| §8 adds mechanical **concentration detection** and a disclosure requirement. | The published statistic remains the pooled ratio of §2. |

Earlier versions of this file are in the repository history; no published result has been recomputed under 2.0
that was published under 1.0, because no result had yet cleared G2 when 2.0 was adopted.
