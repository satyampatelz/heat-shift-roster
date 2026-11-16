# sitefile.py — apni site ki file padho (CSV ya Excel)
# header se padhta hai — column kisi bhi order me ho, naam se milta hai
# purani positional file bhi chalegi (bina header ke)
import csv
import io

import pandas as pd

# sample — upload wale panel me yehi dikhta hai
SAMPLE_WORKERS = [
    {"name": "Imran Ansari", "age": 36, "work_type": "heavy",
     "experience": "experienced", "daily_wage_rs": 650, "heat_illness": False},
    {"name": "Bhola Ram", "age": 54, "work_type": "heavy",
     "experience": "experienced", "daily_wage_rs": 700, "heat_illness": True},
    {"name": "Chandan Kumar", "age": 26, "work_type": "light",
     "experience": "new", "daily_wage_rs": 550, "heat_illness": False},
    {"name": "Gopal Singh", "age": 41, "work_type": "light",
     "experience": "experienced", "daily_wage_rs": 600, "heat_illness": False},
]
SAMPLE_TASKS = [
    {"task": "Concrete pouring", "work_type": "heavy", "hours": 4},
    {"task": "Brick laying", "work_type": "heavy", "hours": 4},
    {"task": "Plaster", "work_type": "light", "hours": 3},
    {"task": "Painting", "work_type": "light", "hours": 2},
]

# header ke naam — ek hi cheez ke alag-alag naam
W_ALIAS = {
    "name": ["name", "worker name", "worker", "full name"],
    "age": ["age"],
    "type": ["work type", "type", "worktype", "worker type"],
    "exp": ["experience", "exp"],
    "wage": ["daily wage", "wage", "wages", "daily wages", "wage per day",
             "daily wage rs", "wage rs", "salary", "daily salary"],
    "heat": ["heat illness before", "heat illness", "illness before",
             "past heat illness", "heat illness history", "illness"],
}
T_ALIAS = {
    "name": ["task name", "task", "name", "work name", "work"],
    "type": ["work type", "type", "worktype", "task type"],
    "hours": ["hours", "hour", "hrs", "duration", "duration hours",
              "hours needed"],
}


# number banao — "36" ya "36.0" dono chalenge
def to_int(value, default=None):
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default


# heavy ya light — light likha ho to light, nahi to heavy
def norm_type(value):
    v = str(value or "").strip().lower()
    return "light" if v in ("light", "l") else "heavy"


# new ya experienced — new likha ho to new, nahi to experienced
def norm_exp(value):
    v = str(value or "").strip().lower()
    return "new" if v in ("new", "n") else "experienced"


# heat illness — yes/haan to True, no/na to False, pata na chale to None
def norm_illness(value):
    v = str(value or "").strip().lower()
    if not v:
        return None
    if v in ("haan", "ha", "yes", "y", "true", "1", "हाँ", "हां", "हा"):
        return True
    if v in ("na", "no", "n", "false", "0", "न", "नहीं", "nahi", "naa"):
        return False
    if v.startswith("haan") or v.startswith("yes"):
        return True
    if v.startswith("na"):
        return False
    return None


# header ko saaf karo — chhota karo, sirf akshar rakho
def norm_head(value):
    v = str(value or "").lower()
    v = "".join(ch if ch.isalnum() or ch == " " else " " for ch in v)
    return " ".join(v.split())


# header row se column ka map banao — naam se, order se nahi
def match_header(cells, alias):
    found = {}
    hits = 0
    for i, cell in enumerate(cells):
        h = norm_head(cell)
        if not h:
            continue
        for field, names in alias.items():
            if field not in found and h in names:
                found[field] = i
                hits += 1
                break
    # kam se kam 2 column mile aur naam wala column ho — tabhi header hai
    if hits >= 2 and "name" in found:
        return found
    return None


# CSV text ko rows me todo — quotes bhi sambhalta hai
def parse_csv_text(text):
    text = str(text or "").lstrip("\ufeff")
    rows = list(csv.reader(io.StringIO(text)))
    rows = [r for r in rows if "".join(r).strip() != ""]
    return rows


# rows se workers aur tasks nikalo — header wala ya positional, dono
def parse_site_rows(rows, fallback_name="My site"):
    name = fallback_name
    crew = []
    task_types = []
    task_hours = []
    task_names = []
    bad = 0
    w_map = None
    t_map = None
    section = "worker"
    for r in rows:
        # har cell ko string banao, khaali jagah hatao
        cells = [str(x if x is not None else "").strip() for x in r]
        first = cells[0].lower() if cells else ""
        # khaali ya # wali line chhodo
        if not first or first.startswith("#"):
            continue
        # Site wali line — site ka naam lo
        if first == "site":
            if len(cells) > 1 and cells[1]:
                name = cells[1]
            continue
        kind = None
        body = cells
        if first == "worker":
            kind = "worker"
            body = cells[1:]
        elif first == "task":
            kind = "task"
            body = cells[1:]
        # header row hai kya? naam se map banao
        if kind == "task":
            m = match_header(body, T_ALIAS)
            if m:
                t_map = m
                section = "task"
                continue
        elif kind == "worker":
            m = match_header(body, W_ALIAS)
            if m:
                w_map = m
                section = "worker"
                continue
        else:
            m = match_header(body, W_ALIAS)
            if m:
                w_map = m
                section = "worker"
                continue
            m = match_header(body, T_ALIAS)
            if m:
                t_map = m
                section = "task"
                continue
        if kind is None:
            kind = section
        # task wali row
        if kind == "task":
            if t_map:
                tname = body[t_map["name"]] if t_map["name"] < len(body) else ""
                hrs = to_int(body[t_map["hours"]]) if t_map["hours"] < len(body) else None
                tval = norm_type(body[t_map["type"]]) if "type" in t_map and t_map["type"] < len(body) else "heavy"
            else:
                tname = body[0] if body else ""
                tval = norm_type(body[1]) if len(body) > 1 else "heavy"
                hrs = to_int(body[2]) if len(body) > 2 else None
            if tname and hrs is not None and 1 <= hrs <= 10 and len(task_types) < 20:
                task_types.append(tval)
                task_hours.append(hrs)
                task_names.append(tname)
            elif tname:
                bad += 1
            continue
        # worker wali row
        if w_map:
            wname = body[w_map["name"]] if w_map["name"] < len(body) else ""
            age = to_int(body[w_map["age"]]) if w_map["age"] < len(body) else None
            wtype = norm_type(body[w_map["type"]]) if "type" in w_map and w_map["type"] < len(body) else "heavy"
            wexp = norm_exp(body[w_map["exp"]]) if "exp" in w_map and w_map["exp"] < len(body) else "experienced"
            wage = None
            if "wage" in w_map and w_map["wage"] < len(body):
                wage = to_int("".join(ch for ch in body[w_map["wage"]] if ch.isdigit()))
            heat = norm_illness(body[w_map["heat"]]) if "heat" in w_map and w_map["heat"] < len(body) else None
        else:
            wname = body[0] if body else ""
            age = to_int(body[1]) if len(body) > 1 else None
            wtype = norm_type(body[2]) if len(body) > 2 else "heavy"
            wexp = norm_exp(body[3]) if len(body) > 3 else "experienced"
            wage = to_int(body[4]) if len(body) > 4 else None
            heat = norm_illness(body[5]) if len(body) > 5 else None
            if heat is None and len(body) > 4:
                heat = norm_illness(body[4])
                if heat is not None:
                    wage = None
        if wname and age is not None and 14 <= age <= 80 and len(crew) < 200:
            crew.append({
                "name": wname, "age": age, "work_type": wtype,
                "experience": wexp,
                "daily_wage_rs": wage if (wage and 100 <= wage <= 5000) else 600,
                "heat_illness": heat is True,
            })
        elif wname:
            bad += 1
    return {"name": name, "crew": crew, "task_types": task_types,
            "task_hours": task_hours, "task_names": task_names, "bad": bad}


# file padho — CSV ya Excel, naam se site ka naam bhi lo
def read_site_file(filename, data):
    # file ka naam saaf karo — site ka naam banega
    base = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").strip()
    fallback = base or "My site"
    low = filename.lower()
    if low.endswith((".xlsx", ".xls")):
        # Excel padho — pehli sheet, bina header ke
        df = pd.read_excel(io.BytesIO(data), header=None, dtype=str)
        df = df.fillna("")
        rows = df.values.tolist()
    else:
        # CSV padho
        text = data.decode("utf-8-sig", errors="replace")
        rows = parse_csv_text(text)
    return parse_site_rows(rows, fallback)
