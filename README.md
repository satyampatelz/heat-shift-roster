# Heat-Shift Roster

**One line:** Every morning, the construction site roster is rebuilt from real heat (WBGT) — heavy work in the cool hours, full daily wage protected, with a compliance log.

## How to run

```bash
cd heat-shift-roster
pip install -r requirements.txt
streamlit run app.py
```

It opens in the browser. Change the date (default 29 May 2024 — the hottest day), change the language from the top (English / Hindi).

## What is real

- **Weather — REAL:** Patna, May–June 2024, 1,464 hourly rows (`data/patna_weather_2024_may_june.csv`). Max temp 42.6°C, max WBGT 35.22°C on 29 May 2024, 12:00. Source: Open-Meteo archive, Patna (25.6, 85.1).
- **WBGT formula — REAL:** WBGT = 0.7 × wet bulb + 0.2 × globe + 0.1 × air temp. Wet bulb uses the Stull formula, globe temp comes from solar radiation.
- **ML forecast — REAL:** LightGBM predicts next-day hourly WBGT, trained on real weather. **MAE = 0.72°C** (last 7 days test, June 2024). Not a fake score.
- **Roster optimiser — REAL:** PuLP (CBC solver). Heavy work only in cool slots (06–11, 16–20), 12–16 break, zero heavy work 11–12.
- **Risk score — RULE + ML:** Score from age + heavy/light work + new/experienced + WBGT. A RandomForest classifier is trained on rule-based labels — train accuracy is 1.0 because the labels come from rules (demo, stated honestly).

## What is demo

- **Site:** Patna Bypass Road Site-1 — demo name, not a real contractor site.
- **Workers:** 25 workers, names and ages are demo. No real health data (privacy).
- **Tasks:** 8 demo tasks. Roster and risk run on this demo data.

## What is in the app

1. WBGT graph — heat through the day, with 28 and 32 lines
2. Old vs new roster — side by side
3. Worker risk list — High / Medium / Low
4. Morning brief — Hindi + English
5. Compliance PDF download — Hindi first, English below (OSH Code log)

## Interview story

"I rebuilt a construction site roster around heat. I took WBGT from real Patna weather (1,464 rows), predicted tomorrow's heat with LightGBM (MAE 0.72°C), moved heavy work to cool hours with a PuLP optimiser, kept the full daily wage, and built an OSH Code compliance PDF. The demo is on the 29 May 2024 heatwave — WBGT was 35.22°C that day."

## Note

This is not medical advice. See a doctor if you feel unwell.
