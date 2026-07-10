import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="WarNum", suffixes=("", "_y"))

df_joined["PolityName"] = df_joined["SideA"].fillna(df_joined["SideB"])
df_joined["WarID"] = df_joined["WarNum"].astype(int)
df_joined["PolityID"] = 0

def coalesce_int(cols):
    for c in cols:
        if c in df_joined.columns and df_joined[c].notna().any():
            return df_joined[c].fillna(0).astype(int)
    return pd.Series([0]*len(df_joined))

df_joined["StartMonth"] = coalesce_int(["StartMonth1", "StartMonth2"])
df_joined["StartDay"] = coalesce_int(["StartDay1", "StartDay2"])
df_joined["StartYear"] = coalesce_int(["StartYear1", "StartYear2"])
df_joined["EndMonth"] = coalesce_int(["EndMonth1", "EndMonth2"])
df_joined["EndDay"] = coalesce_int(["EndDay1", "EndDay2"])
df_joined["EndYear"] = coalesce_int(["EndYear1", "EndYear2"])

# Initiator and Outcome: map string initiator to integer if possible, else 0
def to_int_or_zero(x):
    try:
        return int(x)
    except:
        return 0

df_joined["Initiator"] = df_joined["Initiator"].apply(to_int_or_zero)
df_joined["Outcome"] = df_joined["Outcome"].apply(to_int_or_zero)

# Deaths: sum of SideADeaths and SideBDeaths, fill NaN with 0
df_joined["SideADeaths"] = pd.to_numeric(df_joined["SideADeaths"], errors='coerce').fillna(0).astype(int)
df_joined["SideBDeaths"] = pd.to_numeric(df_joined["SideBDeaths"], errors='coerce').fillna(0).astype(int)
df_joined["Deaths"] = df_joined["SideADeaths"] + df_joined["SideBDeaths"]

result = df_joined[["PolityName", "WarID", "PolityID", "StartMonth", "StartDay", "StartYear",
                    "EndMonth", "EndDay", "EndYear", "Initiator", "Outcome", "Deaths"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)