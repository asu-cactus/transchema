import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

join_01 = pd.merge(s0, s1, on="WarID", suffixes=('_0', '_1'))
join_013 = pd.merge(join_01, s3, on="WarID", suffixes=('', '_3'))

union_2 = s2.copy()

final_join = pd.merge(union_2, join_013, on="WarID", how="inner", suffixes=('_2', ''))

df = final_join[["IsIntervention", "WarID", "WarShortName_0", "WarType_0", "IsInternational"]].copy()

df.rename(columns={"WarShortName_0": "WarShortName", "WarType_0": "WarType"}, inplace=True)

df = df.groupby(["IsIntervention", "WarID", "WarShortName", "WarType", "IsInternational"], as_index=False).size()

df.rename(columns={"size": "count"}, inplace=True)

df = df.drop(columns=["count"])

df = df.astype({
    "IsIntervention": "Int64",
    "WarID": "Int64",
    "WarShortName": "Int64",
    "WarType": "Int64",
    "IsInternational": "Int64"
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)