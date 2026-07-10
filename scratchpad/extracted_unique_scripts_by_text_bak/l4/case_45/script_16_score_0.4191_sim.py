import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

s0['IsInternational'] = pd.NA
s0['IsIntervention'] = pd.NA
s1['IsInternational'] = pd.NA
s1['IsIntervention'] = pd.NA

union_0_1 = pd.concat([s0, s1], ignore_index=True)

s2['IsInternational'] = pd.NA
s3['IsIntervention'] = pd.NA

union_all = pd.concat([union_0_1, s2, s3], ignore_index=True)

union_all['IsInternational'] = union_all['IsInternational'].fillna(0).astype(int)
union_all['IsIntervention'] = union_all['IsIntervention'].fillna(0).astype(int)

union_all['WarType'] = union_all['WarType'].astype(int)
union_all['WarID'] = union_all['WarID'].astype(int)
union_all['WarShortName'] = union_all['WarShortName'].astype(str)

union_all['WarShortName'] = union_all['WarShortName'].apply(lambda x: sum(ord(c) for c in x))

result = union_all[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)