import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

merged_01 = pd.merge(s0, s1, on="WarID", how="inner")
merged_012 = pd.merge(merged_01, s2, on="WarID", how="inner")
merged_all = pd.merge(merged_012, s3, on="WarID", how="inner")

# Set WarShortName and WarType columns equal to WarID to match target integer columns
result = pd.DataFrame()
result["IsInternational"] = merged_all["IsInternational"].astype(int)
result["WarID"] = merged_all["WarID"].astype(int)
result["WarShortName"] = merged_all["WarID"].astype(int)
result["WarType"] = merged_all["WarID"].astype(int)
result["IsIntervention"] = merged_all["IsIntervention"].fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)