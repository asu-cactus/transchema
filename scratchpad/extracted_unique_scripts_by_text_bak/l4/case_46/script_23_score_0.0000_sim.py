import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

agg = s1.groupby("IsInternational").agg(WarID_count=("WarID", "count"), IsIntervention_sum=("IsIntervention", "sum")).reset_index()

merged_01 = pd.merge(s0, s1, on="WarID", how="inner", suffixes=('_0', '_1'))
merged_012 = pd.merge(merged_01, s2, on="WarID", how="inner", suffixes=('', '_2'))
merged_all = pd.merge(merged_012, s3, on="WarID", how="inner", suffixes=('', '_3'))

merged_all["IsIntervention"] = merged_all["IsIntervention"].fillna(0).astype(int)
merged_all["IsInternational"] = merged_all["IsInternational"].fillna(0).astype(int)

result = merged_all[["IsInternational", "WarID", "WarShortName", "WarType", "IsIntervention"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)