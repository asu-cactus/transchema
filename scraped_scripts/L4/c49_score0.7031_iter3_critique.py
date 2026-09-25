import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

# PolityName: coalesce SideA and SideB
df0["PolityName"] = df0["SideA"].fillna(df0["SideB"])

# WarID: WarNum as int
df0["WarID"] = df0["WarNum"].astype(int)

# PolityID: constant 0
df0["PolityID"] = 0

def coalesce_int(cols, df):
    for c in cols:
        if c in df.columns and df[c].notna().any():
            return df[c].fillna(0).astype(int)
    return pd.Series([0]*len(df))

df0["StartMonth"] = coalesce_int(["StartMonth1", "StartMonth2"], df0)
df0["StartDay"] = coalesce_int(["StartDay1", "StartDay2"], df0)
df0["StartYear"] = coalesce_int(["StartYear1", "StartYear2"], df0)
df0["EndMonth"] = coalesce_int(["EndMonth1", "EndMonth2"], df0)
df0["EndDay"] = coalesce_int(["EndDay1", "EndDay2"], df0)
df0["EndYear"] = coalesce_int(["EndYear1", "EndYear2"], df0)

def to_int_or_zero(x):
    try:
        return int(x)
    except:
        return 0

df0["Initiator"] = df0["Initiator"].apply(to_int_or_zero)
df0["Outcome"] = df0["Outcome"].apply(to_int_or_zero)

df0["SideADeaths"] = pd.to_numeric(df0["SideADeaths"], errors='coerce').fillna(0).astype(int)
df0["SideBDeaths"] = pd.to_numeric(df0["SideBDeaths"], errors='coerce').fillna(0).astype(int)
df0["Deaths"] = df0["SideADeaths"] + df0["SideBDeaths"]

group_cols = ["PolityName", "WarID", "PolityID", "StartMonth", "StartDay", "StartYear",
              "EndMonth", "EndDay", "EndYear", "Initiator", "Outcome"]

result = df0.groupby(group_cols, dropna=False, as_index=False).agg({"Deaths": "sum"})

# Ensure column order and types exactly as target schema
result = result[["PolityName", "WarID", "PolityID", "StartMonth", "StartDay", "StartYear",
                 "EndMonth", "EndDay", "EndYear", "Initiator", "Outcome", "Deaths"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)