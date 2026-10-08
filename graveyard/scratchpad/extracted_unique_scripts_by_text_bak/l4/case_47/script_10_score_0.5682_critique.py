import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

# Add missing IsIntervention column to s0 and s2 with default 0 (assuming no intervention)
s0["IsIntervention"] = 0
s2["IsIntervention"] = 0

# Select columns to union (all must have same columns)
cols = ["WarID", "WarShortName", "WarType", "IsIntervention"]

# Union s0, s1, s2
unioned = pd.concat([s0[cols], s1[cols], s2[cols]], ignore_index=True)

# Join unioned with s3 on WarID to get IsInternational
result = pd.merge(unioned, s3[["WarID", "IsInternational"]], on="WarID", how="left")

# Fill missing IsInternational with 0 (assuming no international info means 0)
result["IsInternational"] = result["IsInternational"].fillna(0).astype(int)

# Ensure IsIntervention is integer
result["IsIntervention"] = result["IsIntervention"].astype(int)

# Reorder columns as per target schema
result = result[["IsIntervention", "WarID", "WarShortName", "WarType", "IsInternational"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)