# roster.py — naya roster banao, garmi ke hisaab se
# PuLP optimiser hai, nahi chala to simple rule se kaam hoga
import pandas as pd

# din ke time slot — kaunsa thanda, kaunsa garam
SLOTS = [
    {"slot": "06-08", "cool": True},
    {"slot": "08-11", "cool": True},
    {"slot": "11-12", "cool": False},
    {"slot": "12-16", "cool": False},  # break time, koi kaam nahi
    {"slot": "16-18", "cool": True},
    {"slot": "18-20", "cool": True},
]

# purana roster — pehle jaisa hota tha (galat wala, demo)
def old_roster(tasks_df):
    # purana roster: subah 8 se shaam 5, dopahar me bhi bhaari kaam
    rows = []
    for _, t in tasks_df.iterrows():
        rows.append({
            "task": t["task"],
            "work_type": t["work_type"],
            "time": "08:00-17:00",
            "hours": t["hours"],
            "note": "dopahar me bhi kaam — galat",
        })
    return pd.DataFrame(rows)


# simple rule se naya roster banao (PuLP nahi chala to ye chalega)
def rule_roster(tasks_df):
    # bhaari kaam thande slot me daalo, halka kaam garam slot me bhi chalega
    rows = []
    # bhaari kaam pehle lo
    heavy = tasks_df[tasks_df["work_type"] == "heavy"]
    light = tasks_df[tasks_df["work_type"] == "light"]
    # bhaari kaam subah 06-11 me daalo
    for _, t in heavy.iterrows():
        rows.append({
            "task": t["task"],
            "work_type": t["work_type"],
            "time": "06:00-11:00",
            "hours": t["hours"],
            "note": "bhaari kaam thande time me",
        })
    # halka kaam 11-12 aur 16-20 me daalo
    for _, t in light.iterrows():
        rows.append({
            "task": t["task"],
            "work_type": t["work_type"],
            "time": "11:00-12:00, 16:00-20:00",
            "hours": t["hours"],
            "note": "halka kaam, break ke baad",
        })
    # break ka row bhi daalo
    rows.append({
        "task": "BREAK — 12:00-16:00",
        "work_type": "break",
        "time": "12:00-16:00",
        "hours": 4,
        "note": "sabko break + paani, dihaadi poori",
    })
    return pd.DataFrame(rows)


# PuLP se optimiser chalao
def pulp_roster(tasks_df):
    # PuLP import karo
    import pulp
    # problem banao — heavy kaam garam slot me kam se kam ho
    prob = pulp.LpProblem("roster", pulp.LpMinimize)
    # slot list banao (break wala slot nahi)
    slots = ["06-08", "08-11", "11-12", "16-18", "18-20"]
    # har task, har slot ke liye ghante wala variable banao
    x = {}
    blocked = set()
    for _, t in tasks_df.iterrows():
        for s in slots:
            # bhaari kaam 11-12 me nahi hoga
            if t["work_type"] == "heavy" and s == "11-12":
                blocked.add((t["task"], s))
            else:
                x[(t["task"], s)] = pulp.LpVariable(
                    f"x_{t['task']}_{s}".replace(" ", "_").replace("-", "_"),
                    lowBound=0, cat="Integer")
    # target: 11-12 wale ghante kam se kam ho (garam time)
    # sirf halka kaam hi 11-12 me ja sakta hai, isiliye wahi gino
    prob += pulp.lpSum([x[(t["task"], "11-12")] for _, t in tasks_df.iterrows()
                        if (t["task"], "11-12") not in blocked])
    # har task ke ghante poore hone chahiye
    for _, t in tasks_df.iterrows():
        prob += pulp.lpSum([x[(t["task"], s)] for s in slots
                            if (t["task"], s) not in blocked]) == t["hours"]
    # solve karo
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    # result nikalo
    rows = []
    for _, t in tasks_df.iterrows():
        # kis slot me kitne ghante mile
        parts = []
        for s in slots:
            # blocked slot me 0 ghante
            if (t["task"], s) in blocked:
                continue
            v = x[(t["task"], s)]
            # number nikalo
            val = int(pulp.value(v) or 0)
            if val > 0:
                parts.append(f"{s} ({val}h)")
        # ek line banao
        note = "bhaari kaam thande time me" if t["work_type"] == "heavy" else "halka kaam"
        rows.append({"task": t["task"], "work_type": t["work_type"],
                     "time": ", ".join(parts), "hours": t["hours"], "note": note})
    # break ka row daalo
    rows.append({"task": "BREAK — 12:00-16:00", "work_type": "break",
                 "time": "12:00-16:00", "hours": 4,
                 "note": "sabko break + paani, dihaadi poori"})
    return pd.DataFrame(rows)


# naya roster banao — pehle PuLP, nahi chala to rule
def new_roster(tasks_df):
    try:
        # PuLP try karo
        return pulp_roster(tasks_df)
    except Exception:
        # nahi chala to rule se banao
        return rule_roster(tasks_df)


# purana vs naya — kya badla, ek line me
def what_changed(old_df, new_df):
    # dopahar me bhaari kaam kitne ghante tha, pehle aur ab
    old_heavy_hot = "08:00-17:00 me dopahar 12-16 bhi kaam tha"
    new_heavy_hot = "bhaari kaam 06-11 aur 16-20 me, 12-16 break"
    return [
        "Pehle: " + old_heavy_hot,
        "Ab: " + new_heavy_hot,
        "Dihaadi: poori milegi, break ka time kaata nahi jayega",
    ]
