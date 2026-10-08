import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_28/training_1.csv", index_col=0)

df_merged = pd.merge(df1, df0, on="Store", how="inner")

df_merged["StoreType"] = df_merged["StoreType"].astype(str)
df_merged["Store"] = pd.to_numeric(df_merged["Store"], errors='coerce').astype("Int64")
df_merged["Dept"] = pd.to_numeric(df_merged["Dept"], errors='coerce').astype("Int64")
df_merged["Weekly_Sales"] = pd.to_numeric(df_merged["Weekly_Sales"], errors='coerce').astype("Int64")
df_merged["IsHoliday"] = df_merged["IsHoliday"].astype(bool).astype("Int64")
df_merged["Assortment"] = df_merged["Assortment"].astype(str).map({'a':0,'b':1,'c':2}).astype("Int64")
df_merged["CompetitionDistance"] = pd.to_numeric(df_merged["CompetitionDistance"], errors='coerce').astype("Int64")
df_merged["CompetitionOpenSinceMonth"] = pd.to_numeric(df_merged["CompetitionOpenSinceMonth"], errors='coerce').astype("Int64")
df_merged["CompetitionOpenSinceYear"] = pd.to_numeric(df_merged["CompetitionOpenSinceYear"], errors='coerce').astype("Int64")
df_merged["Promo2"] = pd.to_numeric(df_merged["Promo2"], errors='coerce').astype("Int64")
df_merged["Promo2SinceWeek"] = pd.to_numeric(df_merged["Promo2SinceWeek"], errors='coerce').astype("Int64")
df_merged["Promo2SinceYear"] = pd.to_numeric(df_merged["Promo2SinceYear"], errors='coerce').astype("Int64")

def promo_interval_to_int(x):
    if pd.isna(x):
        return pd.NA
    mapping = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sept":9, "Oct":10, "Nov":11, "Dec":12}
    parts = str(x).split(",")
    # Return the smallest month number in the interval string as integer
    months = [mapping.get(p.strip()[:3], pd.NA) for p in parts if p.strip()[:3] in mapping]
    months = [m for m in months if m is not pd.NA]
    if months:
        return min(months)
    return pd.NA

df_merged["PromoInterval"] = df_merged["PromoInterval"].apply(promo_interval_to_int).astype("Int64")

result = df_merged[[
    "StoreType", "Store", "Dept", "Weekly_Sales", "IsHoliday", "Assortment",
    "CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear",
    "Promo2", "Promo2SinceWeek", "Promo2SinceYear", "PromoInterval"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_28/target_multisource_mcts.csv", index=False)