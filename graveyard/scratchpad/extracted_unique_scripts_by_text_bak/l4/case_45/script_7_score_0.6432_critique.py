import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_0_1 = pd.concat([s0, s1], ignore_index=True)

join_0_1 = pd.merge(union_0_1, s2[['WarID', 'IsIntervention']], on='WarID', how='left')

join_1_2 = pd.merge(join_0_1, s3[['WarID', 'IsInternational']], on='WarID', how='left')

# Replace NaN in IsInternational and IsIntervention with 0 (flags)
join_1_2['IsInternational'] = join_1_2['IsInternational'].fillna(0).astype(int)
join_1_2['IsIntervention'] = join_1_2['IsIntervention'].fillna(0).astype(int)

agg = join_1_2.groupby('WarType').agg(
    WarID=('WarID', 'count'),
    WarShortName=('WarShortName', 'count'),
    IsInternational=('IsInternational', 'sum'),
    IsIntervention=('IsIntervention', 'sum')
).reset_index()

agg = agg[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)