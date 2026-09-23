# Q6 — Build a divergence measure for need and demand

**Division:** undergraduate and graduate. **Graduate addendum required** — see
[addendum.md](addendum.md).
**Owner:** Valentino
**Status:** not started

---

## The ask, in our words

Food shelf activity shows where people **arrive**. It does not show where people **need
help and do not get it**.

1. Create a **new metric or measure** that highlights areas where need is likely larger
   than the activity data shows.
2. **Compare and contrast** it against the three food shelf metrics.
3. Identify **where the new measure and the activity metrics diverge**.
4. Like Q1, **investigate county characteristics** that explain the disagreement.

The brief adds two constraints that are really the whole question:

> Your new metric or measure of need should consider **more than just demand**.
> A sufficient and complete measure of need will likely require the use of **other
> publicly available data**.

---

## The design constraint that decides everything

Your inputs must be **independent of food shelf visits** and **not already inside the Map
the Meal Gap model**. MMG is modelled largely from poverty and unemployment. If you build
an index out of poverty and unemployment, you have rebuilt Map the Meal Gap, given it a
new name, and discovered that it correlates with Map the Meal Gap.

The measure has to add something MMG does not have. The candidates that do:

| signal | why it is not in MMG and not demand | source |
|---|---|---|
| **distance to nearest site** | pure access, derived from our own `block_geoid` | ours, via Gazetteer — see [BLOCK_GEOID.md](../../docs/BLOCK_GEOID.md) |
| **no-vehicle households** | the brief's "no transport" barrier, measured | ACS `B08201` |
| **SNAP participation gap** | eligible-but-not-enrolled: under-claiming, not poverty | DHS caseload ÷ MMG income-eligible FI persons |
| **senior share** | seniors under-claim food assistance at known rates | ACS `S0101` |
| **school meal eligibility** | child need, measured outside the MMG pipeline | MN Dept of Education |
| **site density / capacity** | supply-side, not need-side, but it is what makes need invisible | ours |

---

## Approach

1. **Define need in one sentence, before you touch the data.** The graduate addendum
   requires a falsifiable definition, and writing it first stops the index from becoming
   whatever the data happened to produce.
2. **Build the index.** Normalise each input (rank or z-score), combine with stated
   weights. Simple and explainable beats sophisticated — you will defend this live.
3. **Divergence = need rank − activity rank.** Do it for each of the three metrics
   separately; the brief asks for all three. A county that ranks 5th in need and 60th in
   households served is the story.
4. **Map it.** This is the one question where a Minnesota map genuinely earns its place.
5. **Explain the divergence** with county characteristics, exactly as in Q1.
6. **Stability check.** Re-run with alternative weights. If the top ten counties change,
   the ranking is not a finding — say so and fix it.

---

## What the preview already shows

From `python src/eda.py`:

- The rank correlation between activity per food-insecure person and the food insecurity
  rate is **negative** (−0.26 to −0.29 in 2024). Higher-need counties serve *fewer*
  households per food-insecure person. The divergence the brief hypothesises is already
  visible in the raw comparison.
- **Wilkin County (FIPS 27167) has no reporting food shelf in any of the 55 months.**
  Feeding America estimates food-insecure people there. Observed demand is zero. This is
  the cleanest possible illustration of the question and it belongs on a slide.
- **Rural against metro, 2024:** metro counties serve **4.91** households per
  food-insecure person; rural counties serve **2.98**. But rural counties carry **400**
  food-insecure people per site against metro's **637**. Reach and load point in opposite
  directions, and an index that collapses them into one number loses that.

---

## Traps

- **Rebuilding Map the Meal Gap.** Covered above. This is the failure mode.
- **Arbitrary weights.** Show stability, or do not show a ranking.
- **Circularity through site density.** If low site density drives your need index, and
  you then conclude that low-site-density counties are underserved, you have written a
  tautology. Site density is a *plausible explanation* of divergence, not an *input* to
  need.
- **Small-county noise.** A county with 400 food-insecure people moves ranks on almost
  nothing. Report uncertainty or pool.
- **Cross-county use.** A household that drives to the next county makes its own county
  look underserved. Check whether the divergent counties border a high-activity one —
  and if they do, say so before a judge does.

---

## Deliverables

- [ ] `analysis.py` that rebuilds the index from `data/processed/` + `data/external/`
- [ ] The index itself, documented input by input, with weights and the reason for each
- [ ] A county-level divergence table against all three metrics
- [ ] One map for the deck
- [ ] Stability analysis under alternative weights
- [ ] [addendum.md](addendum.md) completed — it is graded separately
