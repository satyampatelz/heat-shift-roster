# wbgt.py — garmi (WBGT) nikaalne ka code
# simple student style, ek line me ek step
import math
import pandas as pd


# wet bulb temp nikalo (Stull formula, simple wala)
def wet_bulb(temp_c, humidity):
    # temp aur nami se wet bulb nikalte hain
    tw = temp_c * math.atan(0.151977 * math.sqrt(humidity + 8.313659))
    tw = tw + math.atan(temp_c + humidity) - math.atan(humidity - 1.676331)
    tw = tw + 0.00391838 * (humidity ** 1.5) * math.atan(0.023101 * humidity)
    tw = tw - 4.686035
    return round(tw, 2)


# globe temp nikalo (dhoop se garam hota hai, simple approx)
def globe_temp(temp_c, solar):
    # dhoop zyada ho to globe temp zyada hota hai
    return round(temp_c + solar * 0.02, 2)


# WBGT nikalo — asli formula: 0.7 wet bulb + 0.2 globe + 0.1 air temp
def wbgt(temp_c, humidity, solar):
    # pehle wet bulb nikalo
    tw = wet_bulb(temp_c, humidity)
    # phir globe temp nikalo
    tg = globe_temp(temp_c, solar)
    # ab WBGT jodo
    value = 0.7 * tw + 0.2 * tg + 0.1 * temp_c
    return round(value, 2)


# live forecast se WBGT andaza lagao — temp, nami, dhoop, hawa se
def est_wbgt(temp_c, humidity, solar, wind):
    # pehle wet bulb nikalo
    tw = wet_bulb(temp_c, humidity)
    # dhoop se globe temp upar jata hai, hawa se kam hota hai
    if solar > 0:
        lift = min(14, solar / 55) * (1 if wind < 2 else 0.72)
    else:
        lift = 0
    tg = temp_c + lift
    # WBGT jodo
    value = 0.7 * tw + 0.2 * tg + 0.1 * temp_c
    return round(value, 2)


# ek ghante ke liye kya karna hai — break, ya bhaari kaam band?
def hour_action(wbgt_value, work_type):
    # bhaari kaam ho aur WBGT 32 se upar ho to band karo
    if work_type == "heavy" and wbgt_value > 32:
        return "STOP HEAVY"
    # bhaari kaam ho aur WBGT 28 se upar ho to break do
    if work_type == "heavy" and wbgt_value > 28:
        return "BREAK"
    # halka kaam ho aur WBGT 30 se upar ho to break do
    if work_type == "light" and wbgt_value > 30:
        return "BREAK"
    # nahi to kaam chalega
    return "WORK"


# ek din ka data lo, har ghante ka action batao
def day_summary(df_day):
    # khaali list banao
    rows = []
    # har ghante ke liye
    for _, row in df_day.iterrows():
        # bhaari kaam ka action nikalo
        heavy = hour_action(row["wbgt_c"], "heavy")
        # halka kaam ka action nikalo
        light = hour_action(row["wbgt_c"], "light")
        # list me daalo
        rows.append({
            "hour": pd.to_datetime(row["time"]).hour,
            "temp_c": row["temp_c"],
            "wbgt_c": row["wbgt_c"],
            "heavy": heavy,
            "light": light,
        })
    # table banao
    return pd.DataFrame(rows)
