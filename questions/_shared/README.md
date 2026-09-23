# Q2 and Q3 — not scored for us, but not useless

The brief scores Questions 2 and 3 in the **novice division only**. It also says, in the
same paragraph:

> The table above determines what outcomes will be judged for each division. It does not
> limit which data you use. Every dataset is available to every division. An undergraduate
> team or a graduate team **may consider Question 2 or Question 3 and carry their findings
> into another question.**

So we do not answer them. We mine them.

---

## Q2 — Are calls a signal for visits?

**Carry into: Q5, and secondarily Q6.**

The call log is a SNAP helpline. That makes it a second, independent read on SNAP-related
distress that costs us nothing to use, and Q5 is precisely about SNAP.

What it can support:

- A **leading indicator** check: do SNAP eligibility and application calls rise in a
  county before caseloads or food shelf activity move? If yes, that is a genuinely useful
  operational finding for The Food Group, and it belongs in the Q5 story.
- A **barrier signal** for Q6: counties where calls about food assistance rise but food
  shelf activity does not are counties where something sits between wanting help and
  getting it. That is exactly what Q6's divergence measure is trying to find, and the
  call data points at specific counties.

What it cannot support, and why:

- **31% of calls are SNAP Rx** — clinic-pushed referrals. Their volume tracks which
  clinics are enrolled in the program, not household demand. `qkit.calls(exclude_snap_rx=True)`
  drops them, and you should almost always drop them.
- **34% of calls have no usable county.** Any geographic claim has to state that share.
- **Volume is negligible before 2023** (41 records). No trend across the 2022/2023
  boundary is real. `sparse_period` flags them and `qkit.calls()` excludes them.
- The definition of a "food-related call" is **ours**, written in `build_calls()` in
  `clean_data.py`. If we use it in a scored answer, we defend it.

```python
calls = qkit.calls(food_only=True, exclude_snap_rx=True, geocoded_only=True)
```

---

## Q3 — Farmers markets and food shelves

**Carry into: Q6, and secondarily Q5.**

Market Bucks is a SNAP-linked incentive at farmers markets. Where it works well, it is
evidence that a county's low-income households are reachable — which changes how you read
low food shelf activity in that same county.

What it can support:

- A **reachability signal** for Q6: a county with low food shelf activity *and* strong
  Market Bucks participation is reached, but through a different channel. A county with
  low activity on both is a different story, and separating the two is real insight.
- A **SNAP intensity proxy** for Q5: `SNAPDistributed` at markets is SNAP dollars being
  spent, at a site and date level.

What it cannot support:

- **Coverage is narrow.** 48 counties with Market Bucks against 86 with food shelf
  activity. It cannot carry a statewide claim.
- **It is strongly seasonal.** Distribution peaks in August and is effectively limited to
  the growing season. Any comparison with food shelf activity must hold the season fixed,
  or market seasonality will masquerade as an effect.
- **Redeemed above distributed is normal**, not an error — customers carry tokens between
  visits. 3,515 sessions look like this. Flagged `redeemed_over_distributed`; do not "fix"
  them.
- **753 sessions have no county** because the site record has none.

```python
mb = qkit.marketbucks()
```

---

## The rule

Findings from Q2 and Q3 go into a **scored** question's slide or appendix, attributed to
the data they came from. They do not get their own slide, because they earn us no points
and they cost presentation time we do not have.
