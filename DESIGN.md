# Heat-Shift Roster — Deep Design, 16 Nov 2026
Sat said: it is not deep enough, a lot feels missing.
This file fills those gaps. Nothing is built here — only design.

## 1 line
Every morning, the construction site roster is rebuilt from real heat (WBGT) — heavy work in the cool hours, full daily wage protected, with a compliance log.

## Problem — real and big
- In 2024, heat cost $194B and 247B labour hours; 1,832 heat deaths (India).
- A construction worker does heavy work at noon, falls sick in the heat, the site stops, the company loses money.
- Heat rises every year — this is a long-term problem, not a one-year problem.

## Government — why this is real
- OSH Code in force from 21 Nov 2025, Rules 8 May 2026 — under BoCW, the employer MUST give a work-rest cycle.
- Maharashtra SOP Apr 2026: work 6–11am / 4–8pm, break 12–4pm.
- That means companies have to do it, so there is a payer. This is a legal tailwind, not just a good idea.
- The inspector wants a dated log — this app makes that log.

## WBGT — how to measure heat (was missing)
- WBGT is not just temperature. It takes 4 things: air temperature, humidity, wind speed, sunlight (solar radiation).
- Formula: WBGT = 0.7 x Wet Bulb + 0.2 x Globe Temp + 0.1 x Air Temp. This is the outdoor standard.
- Thresholds (by how heavy the work is):
  - Light work: if WBGT goes above 30, increase breaks
  - Heavy work: if WBGT goes above 28, increase breaks; above 32, stop heavy work at noon
- Data: free weather from IMD / Open-Meteo (temp, humidity, wind, solar). For history, ERA5 / IMD gridded data.
- Find WBGT for every hour, not just the day's max — 6am is different from 2pm.

## Input — what is needed (was missing)
1. Site: name, place (Patna demo), how many workers, which shift
2. Work list: what the work is, heavy/light, how many hours, what it depends on, deadline
3. Worker: age, work type, past health, new or experienced (acclimatization), what PPE they wear
4. Weather: tomorrow + next 3 days forecast
- Worker health data is sensitive — only name + age + work type, no illness details. Privacy matters.

## ML — 3 places, the real kind (was missing)
### 1. Heat forecast — LightGBM
- Job: predict WBGT for tomorrow + 3 days, every hour.
- Input: last 7 days of weather, weather trend, place, month.
- Output: P10 / P50 / P90 — best, normal, worst case.
- Check: measure with MAE. If the forecast is wrong, the roster is wrong — that is why this matters.
### 2. Worker risk score — LightGBM / Random Forest
- Job: score 0–100 for which worker is most at risk.
- Input: age, heavy/light work, how many hours in the sun yesterday, new or experienced, any past incident.
- Output: Low / Medium / High. Do not put High workers on noon heavy work, give them light work.
- Check: Precision / Recall — do not miss a High-risk worker.
### 3. Smart roster learning
- Job: learn from past rosters, which schedule worked best.
- Input: past roster, that day's heat, how much work got done, any incident.
- Output: every week the model gets a little smarter — which work fits which hour best.
- This is Phase 2, not day one. Start with rules + optimiser first.

## Roster optimiser — how work moves
- The optimiser's job: put heavy work in cool hours, light work in hot hours, break 12–4pm.
- Rules that must not break:
  - Deadline work first, but not in the heat
  - If one job depends on another, do not break the order
  - Do not cut crew size, do not cut daily wages
  - Every worker gets at least 2 breaks + water time per day
- Tool: PuLP / OR-Tools optimiser. Goal: safety first, then finish the work, then lower cost.
- Output: new roster, what changed from the old roster, why it changed — in one line.

## Pay protection — how the daily wage is saved (was missing)
- The worker gets a noon break, but the full daily wage. Give this in writing.
- How: count break time inside work hours, do not cut it separately. Show it clearly in the roster — "Today 8 hours work, 1 hour break, full daily wage".
- For payroll: a one-line export — worker, date, hours, wage, break. The contractor gets this file.

## Hindi brief + alert (was missing)
- Every morning a brief in Hindi: "Today 2–4pm heat is high, do heavy work in the morning, drink water, take breaks."
- Voice: make audio with Hindi TTS, the site manager sends it on WhatsApp.
- Alert: if WBGT goes above 32, alert at once — "Stop heavy work now, go to shade."

## Compliance log — what the inspector gets (was missing)
- A daily PDF log: date, site, WBGT every hour, what the roster was, when breaks were given, which high-risk worker got light work, who approved it.
- The log must keep date + time + a signature-like record. This is the proof for the OSH Code.
- Data stays saved for 1 year, in SQLite.

## App — what it shows
- Streamlit dashboard: tomorrow's WBGT graph, roster table (old vs new), risk list, compliance PDF download.
- The manager sees everything on 1 page: what changed today, why it changed, how much work will get done.
- It must open on mobile — there is no laptop on site.

## Demo — how to show it (was missing)
- Site: Patna, one construction site (fake name, fake roster).
- Weather: real data from the 2024 heatwave — May–June 2024, Patna.
- Before / After: old roster (heavy work at noon) vs new roster (heavy work in the morning). Compare — how many hot hours were cut, how many incidents would drop, how much work gets done.
- Video: Sat does a 5-min demo in his own voice — "See, at noon WBGT was 33, we moved the work to the morning, full wage was paid."

## Business — how money comes in (was missing)
- Payer: site manager / contractor, who sets tomorrow's roster today.
- Price: ₹1,999–4,999 / site / month. One site has 20–50 workers, one worker's daily wage is ₹500–800 — even one day's incident costs more than this.
- Trial: 2 weeks free on 1 site, then paid.
- Risk: a contractor is a slow buyer, he will not buy at once. So show the demo + compliance log first, sell later.
- Long-term: from 1 site to 10 sites, from one city to another, then a government dashboard.

## Tech stack
- Python, Pandas, NumPy — clean the data
- LightGBM — forecast + risk score
- PuLP / OR-Tools — roster optimiser
- Streamlit — dashboard
- SQLite — save the log
- Open-Meteo / IMD — free weather
- Hindi TTS — voice brief

## Plan — 4 weeks, from a laptop
- Week 1: Data + WBGT engine — Patna 2024 heatwave data, find WBGT every hour, test thresholds.
- Week 2: ML forecast + risk score — train LightGBM, check MAE / Precision.
- Week 3: Roster optimiser + Hindi brief + PDF log — build the Streamlit app.
- Week 4: Demo + test — compare Before/After, make the video demo, write the README.

## Risks — the honest truth (was missing)
- The weather forecast can be wrong — that is why we give P10/P50/P90, and keep real-time alerts.
- The contractor will not buy at once — demo first, sale later.
- Worker data is sensitive — only name + age, no illness details.
- This is not medical advice — it cannot replace a doctor, this must be written.
- In the demo the site is fake, the weather is real — the README must say this clearly.

## Interview story — Sat's story
- "I rebuilt a construction site roster around heat, with ML forecast + risk score, and an OSH Code compliance log. I tested it on the 2024 heatwave."
- Skills it shows: Python, Pandas, LightGBM, PuLP, SQL, Streamlit, Hindi product.
- This is the project where a company says "come work for me" — because the problem is real, the law is real, and the demo runs on real weather.

## What is still missing
- A real site roster — there is no real contractor yet, the demo runs on a synthetic roster.
- Real worker data — not there yet because of privacy, the demo has dummy workers.
- Both come in Phase 2, once the first demo is made.
