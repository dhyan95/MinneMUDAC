# Team plan — who does what, and by when

**Deadline: Friday 17 October 2026.** Roughly four working weeks from 22 September.
**Team of three. Graduate division: Q1, Q4, Q5, Q6 + addendum, Q7 + addendum, Q8.**
**Deliverable: a live presentation with Q&A, where judges may ask anything of anyone.**

---

## The three of us

| | background | what that means for the split |
|---|---|---|
| **Valentino** | BBA in supply chain management and MIS; MSBA | Systems and data plumbing. Has access to the strongest AI tooling of the three, which makes the infrastructure and the cross-cutting analytical work go fastest through him. |
| **Dhyan** | BEng computer engineering; MSBA | Strongest engineering fundamentals. Best fit for the time-series pipeline, which is the most technically demanding and least forgiving part. |
| **Uddam** | BSc computer science; MSBA; worked as a business development analyst at a medical center | The only one with real stakeholder experience. That matters more than it looks: this competition is judged by Food Group staff, not by statisticians. Uddam should own the framing and the deck as well as the geospatial work. |

Two of us have only internship experience, and the third has one analyst role. Nobody
here is a time-series specialist or a GIS specialist. **Plan for that.** The schedule
below front-loads the hard, unfamiliar work (Q7's leakage discipline, Q8's tract
crosswalk) so that a surprise in week 2 is recoverable and a surprise in week 4 is not.

---

## The split

The principle: **one person owns one analytical frame**, not a scattering of questions.
Questions that share a data shape go to the same person, because the second question then
costs a fraction of the first.

### Valentino — the cross-sectional frame
**Owns:** the cleaning pipeline (built), **Q1**, **Q6 + graduate addendum**

Q1 and Q6 are the same object: 87 counties, one row each, need on one axis and activity
on the other. Q6 is Q1 with a better need measure. Building them separately would be
wasted work.

Also owns the repo itself: `src/clean_data.py`, `src/geography.py`, `src/qkit.py`, and
the rule that nobody reads `data/raw/` directly. If the panel is wrong, all six answers
are wrong, so this is the first deliverable and it blocks everyone.

*Why Valentino:* the pipeline is already built, the strongest tooling access shortens the
most cross-cutting work, and the MIS background is exactly the data-plumbing skill set.

### Dhyan — the time-series frame
**Owns:** **Q4**, **Q5**, and the **Q7 model**

Q4, Q5 and Q7 are one monthly pipeline: county × month, with external monthly drivers
joined on. Q4's price lags and Q5's benefit-change events are *inputs* to the Q7 forecast,
so the same person should build all three or the forecast will not use them.

**This is the heaviest load in the team**, and it is deliberate — it goes to the strongest
engineer. Q7 is also the only scored *prediction*, so it gets the most careful pair of
hands.

*Why Dhyan:* computer engineering is the closest background to signal processing and lag
structure, which is what Q4 and Q7 actually are.

### Uddam — the spatial frame, the sources, and the story
**Owns:** **Q8**, the **Q7 age-group addendum**, the **source documentation table**, and
the **deck**

Q8 is the only graduate-exclusive question and the most distinguishing work available to
us. It is also the most self-contained: tracts, distances, LILA flags. The Q7 addendum
(children / seniors / adults) sits naturally here because it is a decomposition rather
than a new forecast — Dhyan hands over the total, Uddam splits it — and it keeps two
people inside Q7 rather than one.

The source documentation table is not busywork: the brief requires **four stated facts
per public source**, and a missing row is a scored loss. One person owning it is how it
gets finished.

The deck matters most and gets owned by the person with stakeholder experience. "These
counties are underserved, here is why, here is what to do" beats model sophistication
with this audience.

### Roles that are not questions

| role | who | why |
|---|---|---|
| **Leakage auditor** | **Uddam** | Must not be the person who built the Q7 model. Audits the whole repo for anything dated August 2026 or later before submission. This is the only rule in the brief with a stated penalty. |
| **Deck owner** | **Uddam** | One voice on the slides, not three. |
| **Panel owner** | **Valentino** | One canonical dataset; changes to it are announced, not silent. |
| **Q&A cross-briefer** | **Dhyan** | Runs the week-4 session where each of us explains someone else's question. |

---

## The weekly plan

### Week 1 — 22–28 September: foundations
**Goal: nobody is blocked, and no question starts from a blank page.**

| who | what |
|---|---|
| all | Read the brief. Read [DATA_ERRORS.md](DATA_ERRORS.md) and [BLOCK_GEOID.md](BLOCK_GEOID.md). Run `python src/clean_data.py` and `python src/eda.py` on your own machine and confirm you get the same numbers. |
| all | **Send the organizer email today** (questions below). Answers may take days. |
| all | Agree the Section-2 decisions and record the reasoning in **our own words**. "The AI suggested it" is not a defensible answer in Q&A. |
| Valentino | Panel v1 signed off. Q1 county frame built. Public covariates downloaded: SAIPE, PEP, ACS, Gazetteer. |
| Dhyan | BLS CPI downloaded and truncated at 2026-07. **Find the MN DHS county-monthly SNAP series** — this is the single highest-risk unknown in the project. If it does not exist, we need to know in week 1, not week 3. |
| Uddam | USDA Food Access Research Atlas downloaded. **Get the 2010→2020 tract crosswalk working** — this is the second highest-risk unknown. Source registry started. |

**End of week 1 test:** every external source we need is on disk, truncated, and has a
row in the registry. If a source turned out not to exist, we know now.

### Week 2 — 29 September–5 October: first answers
**Goal: one rough chart and one sentence per question. Ugly is fine.**

| who | what |
|---|---|
| Valentino | Q1 complete in draft: correlations, breakdown counties, covariates explaining residuals. Q6 need index designed and the falsifiable definition **written before results exist**. |
| Dhyan | Q4 lag analysis in draft. Q5 event study designed around verified benefit-change dates. **Q7 baselines backtested on August 2023, 2024, 2025** — this is the week 2 deliverable that matters most. |
| Uddam | Q8 coverage numbers in draft. Q7 age-share analysis. Deck skeleton: one slide per question, titles only. |

**End of week 2 test:** every question has a number attached to it. Anything with no
number by Friday is the thing we descope, and we decide that as a team rather than
discovering it the night before.

### Week 3 — 6–12 October: sharpen and connect
**Goal: six answers become one story.**

| who | what |
|---|---|
| all | **Through-line check, Monday.** What is the single sentence the deck argues? Draft: *"Visits measure demand; here is where need hides, and why."* Revisit it now that results exist — the data may argue something better. |
| Valentino | Q6 stability analysis under alternative weights. Q6 addendum finished. Q1 and Q6 reconciled so they do not contradict each other. |
| Dhyan | Q7 model beats the baselines in backtest, or we ship the baseline and say so. Q4 and Q5 finalised, and the two questions agree on which one claims the 2023 variation. |
| Uddam | Q8 limitations with **magnitudes**, not apologies. Source registry complete. Deck at draft quality, end to end. |

**End of week 3 test:** a full slide deck exists and can be read start to finish, even if
the charts are ugly. **Findings freeze Friday** — after this, no new analysis, only
tightening.

### Week 4 — 13–17 October: rehearse
**Goal: three people who can each defend all six questions.**

| when | what |
|---|---|
| Mon 13 | **Cross-briefing.** Each person explains someone else's question with no notes, and the owner corrects them. This is the single highest-value hour of the whole month, because judges ask anyone anything. |
| Tue 14 | **Leakage audit** by Uddam. Grep the repo for anything dated 2026-08 or later, in every external file and every derived table. Q7 numbers final after this, not before. |
| Wed 15 | **Deck frozen.** Every number on a slide traces to a script. Charts get their design pass. |
| Thu 16 | **Two full timed rehearsals with mock Q&A.** Each of us fields questions on a question we do not own. Write down every question we fumbled. |
| Fri 17 | **Present.** |

---

## Ask the organizers — send in week 1

Work proceeds on the working assumption until they reply. If they never reply, the
working assumption becomes a stated limitation, which is fine.

| question | our working assumption |
|---|---|
| Which field is "visits"? `UniqueVisits*` is 99.9% empty. | `HouseholdsReg`. It is a parameter in `config.py`, so a different answer is a one-line change. |
| Q7: which site types are in the August actuals? All 87 counties? Hennepin and Ramsey whole or split? | All site types, 87 whole counties. Our code supports the split via `county_split_label`. |
| Q7: what is the scoring metric, the submission format, and is the forecast due before the presentation? | A percentage-error style metric, so small counties matter disproportionately. |
| Is July 2026 final, or still receiving late entries? | Slightly incomplete — 489 reporting sites, 2.8% below the trailing average. |
| Presentation length, Q&A length, slide limits, who the judges are. | 10–20 minutes plus Q&A, judged by Food Group staff. |

---

## Standing rules

1. **Raw data is read-only.** All cleaning happens in `src/clean_data.py`. No
   hand-edited Excel, ever. A hand edit is a number nobody can reproduce.
2. **One canonical panel.** Everyone reads `data/processed/`. If you need a change to
   the panel, it goes in `clean_data.py` and you tell the other two.
3. **Nothing dated August 2026 or later enters the repo.** Truncate at download, not at
   analysis time. Audited by someone who did not build the model.
4. **Every public source gets a registry row** before it is used: publisher, exact
   series, geographic grain, time grain, why this one. Four facts, required by the brief.
5. **Baselines before models.** Anything complex must beat a simple baseline in a
   backtest, or earn its place in the story some other way.
6. **Every number on a slide traces to a script we wrote.** AI tools are permitted, and
   we use them, but a number we cannot derive and explain does not go on a slide.
7. **State limitations ourselves.** The household proxy for visits, county-is-site-location,
   the Atlas vintage. Better from us in minute three than from a judge in minute twelve.

---

## Presentation shape

One story, not six reports. Each question gets **one chart and one takeaway**; everything
else goes in an appendix for Q&A.

Close on the brief's own four decisions, because those are what the audience actually
does on Monday morning:

1. how to allocate resources,
2. where new food shelves are needed,
3. how to argue for a policy,
4. how to measure its own results.

The strongest single fact we currently have: **counties with a higher food-insecurity
rate serve fewer households per food-insecure person** (Spearman −0.26 to −0.29 in 2024),
and **Wilkin County has no reporting food shelf at all**. That is the brief's thesis,
demonstrated in The Food Group's own data, and it is a good opening.
