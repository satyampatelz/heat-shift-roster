# app.py — Heat-Shift Roster app (Streamlit)
# web page jaisa look — colour, location, upload
# English + Hindi dono — upar se language badlo
import os
import sys
import datetime

import pandas as pd
import requests
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# src folder ko path me daalo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from wbgt import day_summary, est_wbgt
from forecast import train_and_check
from risk import score_workers
from roster import old_roster, new_roster, what_changed, SLOTS
from pdf_log import make_pdf
from sitefile import read_site_file, SAMPLE_WORKERS, SAMPLE_TASKS

# ---------------- colours — web page wali palette ----------------
NAVY = "#173f63"
TEAL = "#0e7a6d"
TEAL_DEEP = "#0a5c51"
ORANGE = "#cf6f14"
RED = "#b3352b"
AMBER = "#96600a"
AMBER_SOLID = "#e9a13b"
GOLD = "#a07d16"
INK = "#1a2233"

# quick cities — web page wale (Patna nahi hai)
QUICK_CITIES = [
    ("Gaya", "गया", 24.7914, 85.0002),
    ("Aurangabad", "औरंगाबाद", 24.7520, 84.3742),
    ("Delhi", "दिल्ली", 28.6139, 77.2090),
    ("Bhopal", "भोपाल", 23.2599, 77.4126),
    ("Lucknow", "लखनऊ", 26.8467, 80.9462),
]

# Hindi mahine — brief me tarikh ke liye
HI_MONTHS = ["", "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
             "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
EN_MONTHS = ["", "January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]

# ---------------- language — dono bhasha ke lafz ----------------
TEXT = {
    "en": {
        "title": "Heat-Shift Roster",
        "sub": "Construction roster, rebuilt daily around real heat (WBGT) — with pay protection and compliance log.",
        "date": "Date", "lang": "Language",
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
        "step2": "Step 2 · Location",
        "loc_sub": "Search a city — live weather loads and the roster below rebuilds.",
        "mode_archive": "Archive · May–Jun 2024",
        "mode_live": "Live · any location",
        "search_ph": "Type a city — Gaya, Aurangabad, Delhi, Bhopal, Lucknow…",
        "search_btn": "Search",
        "quick": "Quick cities",
        "no_loc": "No location selected yet — search a city or tap a quick city below.",
        "fc_cap": "Next 7 days · peak WBGT",
        "live_ok": "Live weather loaded for {place} — Open-Meteo forecast. Pick a day below.",
        "live_err": "Live weather could not load. Try again.",
        "badge_high": "Extreme heat day — heavy work stops at midday",
        "badge_med": "Hot day — breaks enforced",
        "badge_low": "Moderate day — normal care",
        "heat_mark": "Past heat illness",
        "heat_note": "Heat-illness memory: {names} — marked yes, so always High risk. No heavy work at midday; light work only, in shade.",
        "honest_h": "What is real, what is demo",
        "honest_1": "Patna weather, May–June 2024 — 1,464 hourly rows, Open-Meteo.",
        "honest_2": "WBGT formula, LightGBM forecast (MAE 0.72°C), PuLP roster optimiser, risk scoring rule.",
        "honest_3": "The starter crew (25 workers, 8 tasks) until you upload your own file.",
        "current_site": "Current site",
        "demo_crew": "demo crew",
        "uploaded_file": "uploaded file",
        "demo_again": "Use demo crew again",
        "pick_day": "Pick a day",
    },
    "hi": {
        "title": "Heat-Shift Roster",
        "sub": "Construction roster, har din asli garmi (WBGT) ke hisaab se dobara — dihaadi protected, compliance log ke saath.",
        "date": "Tarikh", "lang": "Bhasha",
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
        "step2": "चरण 2 · जगह",
        "loc_sub": "शहर खोजो — लाइव मौसम लोड होगा, नीचे का रोस्टर दोबारा बनेगा।",
        "mode_archive": "अभिलेख · मई–जून 2024",
        "mode_live": "लाइव · कोई भी जगह",
        "search_ph": "शहर लिखो — गया, औरंगाबाद, दिल्ली, भोपाल, लखनऊ…",
        "search_btn": "खोजो",
        "quick": "जल्दी चुनो",
        "no_loc": "अभी कोई जगह नहीं चुनी — शहर खोजो या नीचे से चुनो।",
        "fc_cap": "अगले 7 दिन · सबसे ज़्यादा WBGT",
        "live_ok": "लाइव मौसम लोड हो गया — {place}, Open-Meteo forecast। नीचे से दिन चुनो।",
        "live_err": "लाइव मौसम लोड नहीं हुआ। फिर से कोशिश करो।",
        "badge_high": "बहुत ज़्यादा गर्मी — दोपहर में भारी काम बंद",
        "badge_med": "गर्म दिन — विश्राम ज़रूरी",
        "badge_low": "ठीक दिन — सामान्य ध्यान",
        "heat_mark": "पहले गर्मी से बीमार",
        "heat_note": "गर्मी-बीमारी की याद: {names} — yes लिखा है, इसलिए हमेशा उच्च जोखिम। दोपहर में भारी काम नहीं; सिर्फ़ हल्का काम, छाँव में।",
        "honest_h": "क्या असली है, क्या डेमो है",
        "honest_1": "पटना का मौसम, मई–जून 2024 — 1,464 घंटे की rows, Open-Meteo।",
        "honest_2": "WBGT formula, LightGBM forecast (MAE 0.72°C), PuLP roster optimiser, risk scoring rule।",
        "honest_3": "पहली crew (25 worker, 8 tasks) — जब तक अपनी file upload न करो।",
        "current_site": "Current site",
        "demo_crew": "demo crew",
        "uploaded_file": "uploaded file",
        "demo_again": "Use demo crew again",
        "pick_day": "दिन चुनो",
    },
}

# upload wala hissa — dono bhasha me English hi rehta hai
UP_H = "Step 1 · Upload your site file"
UP_SUB = "CSV or Excel — your workers and tasks. The roster below rebuilds for your site."
UP_SAMPLE_LINE = "Your file should look like this sample"
UP_SAMPLE_SUB = "Make your file exactly like the sample below — just change the names and numbers."
UP_NOTE = "Columns can be in any order — they are read by name. Work Type: heavy or light · Experience: new or experienced · Heat Illness Before: yes or no."
UP_PICK = "Choose your file"
UP_DL = "Download sample CSV"
UP_BTN = "Upload site file"

# ---------------- page look — colourful, premium ----------------
st.set_page_config(page_title="Heat-Shift Roster", layout="wide")
st.markdown("""
<style>
  .stApp {
    background:
      radial-gradient(920px 520px at 88% -6%, rgba(233,161,59,.42), rgba(233,161,59,0) 62%),
      radial-gradient(760px 560px at -12% 26%, rgba(46,191,168,.30), rgba(46,191,168,0) 62%),
      radial-gradient(980px 680px at 112% 62%, rgba(224,106,53,.26), rgba(224,106,53,0) 62%),
      radial-gradient(860px 620px at 8% 108%, rgba(214,69,65,.18), rgba(214,69,65,0) 62%),
      linear-gradient(158deg,#fdf3dc 0%,#f9e7c8 26%,#f3ecd9 48%,#e2efe6 74%,#d8ecec 100%);
    background-attachment: fixed;
  }
  header[data-testid="stHeader"] { display: none; }
  .block-container { max-width: 1080px; padding-top: 2rem; }
  h1 { font-size: 2rem; font-weight: 700; color: #1a2233; letter-spacing: -0.5px; }
  h2 { font-size: 1.2rem; font-weight: 600; color: #173f63; margin-top: 2rem; }
  h2::after { content: ""; display: block; width: 48px; height: 3px; background: #a07d16; margin-top: 4px; }
  h3 { font-size: 1rem; font-weight: 600; color: #334155; }
  p, li { color: #3d4a61; }
  hr { border: none; border-top: 1px solid #d9d2c2; margin: 1.5rem 0; }
  .hero { background: linear-gradient(128deg,#175263 0%,#143a5c 52%,#0d2438 100%);
          border-radius: 14px; padding: 1.6rem 1.8rem 1.4rem; margin-bottom: 1rem;
          box-shadow: 0 14px 32px rgba(10,20,40,.25); }
  .hero h1 { color: #ffffff; margin: 0 0 .4rem; }
  .hero p { color: #dbe7f3; margin: 0; }
  .hero .note { color: #a9c4de; font-size: .85rem; margin-top: .6rem; }
  .heatbar { height: 5px; border-radius: 3px; margin-top: 1.1rem;
             background: linear-gradient(90deg,#0e7a6d,#3fae6a,#e9a13b,#cf6f14,#b3352b); }
  .kpi { background: #ffffff; border: 1px solid #e7e2d4; border-radius: 10px;
         padding: 1rem 1.2rem; box-shadow: 0 1px 2px rgba(26,34,51,.06), 0 6px 18px rgba(26,34,51,.09); }
  .kpi .num { font-size: 1.6rem; font-weight: 700; }
  .kpi .lbl { font-size: 0.8rem; color: #68738a; text-transform: uppercase; letter-spacing: 0.5px; }
  .badge { display: inline-block; border-radius: 999px; padding: .35rem 1rem;
           font-weight: 600; font-size: .9rem; margin: .4rem 0 0; }
  .badge-high { background: #fae9e5; color: #b3352b; }
  .badge-med { background: #faf0d3; color: #96600a; }
  .badge-low { background: #e0f0ec; color: #0a5c51; }
  .brief-box { background: #ffffff; border-left: 3px solid #0e7a6d;
               border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin-bottom: 1rem;
               box-shadow: 0 1px 2px rgba(26,34,51,.06); }
  .roster-head { background: linear-gradient(90deg,#0e7a6d,#095a4f); color: #ffffff;
                 border-radius: 10px 10px 0 0; padding: .7rem 1rem; font-weight: 600; }
  .stButton>button { background: linear-gradient(135deg,#173f63,#0e7a6d); color: white;
                     border-radius: 8px; border: none; padding: .5rem 1.2rem; font-weight: 600; }
  .stDownloadButton>button { background: linear-gradient(135deg,#173f63,#0e7a6d); color: white;
                             border-radius: 8px; border: none; padding: .5rem 1.2rem; font-weight: 600; }
  /* button ka text <p> me aata hai — uska rang white rakho, nahi to dark button pe dark text dikhega */
  .stButton>button p, .stDownloadButton>button p { color: #ffffff; margin: 0; }
  .day-chip { background: #ffffff; border: 1px solid #e7e2d4; border-radius: 10px;
              padding: .6rem .4rem; text-align: center; font-size: .85rem; }
  .sun-art { text-align: center; margin-top: 2rem; opacity: .9; }
</style>
""", unsafe_allow_html=True)

# ---------------- data load karo ----------------
BASE = os.path.dirname(__file__)
weather = pd.read_csv(os.path.join(BASE, "data", "patna_weather_2024_may_june.csv"))
weather["time"] = pd.to_datetime(weather["time"])
demo_workers = pd.read_csv(os.path.join(BASE, "data", "workers.csv"))
# Santosh Mahto aur Harish Chandra — pehle garmi se beemar, hamesha High
demo_workers["heat_illness"] = demo_workers["name"].isin(["Santosh Mahto", "Harish Chandra"])
demo_tasks = pd.read_csv(os.path.join(BASE, "data", "tasks.csv"))[["task", "work_type", "hours"]]

# ---------------- session state — pehli baar khaali rakho ----------------
if "mode" not in st.session_state:
    st.session_state.mode = "archive"
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False
if "up_crew" not in st.session_state:
    st.session_state.up_crew = None
if "up_tasks" not in st.session_state:
    st.session_state.up_tasks = None
if "up_site" not in st.session_state:
    st.session_state.up_site = None
if "up_status" not in st.session_state:
    st.session_state.up_status = ""
if "up_file_name" not in st.session_state:
    st.session_state.up_file_name = ""
if "up_key" not in st.session_state:
    st.session_state.up_key = 0
if "live_place" not in st.session_state:
    st.session_state.live_place = None
if "map_lat" not in st.session_state:
    st.session_state.map_lat = None
if "map_lon" not in st.session_state:
    st.session_state.map_lon = None
if "map_last_click" not in st.session_state:
    st.session_state.map_last_click = None
if "live_wbgt" not in st.session_state:
    st.session_state.live_wbgt = {}
if "live_temp" not in st.session_state:
    st.session_state.live_temp = {}
if "live_dates" not in st.session_state:
    st.session_state.live_dates = []
if "live_date" not in st.session_state:
    st.session_state.live_date = ""
if "live_status" not in st.session_state:
    st.session_state.live_status = ""
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "risk_filter" not in st.session_state:
    st.session_state.risk_filter = "All"

# ---------------- helper — chhote kaam ----------------
def fmt_date(d, lang):
    # 29 May 2024 ya 29 मई 2024
    months = HI_MONTHS if lang == "hi" else EN_MONTHS
    return f"{d.day} {months[d.month]} {d.year}"


def cool_windows():
    # thande slot jodo — 06-11, 16-20
    wins = []
    start = None
    prev = None
    for s in SLOTS:
        if not s["cool"] or s["slot"] == "12-16":
            continue
        a, b = s["slot"].split("-")
        a, b = int(a), int(b)
        if start is None:
            start, prev = a, b
        elif a == prev:
            prev = b
        else:
            wins.append(f"{start:02d}–{prev:02d}")
            start, prev = a, b
    if start is not None:
        wins.append(f"{start:02d}–{prev:02d}")
    return ", ".join(wins)


def colour_for(w):
    # WBGT se rang — thanda teal, garam red
    if w > 32:
        return RED
    if w > 30:
        return ORANGE
    if w > 28:
        return NAVY
    return TEAL


# live forecast lao — Open-Meteo se, 7 din ka
def fetch_forecast(lat, lon):
    # forecast API bulao
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon,
              "hourly": "temperature_2m,relative_humidity_2m,shortwave_radiation,wind_speed_10m",
              "forecast_days": 7, "timezone": "auto"}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    h = r.json()["hourly"]
    # har din ke 24 ghante jodo
    wbgt_days = {}
    temp_days = {}
    for i, ts in enumerate(h["time"]):
        d = ts[:10]
        w = est_wbgt(h["temperature_2m"][i], h["relative_humidity_2m"][i],
                     h["shortwave_radiation"][i] or 0, h["wind_speed_10m"][i] or 0)
        wbgt_days.setdefault(d, []).append(w)
        temp_days.setdefault(d, []).append(h["temperature_2m"][i])
    # sirf poore 24 ghante wale din rakho
    wbgt_days = {d: v for d, v in wbgt_days.items() if len(v) == 24}
    temp_days = {d: v for d, v in temp_days.items() if len(v) == 24}
    return wbgt_days, temp_days


def pick_place(lat, lon, label):
    # jagah chuno — live weather load karo
    try:
        wbgt_days, temp_days = fetch_forecast(lat, lon)
    except Exception:
        st.session_state.live_status = "err"
        return
    if not wbgt_days:
        st.session_state.live_status = "err"
        return
    st.session_state.live_place = label
    st.session_state.map_lat = lat
    st.session_state.map_lon = lon
    st.session_state.live_wbgt = wbgt_days
    st.session_state.live_temp = temp_days
    st.session_state.live_dates = sorted(wbgt_days.keys())
    st.session_state.live_date = st.session_state.live_dates[0]
    st.session_state.live_status = "ok"
    st.session_state.search_results = []


# ---------------- upar: language + hero ----------------
col_t, col_l = st.columns([4, 1])
with col_l:
    lang_pick = st.radio("Language / Bhasha", ["English", "Hindi"], horizontal=True, label_visibility="collapsed")
lang = "en" if lang_pick == "English" else "hi"
T = TEXT[lang]

with col_t:
    st.markdown(
        f'<div class="hero"><h1>{T["title"]}</h1><p>{T["sub"]}</p>'
        f'<p class="note">{T["demo"]}</p><div class="heatbar"></div></div>',
        unsafe_allow_html=True)

# ---------------- Step 1 · Site upload ----------------
st.markdown(f"## {UP_H}")
st.write(UP_SUB)
# abhi kaunsi site hai
if st.session_state.up_site:
    site_name = st.session_state.up_site
    site_tag = T["uploaded_file"]
else:
    site_name = "Patna Bypass Road Site-1 (Demo)"
    site_tag = T["demo_crew"]
st.write(f'{T["current_site"]}: **{site_name}** ({site_tag})')

if st.button(UP_BTN):
    st.session_state.show_upload = True

if st.session_state.show_upload:
    # pehle sample dikhao, phir file chunno
    st.write(f"**{UP_SAMPLE_LINE}**")
    st.write(UP_SAMPLE_SUB)
    # sample workers table
    sw = pd.DataFrame(SAMPLE_WORKERS)
    sw["heat_illness"] = sw["heat_illness"].map({True: "yes", False: "no"})
    sw.columns = ["Name", "Age", "Work Type", "Experience", "Daily Wage", "Heat Illness Before"]
    st.dataframe(sw, hide_index=True, use_container_width=True)
    # sample tasks table
    stt = pd.DataFrame(SAMPLE_TASKS)
    stt.columns = ["Task Name", "Work Type", "Hours"]
    st.dataframe(stt, hide_index=True, use_container_width=True)
    st.caption(UP_NOTE)
    # file chunno + sample download karo
    up_file = st.file_uploader(UP_PICK, type=["csv", "xlsx", "xls"],
                               key=f"sitefile_{st.session_state.up_key}")
    with open(os.path.join(BASE, "samples", "1-sample-correct.csv"), "rb") as f:
        st.download_button(UP_DL, f, file_name="sample-site.csv", mime="text/csv")
    # demo crew wapas lao
    if st.session_state.up_site and st.button(T["demo_again"]):
        st.session_state.up_crew = None
        st.session_state.up_tasks = None
        st.session_state.up_site = None
        st.session_state.up_status = ""
        st.session_state.up_file_name = ""
        st.session_state.up_key += 1
        st.rerun()
    # file aayi to padho
    if up_file is not None and up_file.name != st.session_state.up_file_name:
        parsed = read_site_file(up_file.name, up_file.getvalue())
        st.session_state.up_file_name = up_file.name
        if not parsed["crew"]:
            st.session_state.up_status = "No workers could be read from this file. Check the format above and try again."
            st.session_state.up_crew = None
            st.session_state.up_tasks = None
            st.session_state.up_site = None
        else:
            st.session_state.up_crew = pd.DataFrame(parsed["crew"])
            if len(parsed["task_names"]) >= 2:
                st.session_state.up_tasks = pd.DataFrame({
                    "task": parsed["task_names"],
                    "work_type": parsed["task_types"],
                    "hours": parsed["task_hours"],
                })
            else:
                st.session_state.up_tasks = demo_tasks.copy()
            st.session_state.up_site = parsed["name"]
            msg = (f'Loaded "{parsed["name"]}" — {len(parsed["crew"])} workers, '
                   f'{len(st.session_state.up_tasks)} tasks. The risk list and roster below are now for this site.')
            heat_n = sum(1 for w in parsed["crew"] if w["heat_illness"])
            if heat_n > 0:
                msg += (f" {heat_n} worker(s) marked yes for past heat illness — "
                        "always High risk, no heavy work at midday.")
            if parsed["bad"] > 0:
                msg += f" {parsed['bad']} row(s) were skipped — they did not match the format."
            st.session_state.up_status = msg
    if st.session_state.up_status:
        st.success(st.session_state.up_status)

# kaunsi crew aur tasks use karni hai — upload wali ya demo
if st.session_state.up_crew is not None:
    workers = st.session_state.up_crew
else:
    workers = demo_workers
if st.session_state.up_tasks is not None:
    tasks = st.session_state.up_tasks
else:
    tasks = demo_tasks

st.markdown("---")

# ---------------- Step 2 · Location ----------------
st.markdown(f"## {T['step2']}")
st.write(T["loc_sub"])
# mode chunno — archive ya live
mode_labels = [T["mode_archive"], T["mode_live"]]
mode_pick = st.radio("Weather source", mode_labels, horizontal=True, label_visibility="collapsed",
                     index=0 if st.session_state.mode == "archive" else 1)
st.session_state.mode = "archive" if mode_pick == T["mode_archive"] else "live"

if st.session_state.mode == "archive":
    # purana data — 61 din, date chunno
    dates = sorted(weather["time"].dt.date.unique())
    picked = st.selectbox(T["date"], dates, index=dates.index(datetime.date(2024, 5, 29)))
else:
    # live mode — pehle jagah chunno
    c_search, c_btn = st.columns([4, 1])
    with c_search:
        q = st.text_input("City", placeholder=T["search_ph"], label_visibility="collapsed")
    with c_btn:
        do_search = st.button(T["search_btn"])
    if do_search and q.strip():
        try:
            r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                             params={"name": q.strip(), "count": 6, "language": "en", "format": "json"},
                             timeout=10)
            r.raise_for_status()
            st.session_state.search_results = r.json().get("results", []) or []
        except Exception:
            st.session_state.search_results = []
            st.error(T["live_err"])
    # search ke result — button dabao to jagah chunno
    for i, p in enumerate(st.session_state.search_results):
        label = f'{p["name"]}, {p.get("admin1", "")}, {p.get("country", "")}'.strip(", ")
        if st.button(label, key=f"sr_{i}"):
            pick_place(p["latitude"], p["longitude"], p["name"])
    # quick city chips
    st.write(f"**{T['quick']}**")
    chip_cols = st.columns(5)
    for i, (en_name, hi_name, lat, lon) in enumerate(QUICK_CITIES):
        with chip_cols[i]:
            if st.button(hi_name if lang == "hi" else en_name, key=f"chip_{i}"):
                pick_place(lat, lon, en_name)
    # map — tap karo to us jagah ka live weather lao
    try:
        from streamlit_folium import st_folium
        import folium
        map_ok = True
    except Exception:
        map_ok = False
    if map_ok:
        # leaflet local file se — CDN slow ho to bhi map chale; sirf leaflet chahiye
        folium.Map.default_js = [("leaflet", "/app/static/leaflet.js")]
        folium.Map.default_css = [("leaflet_css", "/app/static/leaflet.css")]
        # India centre, zoom 5
        m = folium.Map(location=[25.6, 85.1], zoom_start=5)
        # chuni hui jagah pe marker lagao
        if st.session_state.map_lat is not None:
            folium.Marker([st.session_state.map_lat, st.session_state.map_lon],
                          tooltip=st.session_state.live_place or "").add_to(m)
        out = st_folium(m, height=350, use_container_width=True, key="loc_map")
        click = out.get("last_clicked") if out else None
        if click:
            # same click dobara process mat karo
            clat, clon = round(click["lat"], 2), round(click["lng"], 2)
            if (clat, clon) != st.session_state.map_last_click:
                st.session_state.map_last_click = (clat, clon)
                pick_place(clat, clon, f"Map ({clat:.2f}, {clon:.2f})")
                st.rerun()
    else:
        st.caption("Map needs streamlit-folium — run: pip install -r requirements.txt")
    # abhi koi jagah nahi chuni
    if not st.session_state.live_dates:
        st.info(T["no_loc"])
        if st.session_state.live_status == "err":
            st.error(T["live_err"])
        st.stop()
    if st.session_state.live_status == "ok":
        st.success(T["live_ok"].replace("{place}", st.session_state.live_place))
    # agle 7 din — din chunno
    st.write(f"**{T['fc_cap']}**")
    day_cols = st.columns(7)
    for i, d in enumerate(st.session_state.live_dates):
        peak = max(st.session_state.live_wbgt[d])
        dd = datetime.date.fromisoformat(d)
        with day_cols[i]:
            st.markdown(
                f'<div class="day-chip" style="border-top: 4px solid {colour_for(peak)}">'
                f'<b>{dd.day} {EN_MONTHS[dd.month][:3]}</b><br>{peak:.1f}°C WBGT</div>',
                unsafe_allow_html=True)
    day_labels = []
    for d in st.session_state.live_dates:
        dd = datetime.date.fromisoformat(d)
        day_labels.append(f"{dd.day} {EN_MONTHS[dd.month]} — {max(st.session_state.live_wbgt[d]):.1f}°C WBGT")
    day_idx = st.selectbox(T["pick_day"], range(len(day_labels)),
                           format_func=lambda i: day_labels[i],
                           index=st.session_state.live_dates.index(st.session_state.live_date))
    st.session_state.live_date = st.session_state.live_dates[day_idx]
    picked = datetime.date.fromisoformat(st.session_state.live_date)

# ---------------- us din ka data nikalo ----------------
if st.session_state.mode == "live":
    # live forecast se — 24 ghante
    hours = list(range(24))
    wbgt_list = st.session_state.live_wbgt[st.session_state.live_date]
    temp_list = st.session_state.live_temp[st.session_state.live_date]
else:
    # archive CSV se
    day = weather[weather["time"].dt.date == picked].copy()
    summary = day_summary(day)
    hours = summary["hour"].tolist()
    wbgt_list = summary["wbgt_c"].tolist()
    temp_list = summary["temp_c"].tolist()

wbgt_max = float(max(wbgt_list))
noon = wbgt_list[12] if len(wbgt_list) > 12 else wbgt_max
tmax = float(temp_list[wbgt_list.index(wbgt_max)])

# risk nikalo
risk_df = score_workers(workers, wbgt_max)
high_names = risk_df[risk_df["risk"] == "High"]["name"].tolist()
heat_names = risk_df[risk_df["heat_illness"] == True]["name"].tolist()

# roster banao
old = old_roster(tasks)
new = new_roster(tasks)
# bhaari kaam kitne ghante thande time me gaya
heavy_hours = int(tasks[tasks["work_type"] == "heavy"]["hours"].sum())

# ---------------- KPI cards — har ek ka apna rang ----------------
k1, k2, k3, k4 = st.columns(4)
kpi_data = [
    (k1, f"{wbgt_max:.1f} °C", T["kpi_max"], RED),
    (k2, f"{noon:.1f} °C", T["kpi_noon"], AMBER),
    (k3, str(len(high_names)), T["kpi_high"], NAVY),
    (k4, f"{heavy_hours} h", T["kpi_moved"], TEAL),
]
for col, num, lbl, colour in kpi_data:
    with col:
        st.markdown(
            f'<div class="kpi" style="border-top: 4px solid {colour}">'
            f'<div class="num" style="color: {colour}">{num}</div>'
            f'<div class="lbl">{lbl}</div></div>',
            unsafe_allow_html=True)

# din kaisa hai — badge
if wbgt_max > 32:
    badge_txt, badge_cls = T["badge_high"], "badge-high"
elif wbgt_max > 28:
    badge_txt, badge_cls = T["badge_med"], "badge-med"
else:
    badge_txt, badge_cls = T["badge_low"], "badge-low"
st.markdown(f'<span class="badge {badge_cls}">{badge_txt}</span>', unsafe_allow_html=True)

# ---------------- WBGT graph — heat gradient wali line ----------------
st.markdown(f"## {T['chart']}")
fig, ax = plt.subplots(figsize=(9, 3.2))
# 32 se upar red zone, 28-32 amber zone
ax.axhspan(32, 38, color=RED, alpha=0.07)
ax.axhspan(28, 32, color=AMBER_SOLID, alpha=0.10)
# line — har ghante ka rang WBGT se
for i in range(len(hours) - 1):
    ax.plot([hours[i], hours[i + 1]], [wbgt_list[i], wbgt_list[i + 1]],
            color=colour_for(wbgt_list[i]), linewidth=2.5)
# halka warm fill neeche
ax.fill_between(hours, wbgt_list, 20, color=ORANGE, alpha=0.06)
# peak point — red dot
ax.plot([hours[wbgt_list.index(wbgt_max)]], [wbgt_max], "o", color=RED,
        markersize=8, markerfacecolor="white", markeredgewidth=2)
ax.axhline(28, color="#94a3b8", linestyle="--", linewidth=1)
ax.axhline(32, color=RED, linestyle="--", linewidth=1)
ax.text(0.5, 28.5, "28 — heavy break", fontsize=8, color="#64748b")
ax.text(0.5, 32.5, "32 — heavy stop", fontsize=8, color=RED)
ax.set_xlabel("Hour of day" if lang == "en" else "Din ka ghanta")
ax.set_ylabel("WBGT (°C)")
ax.set_xlim(0, 23)
ax.set_ylim(14, 38)
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
    # naya roster — teal band wala heading
    st.markdown(f'<div class="roster-head">{T["new"]}</div>', unsafe_allow_html=True)

    def tint_row(row):
        # bhaari copper, halka teal, break amber
        if row["work_type"] == "heavy":
            return ["background-color: #f7e3cf"] * len(row)
        if row["work_type"] == "light":
            return ["background-color: #e0f0ec"] * len(row)
        return ["background-color: #faf0d3"] * len(row)

    st.dataframe(new.style.apply(tint_row, axis=1), hide_index=True, use_container_width=True)

# kya badla
st.markdown(f"### {T['changed']}")
for line in what_changed(old, new, lang):
    st.write("- " + line)
# garmi-beemari wale worker — dopahar me bhaari kaam nahi
if heat_names:
    st.warning(T["heat_note"].replace("{names}", ", ".join(heat_names)))

# ---------------- risk list ----------------
st.markdown(f"## {T['risk']}")
# filter — All / High / Medium / Low
f_all = f"All ({len(risk_df)})"
f_high = f"High ({len(high_names)})"
f_med = f"Medium ({len(risk_df[risk_df['risk'] == 'Medium'])})"
f_low = f"Low ({len(risk_df[risk_df['risk'] == 'Low'])})"
f_pick = st.radio("Show", [f_all, f_high, f_med, f_low], horizontal=True, label_visibility="collapsed")
if f_pick == f_high:
    show = risk_df[risk_df["risk"] == "High"]
elif f_pick == f_med:
    show = risk_df[risk_df["risk"] == "Medium"]
elif f_pick == f_low:
    show = risk_df[risk_df["risk"] == "Low"]
else:
    show = risk_df
show = show[["name", "age", "work_type", "experience", "score", "risk", "heat_illness"]].copy()
show["heat_illness"] = show["heat_illness"].map({True: "⚠ yes", False: "—"})
show.columns = [T["name"], T["age"], T["type"], T["exp"], T["score"], T["risk_col"], T["heat_mark"]]


def tint_risk(row):
    # High red, Medium amber, Low teal
    risk_val = row[T["risk_col"]]
    if risk_val == "High":
        return ["background-color: #fae9e5"] * len(row)
    if risk_val == "Medium":
        return ["background-color: #faf0d3"] * len(row)
    return ["background-color: #e0f0ec"] * len(row)


st.dataframe(show.style.apply(tint_risk, axis=1), hide_index=True, use_container_width=True)

# ---------------- morning brief — Hindi + English dono ----------------
st.markdown(f"## {T['brief']}")
# bhaari kaam ke safe ghante — thande slot se
wins = cool_windows() if heavy_hours > 0 else ""
if wins:
    hi_heavy = f"भारी काम आज सिर्फ़ इन घंटों में होगा: {wins}। "
    en_heavy = f"Heavy work today only in these hours: {wins}. "
else:
    hi_heavy = "आज भारी काम के लिए कोई सुरक्षित घंटा नहीं — भारी काम कल पर, दिहाड़ी पूरी। "
    en_heavy = "No safe heavy-work hours today — heavy work deferred, full wage paid. "
hi_heat = ""
en_heat = ""
if heat_names:
    names = ", ".join(heat_names)
    hi_heat = f"गर्मी-बीमारी की याद: {names} को yes लिखा है — हमेशा उच्च जोखिम, दोपहर में भारी काम नहीं। "
    en_heat = f"Heat-illness note: {names} marked yes — always High risk, no heavy work at midday. "
hindi_text = (
    f"आज {fmt_date(picked, 'hi')} को दोपहर में गर्मी ज़्यादा है (WBGT {wbgt_max:.1f}°C, हवा {tmax:.1f}°C)। "
    f"{hi_heavy}दोपहर 12–4 विश्राम लो, पानी पियो, छाँव में बैठो। हल्का काम शाम को होगा। "
    f"ज़्यादा जोखिम वाले {len(high_names)} मज़दूर आज हल्का काम करेंगे। {hi_heat}"
    "दिहाड़ी पूरी मिलेगी — विश्राम का समय काटा नहीं जाएगा।"
)
english_text = (
    f"Today, {fmt_date(picked, 'en')}, heat peaks at midday (WBGT {wbgt_max:.1f}°C, air {tmax:.1f}°C). "
    f"{en_heavy}Take a full break 12:00–16:00 — drink water, sit in shade. Light work fills the evening. "
    f"{len(high_names)} high-risk workers do light work today. {en_heat}"
    "Full day wage will be paid; break time will not be cut."
)
st.markdown(f'<div class="brief-box"><b>{T["brief_hi"]}</b><br>{hindi_text}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="brief-box"><b>{T["brief_en"]}</b><br>{english_text}</div>', unsafe_allow_html=True)

# ---------------- forecast accuracy — sach wala MAE (ek baar train, phir cache) ----------------
@st.cache_resource
def get_mae():
    _, mae, _ = train_and_check(os.path.join(BASE, "data", "patna_weather_2024_may_june.csv"))
    return mae


st.caption(f"{T['mae']}: {get_mae():.2f} °C  (LightGBM, real Patna weather, last 7 days test)")

# ---------------- kya asli hai, kya demo hai ----------------
st.markdown(f"## {T['honest_h']}")
st.write(f"- **Real:** {T['honest_1']}")
st.write(f"- **Real:** {T['honest_2']}")
st.write(f"- **Demo:** {T['honest_3']}")

# ---------------- PDF download ----------------
st.markdown("---")
pdf_site = f"{site_name} ({site_tag})"
if st.session_state.mode == "live" and st.session_state.live_place:
    pdf_site += f" — live weather: {st.session_state.live_place}"
pdf_path = os.path.join(BASE, "compliance_log.pdf")
make_pdf(pdf_path, str(picked), pdf_site, round(wbgt_max, 1), round(noon, 1),
         high_names, new, "Language: Hindi + English", heat_names=heat_names)
with open(pdf_path, "rb") as f:
    st.download_button(T["pdf"], f, file_name=f"compliance_log_{picked}.pdf",
                       mime="application/pdf")

st.caption(T["footer"])

# ---------------- neeche — sun aur waves, decoration ----------------
st.markdown(
    '<div class="sun-art">'
    '<svg width="320" height="60" viewBox="0 0 320 60" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="160" cy="26" r="14" fill="#e9a13b"/>'
    '<g stroke="#e9a13b" stroke-width="2" stroke-linecap="round">'
    '<line x1="160" y1="4" x2="160" y2="10"/><line x1="160" y1="42" x2="160" y2="48"/>'
    '<line x1="138" y1="26" x2="144" y2="26"/><line x1="176" y1="26" x2="182" y2="26"/>'
    '<line x1="144" y1="10" x2="148" y2="14"/><line x1="172" y1="38" x2="176" y2="42"/>'
    '<line x1="176" y1="10" x2="172" y2="14"/><line x1="148" y1="38" x2="144" y2="42"/>'
    '</g>'
    '<path d="M0 52 Q 40 44 80 52 T 160 52 T 240 52 T 320 52" fill="none" stroke="#0e7a6d" stroke-width="2.5"/>'
    '<path d="M0 58 Q 40 51 80 58 T 160 58 T 240 58 T 320 58" fill="none" stroke="#cf6f14" stroke-width="2" opacity="0.7"/>'
    '</svg></div>',
    unsafe_allow_html=True)
