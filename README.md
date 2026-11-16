# Heat-Shift Roster

**One line / Ek line:** Har subah construction site ka roster kal ki asli garmi (WBGT) ke hisaab se dobara bane — bhaari kaam thande ghante me, dihaadi protected, compliance log ke saath.

## How to run / Kaise chalao

```bash
cd heat-shift-roster
pip install -r requirements.txt
streamlit run app.py
```

Browser me khul jayega. Date badlo (default 29 May 2024 — sabse garam din), language upar se badlo (English / Hindi).

## What is real / Kya asli hai

- **Weather / Mausam — REAL:** Patna, May–June 2024, 1,464 hourly rows (`data/patna_weather_2024_may_june.csv`). Max temp 42.6°C, max WBGT 35.22°C on 29 May 2024, 12:00. Source: Open-Meteo archive, Patna (25.6, 85.1).
- **WBGT formula — REAL:** WBGT = 0.7 × wet bulb + 0.2 × globe + 0.1 × air temp. Wet bulb Stull formula se, globe temp solar se.
- **ML forecast — REAL:** LightGBM, kal ka hourly WBGT predict karta hai, real weather pe train hota hai. **MAE = 0.72°C** (last 7 days test, June 2024). Fake score nahi hai.
- **Roster optimiser — REAL:** PuLP (CBC solver). Bhaari kaam sirf thande slot me (06-11, 16-20), 12-16 break, 11-12 me bhaari kaam zero.
- **Risk score — RULE + ML:** Age + bhaari/halka + naya/purana + WBGT se score. RandomForest classifier rule wale label pe train hota hai — train accuracy 1.0 aati hai kyunki label rule se bane hain (demo hai, sach likha hai).

## What is demo / Kya demo hai

- **Site:** Patna Bypass Road Site-1 — naam demo hai, asli contractor site nahi hai.
- **Workers:** 25 workers, naam/umar demo hain. Koi real health data nahi hai (privacy).
- **Tasks:** 8 tasks demo hain. Roster aur risk usi demo data pe chalte hain.

## App me kya hai (sirf zaroori cheez)

1. WBGT graph — din bhar ki garmi, 28 aur 32 ki line ke saath
2. Purana vs naya roster — side by side
3. Worker risk list — High / Medium / Low
4. Morning brief — Hindi + English dono
5. Compliance PDF download — Hindi pehle, English neeche (OSH Code log)

## Interview story / Interview me kya bolega

"Maine construction site ka roster garmi ke hisaab se dobara banaya. Real Patna weather (1,464 rows) se WBGT nikala, LightGBM se kal ki garmi predict ki (MAE 0.72°C), PuLP optimiser se bhaari kaam thande time me daala, dihaadi poori rakhi, aur OSH Code ka compliance PDF banaya. Demo 29 May 2024 heatwave pe hai — us din WBGT 35.22°C tha."

## Note

Ye medical advice nahi hai. Tabiyat kharab ho to doctor ko dikhao.
This is not medical advice. See a doctor if you feel unwell.
