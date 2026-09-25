import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_0_1 = pd.concat([s0, s1], ignore_index=True)

agg = union_0_1.groupby("WarType").agg(
    WarID=("WarID", "count"),
    WarShortName=("WarShortName", pd.Series.nunique)
).reset_index()

join_2 = pd.merge(agg, s2[["WarID", "IsIntervention"]], on="WarID", how="left")

final = pd.merge(join_2, s3[["WarID", "IsInternational"]], on="WarID", how="left")

final = final[["WarType", "WarID", "WarShortName", "IsInternational", "IsIntervention"]]

final["WarType"] = final["WarType"].astype("Int64")
final["WarID"] = final["WarID"].astype("Int64")
final["WarShortName"] = final["WarShortName"].astype("Int64")
final["IsInternational"] = final["IsInternational"].fillna(0).astype("Int64")
final["IsIntervention"] = final["IsIntervention"].fillna(0).astype("Int64")

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)