import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

agg = df.groupby("Initiator").agg(
    WarID=("WarID", "count"),
    Deaths=("Deaths", "sum"),
    Outcome=("Outcome", "max"),
    StartYear=("StartYear", "min"),
    EndYear=("EndYear", "max")
).reset_index()

agg["PolityName"] = pd.NA
agg["StartMonth"] = pd.NA
agg["StartDay"] = pd.NA
agg["EndMonth"] = pd.NA
agg["EndDay"] = pd.NA

agg = agg[[
    "Initiator", "WarID", "PolityName", "StartYear", "StartMonth", "StartDay",
    "EndYear", "EndMonth", "EndDay", "Outcome", "Deaths"
]]

agg["WarID"] = agg["WarID"].astype("Int64")
agg["PolityName"] = agg["PolityName"].astype("Int64")
agg["StartYear"] = agg["StartYear"].astype("Int64")
agg["StartMonth"] = agg["StartMonth"].astype("Int64")
agg["StartDay"] = agg["StartDay"].astype("Int64")
agg["EndYear"] = agg["EndYear"].astype("Int64")
agg["EndMonth"] = agg["EndMonth"].astype("Int64")
agg["EndDay"] = agg["EndDay"].astype("Int64")
agg["Outcome"] = agg["Outcome"].astype("Int64")
agg["Deaths"] = agg["Deaths"].astype("Int64")

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)