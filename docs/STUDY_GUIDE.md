# Study guide for Saturday

Written 16 October 2026 for Valentino, Dhyan and Uddam. Not for judges.

How to use it: answer in writing, without the notebooks open, two to four sentences each.
The point is the reasoning, not the number. If you cannot explain why we did something,
that is the thing to go read before Saturday. Send your answers back and they get graded
against what the scripts and notebooks actually say, with the gaps pointed out.

Judges were told on Thursday to interrupt, to push on why each data source was chosen, and
to check that we own every decision rather than "the AI said so". The questions below are
the ones that push does.

---

## Part A. Everyone answers these

1. Define need and demand the way the challenge glossary does. Then say which of our
   numbers measures which, and what "latent demand" and "unmet demand" are.
2. Why do we say "recorded activity" and not "demand" or "need" when we talk about the
   three metrics? Give one case where recorded activity would understate demand.
3. A judge says: "Your per-resident chart shows no relationship. Doesn't that just mean the
   Feeding America numbers are wrong?" Answer in a way that defends neither side.
4. Which public sources did we add beyond the ones the organizers gave us? Pick one you
   did not download yourself and say why that one and not the obvious alternative.
5. What is the one rule in the brief with a stated penalty, and name two concrete things
   we did in the repository to make sure we followed it.
6. If a judge asks "what did AI do in this project", what is your answer? Be specific
   about what was yours.
7. For your own question, name one limitation you would say before a judge asks.
8. What is the one sentence the whole deck is arguing? Say it from memory.
9. Why is the March 2023 step on Dhyan's slide and not on the food-prices side of the
   story? What two things do Q4 and Q5 agree on about it?
10. The Food Group can act on three things from our work. What are they, and which
    finding backs each one?

---

## Part B. Valentino (Q1, Q6, pipeline)

1. In raw counts the slope is 1.15 to 1.24, and per 1,000 residents the correlation is
   about zero. Explain to someone who has never run a regression why both are true at
   the same time.
2. Why fit log of activity on log of food-insecure persons? What does a slope above 1
   mean in words, and what would a slope of exactly 1 have meant?
3. We say the four county characteristics "explain 3% and none is clearly associated".
   Why not "they have no effect"? What does the interval around distance tell you?
4. "The residual partly measures the network." What does that mean, what number backs
   it, and why should the Food Group read the Q1 ranking with that in mind?
5. Cook County: what did we find about where its pounds come from, and why does that
   matter for any site-level analysis?
6. State the need definition from memory. What makes it falsifiable? What evidence would
   make you reject it, and what would make you revise the index instead?
7. What rule decided which inputs went into the index? Why are distance and rurality out,
   and why is poverty out?
8. Why equal weights? How did you check that the ranking does not hinge on that choice,
   and what did the check show?
9. What was the Wilkin prediction, when was it written, and why does it count as a test?
   What would you have done if it had landed at the 30th percentile?
10. Read this aloud in plain words: "no-internet +0.41 SD per SD, p = 0.005". Then give the
    caveat about no-internet also being on the need side, with the number.
11. "County size explains 85% of activity; neither measure of need adds more than a
    point." What model produced that, and what does it NOT say about need?
12. The three maps: what does each show, what does rank 1 mean, why is Wilkin hatched, and
    why are the two need maps alike while the activity map is not?
13. Moran's I and the join counts: what question were they answering and what did we
    conclude? Why did we run more than one test?
14. Our index and Feeding America correlate 0.77 and differ on five of the top ten. Where
    does each find need, and why is that difference useful rather than a problem?
15. Timeliness: a judge says Feeding America lags two years, so what does your index gain?
    Give the honest answer.

---

## Part C. Dhyan (Q4, Q5)

Start with these five. They are the ones that went wrong this week, and a judge who reads
the error bars on the lag chart will ask them.

- C0a. Read the lag chart out loud, metric by metric: which bars clear zero, and which do
  not? Give the p-values for lag 1, lag 2 and lag 4 in households.
- C0b. Why can you not say "households respond at month four"? What exactly does an error
  bar that crosses zero mean?
- C0c. A rise at lag 1 and a fall at lag 2, with a six-month sum of about zero. In one
  sentence, what does that pattern mean for The Food Group?
- C0d. Your notebook prints "+367% per 1% price change". What is wrong with that number,
  and what is the right one?
- C0e. The March 2023 step is 19%. February to March is a seasonal rise every year. How do
  you know the 19% is not just the spring rise? Give the numbers for the other years.
- C0f. Your appendix slide used to say March 2023 was "the largest single move". Which
  other month-to-month step in the series is the same size, and what is the honest
  wording?
- C0g. The lag model has 46 months, not 47. Which month is missing from the CPI series,
  why, and how would you answer a judge who asks about it?
- C0h. Say the one sentence about food prices that is on your slide, from memory, and
  then the one sentence about SNAP. Then say which number backs each.

1. Why work in changes rather than levels when relating prices to activity? What goes
   wrong with levels?
2. Why the Midwest food-at-home CPI and not the national or the Minneapolis series? What
   does "one series for all counties" mean for what you are allowed to claim?
3. What does the lag-1 bar mean? Why do you say the price effect is "small and late"
   rather than "prices drive demand"?
4. Why are month-of-year effects not optional in this model? What would the lag
   estimates look like without them?
5. How do you know the March 2023 step is not a price effect?
6. Describe the event study in plain words: what are unit and month fixed effects doing,
   what is "exposure", and what is the interaction term testing?
7. "Exposure does not predict a larger rise (p = 0.42 and 0.33)." What does that say about
   substitution between SNAP and food shelves, and what does it not say?
8. The 19% step and the 30% county jump are both on our slides. Why are both right, and
   which claim does each one back?
9. Why cluster the errors on the reporting unit?
10. Pounds per household fell from 62 to 50. Give two different explanations and say
    which one the data can tell apart.
11. The month-effects figure: evaluated at mean exposure. Why did that matter, and what
    did the first version of the figure get wrong?
12. Where does each number on your slide come from? If a judge asks you to reproduce one,
    what do you run?
13. What is the SNAP timeline we are using (last extra payment, first regular-only month)
    and where did we verify it?

---

## Part D. Uddam (Q7, Q8)

Two things that were wrong in the 16 October upload, so start here:

- D0a. The slide said "7.9 miles to the nearest SNAP grocery". No table has that number.
  The retail comparison gives 10.0 miles for large SNAP groceries and 5.9 for all SNAP
  stores. Where did 7.9 come from, and which number belongs on the slide with what
  label?
- D0b. After Wilkin was set to zero, the statewide sums changed. Give the new households,
  pounds and individuals totals, and say why the growth-versus-2025 figures all moved
  by a tenth of a point.

1. Why six simple methods rather than one complex model? What do you say to "why not
   ARIMA or a machine-learning model"?
2. Explain the pooled May-to-July ratio in words. What does "shrunk toward the statewide
   ratio" do, and why does it help small counties?
3. How was the backtest built so that no fold could see its own future? Why three
   Augusts and not one?
4. Why RMSE to pick the method? What does RMSE reward, and which counties dominate it?
5. Wilkin is submitted as zeros. Why, and what do you say to "isn't that giving up"?
6. Hennepin and Anoka: what is the issue with the July 2026 base, and what did we decide?
7. Where do the intervals come from, and what is their weakness?
8. The leakage audit: what four things does it check, who ran it, and why does it matter
   that it was not you?
9. What is a LILA tract? Which USDA variant did you use, and what changes if you pick
   another?
10. Why population-weighted distances rather than tract counts? Why straight-line miles?
11. The 2010 to 2020 tract crosswalk: what is the problem, how did you handle it, and
    what is the magnitude of the ambiguity?
12. "Fill or repeat": what evidence says the network repeats the retail gap, and what
    would "fill" have looked like in the numbers?
13. Why does the grocery distance change when you count more retailer types, and what
    does that do to the conclusion?
14. 402 sites in Q8, 462 in Q1 and Q6. Why do they differ, and does it change anything?
15. Site locations are tract interior points. What is the displacement bound, and why
    does it matter more in rural tracts?
16. Why does being within five miles not prove access? Name three things proximity does
    not capture.

---

## Part E. Curveballs

Judges are told to knock you off balance. Have an answer for each.

1. "If the Food Group could act on only one number from your work, which one?"
2. "What is the weakest part of your analysis?"
3. "What would you do with one more month?"
4. "You used the same word, activity, for three different metrics. Which one should the
   Food Group care about?"
5. "Your index says Nobles has high need. What should the Food Group actually do in
   Nobles on Monday?"
6. "Why should I believe a definition of need that you wrote before looking at data?"
7. "Your forecast is only one month out. What is it good for?"
8. "You cited Feeding America. What exactly did you take from it, and what did you not?"

---

## Part F. Facts to have cold (from the 16 October review)

Not answers to the questions above. These are the sentences each of us must be able to
say without notes, because a judge who reads our own charts will ask for them.

### Dhyan

- Lag model, monthly changes, lags 0 to 6 in one model, month effects, HAC errors,
  46 months (October 2025 CPI was never published).
- Lag 1: households +3.7% (p = 0.040), pounds +7.0% (p < 0.001), individuals +7.7%
  (p < 0.001). Lag 2: households −6.9% (p = 0.012), individuals −4.0% (p = 0.020),
  pounds not significant (p = 0.287). Lag 4 households +7.3% is NOT significant
  (p = 0.085). Sum over six months not different from zero for any metric.
- The sentence: a price rise moves visits earlier rather than adding them.
- The notebook's "+367% per 1% price change" multiplies by 100 twice. The right number
  is 3.7%. Never say the big one.
- March 2023 step: +0.176 log = +19.3% with unit and month effects; median unit +18.9%;
  90% of 78 units rose; state total +20.3%. February to March in the other years is
  −4.2%, −1.2%, +3.6%, +8.6%, so the excess is +17.4%. Not the spring rise.
- Exposure coefficients 0.013 and −0.009, p = 0.42 and 0.33: counties with more people on
  SNAP did not rise more.
- Not "the largest single move": June 2022 is the same size. Say "one of the largest, and
  the only one that lines up with a dated policy change".
- Why Midwest CPI: the finest monthly series covering all of Minnesota; the metro series
  is bimonthly. Why MN DHS: the only county-level monthly SNAP series.

### Uddam

- Statewide forecast with Wilkin at zero: 241,906 households, 12.85 million pounds,
  745,851 individuals (263,933 children, 394,512 adults, 87,406 seniors). Growth versus
  August 2025: +2.0%, +0.9%, +3.8%.
- Wilkin: no reporting food shelf since 2022, so zeros, not a guess.
- Rural LILA distances: 8.0 miles to a food shelf, 9.2 to an OpenStreetMap supermarket,
  10.0 to a large SNAP grocery, 5.9 counting every SNAP store. Within five miles of a
  food shelf: 98% urban LILA, 95% urban other, 55% rural other, 37% rural LILA.
- Metro-adjacent and remote rural LILA: 34% and 39% within five miles.

### Valentino

- Index vs Feeding America: Spearman 0.77. Index vs poverty: 0.76, R² 0.60. Feeding
  America vs poverty: 0.87, R² 0.80. So the index is not a poverty map; 40% of it is
  housing cost, vehicles, access and debt.
- Barriers: no internet +0.41 SD (p = 0.005), distance +0.23 SD (p = 0.025), R² 0.17.
  No internet also sits on the need side (+0.27 SD), so part of its effect is need.
- Timeliness: inputs lag about a year, Feeding America about two; the gain is months,
  the real gain is observed inputs anyone can recompute.
