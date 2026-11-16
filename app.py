# app.py — Heat-Shift Roster app (Streamlit)
# premium, classic, clean — top company jaisa, koi faltu nahi
# English + Hindi dono — upar se language badlo
import os
import sys
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# src folder ko path me daalo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from wbgt import day_summary
from forecast import train_and_check
from risk import score_workers
from roster import old_roster, new_roster, what_changed
from pdf_log import make_pdf

# ---------------- language — dono bhasha ke lafz ----------------
TEXT = {
    "en": {
        "title": "Heat-Shift Roster",
        "sub": "Construction roster, rebuilt daily around real heat (WBGT) — with pay protection and compliance log.",
        "site": "Site", "date": "Date", "lang": "Language",
        "kpi_max": "Max WBGT", "kpi_noon": "WBGT at 12:00",
        "kpi_high": "High-risk workers", "kpi_moved": "Heavy hours moved to cool time",
        "chart": "Heat through the day (WBGT)",
        "old": "Old roster", "new": "New roster — heat-safe",
        "risk": "Worker risk list",
        "brief": "Morning brief",
        "brief_hi": "Hindi brief",
        "brief_en": "English brief",
        "pdf": "Download compliance PDF",
        "changed": "What changed",
        "demo": "Demo site — weather is real (Patna, May–June 2024), site and workers are demo.",
        "mae": "Forecast accuracy (MAE, next-day WBGT)",
        "footer": "Not medical advice. If a worker feels unwell, see a doctor.",
        "name": "Name", "age": "Age", "type": "Work", "exp": "Experience",
        "score": "Score", "risk_col": "Risk",
        "heavy": "Heavy", "light": "Light",
    },
    "hi": {
        "title": "Heat-Shift Roster",
        "sub": "Construction roster, har din asli garmi (WBGT) ke hisaab se dobara — dihaadi protected, compliance log ke saath.",
        "site": "Site", "date": "Tarikh", "lang": "Bhasha",
        "kpi_max": "Max WBGT", "kpi_noon": "12 baje WBGT",
        "kpi_high": "Zyada risk wale worker", "kpi_moved": "Bhaari kaam thande time me gaya",
        "chart": "Din bhar ki garmi (WBGT)",
        "old": "Purana roster", "new": "Naya roster — garmi se safe",
        "risk": "Worker risk list",
        "brief": "Subah ka brief",
        "brief_hi": "Hindi brief",
        "brief_en": "English brief",
        "pdf": "Compliance PDF download karo",
        "changed": "Kya badla",
        "demo": "Demo site hai — mausam asli hai (Patna, May–June 2024), site aur worker demo hain.",
        "mae": "Forecast kitna sahi hai (MAE, kal ka WBGT)",
        "footer": "Ye medical advice nahi hai. Tabiyat kharab ho to doctor ko dikhao.",
        "name": "Naam", "age": "Umar", "type": "Kaam", "exp": "Experience",
        "score": "Score", "risk_col": "Risk",
        "heavy": "Bhaari", "light": "Halka",
    },
}

# ---------------- premium look — clean, classic, no chapri colour ----------------
st.set_page_config(page_title="Heat-Shift Roster", layout="wide")
st.markdown("""
<style>
  .block-container { max-width: 1080px; padding-top: 2rem; }
  h1 { font-size: 2rem; font-weight: 700; color: #1e293b; letter-spacing: -0.5px; }
  h2 { font-size: 1.2rem; font-weight: 600; color: #1e293b; margin-top: 2rem; }
  h3 { font-size: 1rem; font-weight: 600; color: #334155; }
  p, li { color: #475569; }
  hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }
  .kpi { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
         padding: 1rem 1.2rem; }
  .kpi .num { font-size: 1.6rem; font-weight: 700; color: #1e3a5f; }
  .kpi .lbl { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
  .brief-box { background: #f8fafc; border-left: 3px solid #1e3a5f;
               border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin-bottom: 1rem; }
  .stButton>button { background: #1e3a5f; color: white; border-radius: 6px;
                     border: none; padding: 0.5rem 1.5rem; }
  .stDownloadButton>button { background: #1e3a5f; color: white; border-radius: 6px;
                            border: none; padding: 0.5rem 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ---------------- data load karo ----------------
BASE = os.path.dirname(__file__)
weather = pd.read_csv(os.path.join(BASE, "data", "patna_weather_2024_may_june.csv"))
weather["time"] = pd.to_datetime(weather["time"])
workers = pd.read_csv(os.path.join(BASE, "data", "workers.csv"))
tasks = pd.read_csv(os.path.join(BASE, "data", "tasks.csv"))

# ---------------- upar: title + language ----------------
col_t, col_l = st.columns([4, 1])
with col_l:
    lang_pick = st.radio("Language / Bhasha", ["English", "Hindi"], horizontal=True, label_visibility="collapsed")
lang = "en" if lang_pick == "English" else "hi"
T = TEXT[lang]

with col_t:
    st.title(T["title"])
    st.write(T["sub"])
    st.caption(T["demo"])

st.markdown("---")

# ---------------- date aur site chunno ----------------
c1, c2 = st.columns(2)
with c1:
    dates = sorted(weather["time"].dt.date.unique())
    picked = st.selectbox(T["date"], dates, index=dates.index(pd.to_datetime("2024-05-29").date()))
with c2:
    site = st.selectbox(T["site"], ["Patna Bypass Road Site-1 (Demo)"])

# us din ka data nikalo
day = weather[weather["time"].dt.date == picked].copy()
summary = day_summary(day)
wbgt_max = float(day["wbgt_c"].max())
noon = day[day["time"].dt.hour == 12]
wbgt_noon = float(noon["wbgt_c"].values[0]) if len(noon) else wbgt_max

# risk nikalo
risk_df = score_workers(workers, wbgt_max)
high_names = risk_df[risk_df["risk"] == "High"]["name"].tolist()

# roster banao
old = old_roster(tasks)
new = new_roster(tasks)
# bhaari kaam kitne ghante thande time me gaya
heavy_hours = int(tasks[tasks["work_type"] == "heavy"]["hours"].sum())

# ---------------- KPI cards — sirf 4 number, koi faltu nahi ----------------
k1, k2, k3, k4 = st.columns(4)
for col, num, lbl in [
    (k1, f"{wbgt_max:.1f} °C", T["kpi_max"]),
    (k2, f"{wbgt_noon:.1f} °C", T["kpi_noon"]),
    (k3, str(len(high_names)), T["kpi_high"]),
    (k4, f"{heavy_hours} h", T["kpi_moved"]),
]:
    with col:
        st.markdown(f'<div class="kpi"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

# ---------------- WBGT graph — simple, elegant ----------------
st.markdown(f"## {T['chart']}")
fig, ax = plt.subplots(figsize=(9, 3.2))
ax.plot(summary["hour"], summary["wbgt_c"], color="#1e3a5f", linewidth=2)
ax.axhline(28, color="#94a3b8", linestyle="--", linewidth=1)
ax.axhline(32, color="#b91c1c", linestyle="--", linewidth=1)
ax.text(6.2, 28.5, "28 — heavy break", fontsize=8, color="#64748b")
ax.text(6.2, 32.5, "32 — heavy stop", fontsize=8, color="#b91c1c")
ax.fill_between(summary["hour"], summary["wbgt_c"], 20, color="#1e3a5f", alpha=0.05)
ax.set_xlabel("Hour of day" if lang == "en" else "Din ka ghanta")
ax.set_ylabel("WBGT (°C)")
ax.set_xlim(0, 23)
ax.grid(color="#e2e8f0", linewidth=0.6)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
st.pyplot(fig)

# ---------------- purana vs naya roster ----------------
st.markdown(f"## {T['old']}  /  {T['new']}")
r1, r2 = st.columns(2)
with r1:
    st.dataframe(old, hide_index=True, use_container_width=True)
with r2:
    st.dataframe(new, hide_index=True, use_container_width=True)

# kya badla
st.markdown(f"### {T['changed']}")
for line in what_changed(old, new):
    st.write("- " + line)

# ---------------- risk list ----------------
st.markdown(f"## {T['risk']}")
show = risk_df[["name", "age", "work_type", "experience", "score", "risk"]].copy()
show.columns = [T["name"], T["age"], T["type"], T["exp"], T["score"], T["risk_col"]]
st.dataframe(show, hide_index=True, use_container_width=True)

# ---------------- morning brief — Hindi + English dono ----------------
st.markdown(f"## {T['brief']}")
hindi_text = (
    f"Aaj {picked} ko dopahar me garmi zyada hai (WBGT {wbgt_max:.1f} C). "
    "Bhaari kaam subah 6-11 aur shaam 4-8 me karo. "
    "Dopahar 12-4 break lo, paani piyo. "
    "Dihaadi poori milegi, break ka time kaata nahi jayega."
)
english_text = (
    f"Today {picked}, heat is high in the afternoon (WBGT {wbgt_max:.1f} C). "
    "Do heavy work in the morning 6-11 and evening 4-8. "
    "Take a break 12-4, drink water. "
    "Full day wage will be paid, break time will not be cut."
)
st.markdown(f'<div class="brief-box"><b>{T["brief_hi"]}</b><br>{hindi_text}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="brief-box"><b>{T["brief_en"]}</b><br>{english_text}</div>', unsafe_allow_html=True)

# ---------------- forecast accuracy — sach wala MAE (ek baar train, phir cache) ----------------
@st.cache_resource
def get_mae():
    _, mae, _ = train_and_check(os.path.join(BASE, "data", "patna_weather_2024_may_june.csv"))
    return mae


st.caption(f"{T['mae']}: {get_mae():.2f} °C  (LightGBM, real Patna weather, last 7 days test)")

# ---------------- PDF download ----------------
st.markdown("---")
pdf_path = os.path.join(BASE, "compliance_log.pdf")
make_pdf(pdf_path, str(picked), site, round(wbgt_max, 1), round(wbgt_noon, 1),
         high_names, new, "Language: Hindi + English")
with open(pdf_path, "rb") as f:
    st.download_button(T["pdf"], f, file_name=f"compliance_log_{picked}.pdf",
                       mime="application/pdf")

st.caption(T["footer"])
