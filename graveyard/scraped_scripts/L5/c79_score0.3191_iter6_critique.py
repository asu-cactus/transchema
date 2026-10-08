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

# Count distinct PolityName per group
# PolityName is string in source, target expects integer count of distinct PolityName

agg = df.groupby(["Initiator", "WarID"]).agg(
    PolityName=("PolityName", lambda x: x.nunique(dropna=True)),
    StartYear=("StartYear", "min"),
    StartMonth=("StartMonth", "min"),
    StartDay=("StartDay", "min"),
    EndYear=("EndYear", "max"),
    EndMonth=("EndMonth", "max"),
    EndDay=("EndDay", "max"),
    Outcome=("Outcome", "max"),
    Deaths=("Deaths", "sum")
).reset_index()

# Convert columns to Int64 dtype to allow NA integers
agg = agg.astype({
    "WarID": "Int64",
    "PolityName": "Int64",
    "StartYear": "Int64",
    "StartMonth": "Int64",
    "StartDay": "Int64",
    "EndYear": "Int64",
    "EndMonth": "Int64",
    "EndDay": "Int64",
    "Outcome": "Int64",
    "Deaths": "Int64"
})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)