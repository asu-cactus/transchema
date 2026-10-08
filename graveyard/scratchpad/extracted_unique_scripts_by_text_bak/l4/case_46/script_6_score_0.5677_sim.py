import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

s0['IsInternational'] = pd.NA
s0['IsIntervention'] = pd.NA
s2['IsInternational'] = pd.NA
s2['IsIntervention'] = pd.NA

union_0_2 = pd.concat([s0, s2], ignore_index=True, sort=False)
union_0_2_1 = pd.concat([union_0_2, s1], ignore_index=True, sort=False)
union_all = pd.concat([union_0_2_1, s3], ignore_index=True, sort=False)

union_all['IsInternational'] = union_all['IsInternational'].fillna(0).astype(int)
union_all['IsIntervention'] = union_all['IsIntervention'].fillna(0).astype(int)
union_all['WarID'] = union_all['WarID'].astype(int)
union_all['WarShortName'] = union_all['WarShortName'].astype(str)
union_all['WarType'] = union_all['WarType'].astype(int)

warshortname_counts = union_all.groupby('WarShortName')['WarShortName'].transform('count')
union_all['WarShortName'] = warshortname_counts.astype(int)

result = union_all[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)