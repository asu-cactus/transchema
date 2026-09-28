import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

join_2_3 = pd.merge(s2, s3, on="WarID", suffixes=('_2', '_3'))

union_0_1 = pd.concat([s0, s1], ignore_index=True)

final = pd.merge(union_0_1, join_2_3, on="WarID", how="inner")

result = final[["WarType_2", "WarID", "WarShortName_2", "IsInternational", "IsIntervention"]].copy()
result.columns = ['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)