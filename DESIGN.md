# Heat-Shift Roster — Deep Design, 16 Nov 2026
Sat ne bola: deep nahi hai, bahut kuch missing lag raha hai.
Ye file woh missing cheezein bhar deti hai. Kuch banaya nahi hai — sirf design hai.

## 1 line
Har subah construction site ka roster kal ki asli garmi (WBGT) ke hisaab se dobara bane — bhaari kaam thande ghante me, dihaadi protected, compliance log ke saath.

## Problem — asli, bada
- 2024 me heat se $194B aur 247B labour hours gaye; 1,832 heat deaths (India).
- Construction worker dopahar me bhaari kaam karta hai, garmi me girta hai, site rukti hai, company ko nuksaan.
- Garmi har saal badh rahi hai — ye long-term problem hai, ek saal ka nahi.

## Government — kyun ye real hai
- OSH Code 21 Nov 2025 se LAGU hai, Rules 8 May 2026 — BoCW employer ko work-rest cycle DENA HI HOGA.
- Maharashtra SOP Apr 2026: 6-11am / 4-8pm kaam, 12-4pm break.
- Iska matlab: company ko karna hi hoga, isiliye payer hai. Ye kanoon ka tailwind hai, sirf achhi idea nahi.
- Inspector ko dated log chahiye — wo log ye app banata hai.

## WBGT — garmi kaise naapein (missing tha)
- WBGT sirf temperature nahi hai. Isme 4 cheez aati hai: hawa ka temperature, nami (humidity), hawa ki speed, dhoop (solar radiation).
- Formula: WBGT = 0.7 x Wet Bulb + 0.2 x Globe Temp + 0.1 x Air Temp. Outdoor me ye standard hai.
- Threshold (kaam ki bhari-pan ke hisaab se):
  - Halka kaam: WBGT 30 se upar ho to break badhao
  - Bhaari kaam: WBGT 28 se upar ho to break badhao, 32 se upar ho to dopahar me bhaari kaam band
- Data: IMD / Open-Meteo se free mausam (temp, humidity, wind, solar). History ke liye ERA5 / IMD gridded data.
- Har ghante ka WBGT nikalo, sirf din ka max nahi — subah 6 baje alag, dopahar 2 baje alag.

## Input — kya chahiye (missing tha)
1. Site: naam, jagah (Patna demo), kitne workers, kaunsi shift
2. Kaam list: kaam kya hai, bhaari/halka, kitne ghante, kispe depend karta hai, deadline kab hai
3. Worker: age, kaam type, pehle ki tabiyat, naye hai ya purane (acclimatization), PPE kya pehna hai
4. Mausam: kal + aane wale 3 din ka forecast
- Worker ki health data sensitive hai — naam + age + kaam type bas, bimari ka detail nahi. Privacy ka khayal rakhna hai.

## ML — 3 jagah, asli wali (missing tha)
### 1. Garmi forecast — LightGBM
- Kaam: Kal + 3 din ka WBGT predict karo, har ghante ka.
- Input: pichle 7 din ka mausam, mausam ka trend, jagah, mahina.
- Output: P10 / P50 / P90 — matlab best, normal, worst case.
- Check: MAE se naapo, kitna galat hua. Agar forecast galat ho to roster galat hoga — isiliye ye zaroori hai.
### 2. Worker risk score — LightGBM / Random Forest
- Kaam: Kaun worker zyada risk me hai, score 0-100.
- Input: age, kaam bhaari/halka, pichle din kitne ghante dhoop me, naye hai ya purane, pehle koi incident hua ya nahi.
- Output: Low / Medium / High. High wale ko dopahar me mat lagao, halka kaam do.
- Check: Precision / Recall — High risk wale ko miss mat karo.
### 3. Smart roster seekhna
- Kaam: Pichle roster se seekho, kaunsa schedule best raha.
- Input: pichla roster, us din ki garmi, kitna kaam hua, koi incident hua ya nahi.
- Output: Har hafte model thoda aur smart — kaunsa kaam kis ghante me best hota hai.
- Ye Phase 2 hai, pehle din se nahi. Pehle rule + optimiser se shuru karo.

## Roster optimiser — kaam kaise badlein
- Optimiser ka kaam: bhaari kaam thande ghante me daalo, halka kaam garam ghante me, break 12-4pm.
- Rules jo todne nahi hain:
  - Deadline wala kaam pehle, par garmi me nahi
  - Ek kaam dusre pe depend karta hai to order mat bigado
  - Crew size kam mat karo, dihaadi mat kaato
  - Har worker ko din me kam se kam 2 break + paani ka time
- Tool: PuLP / OR-Tools se optimiser. Objective: safety pehle, phir kaam pura ho, phir cost kam.
- Output: Naya roster, purana roster se kya badla, kyun badla — ek line me wajah.

## Pay protection — dihaadi kaise bachegi (missing tha)
- Worker ko dopahar me break milega, par dihaadi poori milegi. Ye likh ke do.
- Kaise: Break ka time kaam ke ghante me gino, alag se kaatna mat. Roster me saaf dikhao — "Aaj 8 ghante kaam, 1 ghante break, dihaadi poori".
- Payroll ke liye: Ek line export — worker, date, ghante, dihaadi, break. Contractor ko ye file milegi.

## Hindi brief + alert (missing tha)
- Har subah Hindi me brief: "Aaj dopahar 2-4 garmi zyada hai, bhaari kaam subah karo, paani piyo, break lo."
- Voice: Hindi TTS se audio banao, site manager WhatsApp pe bhej de.
- Alert: Agar WBGT 32 se upar jaye to turant alert — "Abhi bhaari kaam roko, chhaya me jao."

## Compliance log — inspector ko kya milega (missing tha)
- Har din ka PDF log: date, site, WBGT har ghante, roster kya tha, break kab diye, kis worker ko high risk pe halka kaam diya, kisne approve kiya.
- Log me date + time + signature jaisa record rahe. Yehi OSH Code ka proof hai.
- Data 1 saal tak save rahe, SQLite me.

## App — kya dikhega
- Streamlit dashboard: Kal ka WBGT graph, roster table (purana vs naya), risk list, compliance PDF download.
- Manager ko 1 page me sab dikhe: aaj kya badla, kyun badla, kitna kaam hoga.
- Mobile pe khulna chahiye, site pe laptop nahi hota.

## Demo — kaise dikhayein (missing tha)
- Site: Patna, ek construction site (naam nakli, roster nakli).
- Mausam: 2024 heatwave ka asli data — May-June 2024, Patna.
- Before / After: Pehle wala roster (dopahar me bhaari kaam) vs naya roster (subah bhaari kaam). Compare karo — kitne ghante garmi me kam hue, kitne incident kam honge, kaam kitna pura hoga.
- Video: Sat apni awaaz me 5 min demo — "Ye dekho, dopahar me WBGT 33 tha, humne kaam subah kar diya, dihaadi poori mili."

## Business — paisa kaise aayega (missing tha)
- Payer: site manager / contractor, kal ka roster aaj set karta hai.
- Price: ₹1,999–4,999 / site / month. Ek site pe 20-50 worker hote hain, ek worker ki dihaadi ₹500-800 hai — ek din ka incident bhi isse zyada kharcha hai.
- Trial: 1 site pe 2 hafte free, phir paid.
- Risk: Contractor slow buyer hota hai, turant nahi kharidega. Isiliye demo + compliance log pehle dikhao, sale baad me.
- Long-term: Ek site se 10 site, ek sheher se dusre sheher, phir government dashboard.

## Tech stack
- Python, Pandas, NumPy — data saaf karo
- LightGBM — forecast + risk score
- PuLP / OR-Tools — roster optimiser
- Streamlit — dashboard
- SQLite — log save karo
- Open-Meteo / IMD — mausam free
- Hindi TTS — voice brief

## Plan — 4 hafte, laptop se
- Week 1: Data + WBGT engine — Patna 2024 heatwave data, har ghante WBGT nikalo, threshold test karo.
- Week 2: ML forecast + risk score — LightGBM train karo, MAE / Precision check karo.
- Week 3: Roster optimiser + Hindi brief + PDF log — Streamlit app banao.
- Week 4: Demo + test — Before/After compare karo, video demo banao, README likho.

## Risks — sach baat (missing tha)
- Mausam forecast galat ho sakta hai — isiliye P10/P50/P90 do, aur real-time alert rakho.
- Contractor turant nahi kharidega — demo pehle, sale baad me.
- Worker data sensitive hai — naam + age bas, bimari ka detail mat lo.
- Ye medical advice nahi hai — doctor ki jagah nahi lega, ye likhna hoga.
- Demo me site nakli hai, mausam asli hai — README me saaf likhna hoga.

## Interview me kya bolega — Sat ki kahani
- "Maine construction site ka roster garmi ke hisaab se dobara banaya, ML se forecast + risk score, OSH Code ka compliance log banaya. 2024 heatwave pe test kiya."
- Skills dikhenge: Python, Pandas, LightGBM, PuLP, SQL, Streamlit, Hindi product.
- Yehi woh project hai jisme company bolegi "tum mere paas kaam karo" — kyunki problem real hai, kanoon real hai, demo real mausam pe hai.

## Kya abhi bhi missing hai
- Asli site ka roster — abhi tak koi real contractor nahi hai, demo synthetic roster pe hai.
- Asli worker ka data — privacy ke wajah se abhi tak nahi hai, demo me dummy worker hain.
- Ye dono Phase 2 me aayenge, jab pehla demo ban jaye.
