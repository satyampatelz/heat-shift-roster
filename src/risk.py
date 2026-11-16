# risk.py — worker ka risk score nikalo
# rule + ML classifier, dono simple
# NOTE: worker data DEMO hai, asli incident data nahi hai
# isiliye classifier rule se bane label pe train hota hai — ye demo hai, sach likha hai
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# garmi ke point — WBGT se seedha, har degree pe badhta hai
def heat_points(wbgt_max):
    # 20 se upar har degree pe 1.7 point, max 30
    h = round((wbgt_max - 20) * 1.7)
    if h < 0:
        return 0
    if h > 30:
        return 30
    return h


# rule se score nikalo — 0 se 100
def rule_score(age, work_type, experience, wbgt_max, ill=False):
    # shuru me 0
    score = 0
    # umar zyada ho to risk zyada
    if age >= 50:
        score = score + 30
    elif age >= 40:
        score = score + 15
    # bhaari kaam ho to risk zyada
    if work_type == "heavy":
        score = score + 25
    # naya worker ho to risk zyada (garmi ki aadat nahi)
    if experience == "new":
        score = score + 20
    # garmi zyada ho to risk zyada — har degree pe point
    score = score + heat_points(wbgt_max)
    # pehle garmi se beemar hua ho to hamesha High risk
    if ill:
        score = max(score, 80)
    # 100 se zyada mat karo
    return min(score, 100)


# score se Low / Medium / High banao
def risk_band(score):
    # 60 se upar High
    if score >= 60:
        return "High"
    # 35 se upar Medium
    if score >= 35:
        return "Medium"
    # nahi to Low
    return "Low"


# saare workers ka risk nikalo
def score_workers(workers_df, wbgt_max):
    # copy banao
    df = workers_df.copy()
    # heat illness wala column ho to lo, nahi to sab False
    if "heat_illness" not in df.columns:
        df["heat_illness"] = False
    # har worker ka score nikalo
    df["score"] = df.apply(
        lambda r: rule_score(r["age"], r["work_type"], r["experience"],
                             wbgt_max, bool(r["heat_illness"])),
        axis=1)
    # band nikalo
    df["risk"] = df["score"].apply(risk_band)
    # zyada risk pehle dikhao
    df = df.sort_values("score", ascending=False)
    return df


# ML classifier — rule wale label pe train hota hai (demo only)
def train_risk_model(workers_df, wbgt_max):
    # pehle rule se label banao
    df = score_workers(workers_df, wbgt_max)
    # feature banao: umar, bhaari=1/halka=0, naya=1/purana=0
    X = pd.DataFrame({
        "age": df["age"],
        "heavy": (df["work_type"] == "heavy").astype(int),
        "new": (df["experience"] == "new").astype(int),
        "wbgt_max": wbgt_max,
    })
    # label banao: High=2, Medium=1, Low=0
    y = df["risk"].map({"Low": 0, "Medium": 1, "High": 2})
    # model banao
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    # train karo (chhota demo data hai, isiliye accuracy zyada aayegi — sach hai)
    model.fit(X, y)
    # train pe hi check karo
    pred = model.predict(X)
    acc = accuracy_score(y, pred)
    return model, round(float(acc), 2)
