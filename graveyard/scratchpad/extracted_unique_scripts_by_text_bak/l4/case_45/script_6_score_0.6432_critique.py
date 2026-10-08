import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# Join s0 and s1 on WarID
join_0_1 = pd.merge(s0, s1, on="WarID", how="outer", suffixes=('_0', '_1'))

# Since s0 and s1 have same schema, but different data, merging on WarID will produce duplicates or NaNs.
# Instead, we should UNION s0 and s1 first, then join with s2 and s3.

union_0_1 = pd.concat([s0, s1], ignore_index=True)

# Join union_0_1 with s2 on WarID
join_2 = pd.merge(union_0_1, s2[["WarID", "IsIntervention"]], on="WarID", how="left")

# Join the above with s3 on WarID
join_3 = pd.merge(join_2, s3[["WarID", "IsInternational"]], on="WarID", how="left")

# Group by WarType and aggregate
final = join_3.groupby("WarType").agg(
    WarID=("WarID", "count"),
    WarShortName=("WarShortName", pd.Series.nunique),
    IsInternational=("IsInternational", "sum"),
    IsIntervention=("IsIntervention", "sum")
).reset_index()

# Cast columns to Int64 (nullable integer)
final = final.astype({
    "WarType": "Int64",
    "WarID": "Int64",
    "WarShortName": "Int64",
    "IsInternational": "Int64",
    "IsIntervention": "Int64"
})

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)