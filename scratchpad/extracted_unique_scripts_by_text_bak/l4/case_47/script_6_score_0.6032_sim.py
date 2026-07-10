import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

join_0 = pd.merge(s3, s0, on="WarID", suffixes=('_3', '_0'))
join_0 = join_0[['IsInternational', 'WarID', 'WarShortName_0', 'WarType_0']]
join_0 = join_0.rename(columns={'WarShortName_0': 'WarShortName', 'WarType_0': 'WarType'})

union_1 = pd.concat([s0, s2], ignore_index=True)
union_1['IsInternational'] = 0

final_union = pd.concat([union_1, join_0], ignore_index=True)

final_union['IsIntervention'] = 0
final_union = final_union[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

final_union.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)