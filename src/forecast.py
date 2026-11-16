# forecast.py — kal ki garmi (WBGT) predict karo, LightGBM se
# data asli hai: Patna May-June 2024, 1464 hourly rows
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error


# data load karo aur features banao
def make_features(csv_path):
    # csv padho
    df = pd.read_csv(csv_path)
    # time ko date banao
    df["time"] = pd.to_datetime(df["time"])
    # ghanta nikalo
    df["hour"] = df["time"].dt.hour
    # saal ka din nikalo
    df["dayofyear"] = df["time"].dt.dayofyear
    # 24 ghante pehle ka WBGT nikalo (lag feature)
    df["wbgt_lag24"] = df["wbgt_c"].shift(24)
    # 24 ghante pehle ka temp nikalo
    df["temp_lag24"] = df["temp_c"].shift(24)
    # 24 ghante pehle ki nami nikalo
    df["hum_lag24"] = df["humidity_pct"].shift(24)
    # target: 24 ghante baad ka WBGT (kal same time)
    df["target"] = df["wbgt_c"].shift(-24)
    # khaali row hatao
    df = df.dropna()
    return df


# model train karo aur MAE batao (sach wala, fake nahi)
def train_and_check(csv_path):
    # features banao
    df = make_features(csv_path)
    # feature wale column chunno
    cols = ["hour", "dayofyear", "temp_c", "humidity_pct",
            "wind_kmh", "solar_wm2", "wbgt_lag24", "temp_lag24", "hum_lag24"]
    # X aur y banao
    X = df[cols]
    y = df["target"]
    # aakhri 7 din test ke liye rakho, baaki train
    split = len(df) - 7 * 24
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    # LightGBM model banao
    import lightgbm as lgb
    model = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.05,
                              num_leaves=31, random_state=42, verbose=-1)
    # train karo
    model.fit(X_train, y_train)
    # test pe predict karo
    pred = model.predict(X_test)
    # MAE nikalo — kitna galat hua
    mae = mean_absolute_error(y_test, pred)
    return model, mae, cols


# ek din ke liye kal ka WBGT predict karo
def predict_next_day(model, cols, df_today):
    # aaj ke aakhri 24 ghante lo
    last = df_today.tail(24).copy()
    # features banao
    last["hour"] = pd.to_datetime(last["time"]).dt.hour
    last["dayofyear"] = pd.to_datetime(last["time"]).dt.dayofyear + 1
    last["wbgt_lag24"] = last["wbgt_c"]
    last["temp_lag24"] = last["temp_c"]
    last["hum_lag24"] = last["humidity_pct"]
    # predict karo
    pred = model.predict(last[cols])
    # result banao
    out = pd.DataFrame({"hour": last["hour"].values,
                        "pred_wbgt": [round(float(p), 2) for p in pred]})
    return out


if __name__ == "__main__":
    # khud chalao to MAE print hoga
    m, mae, cols = train_and_check("data/patna_weather_2024_may_june.csv")
    print("MAE (WBGT, next day):", round(mae, 2))
