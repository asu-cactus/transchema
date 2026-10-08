import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_01 = pd.concat([s0, s1], ignore_index=True)

join_1 = pd.merge(union_01, s2[['WarID', 'IsIntervention']], on='WarID', how='left')

join_2 = pd.merge(join_1, s3[['WarID', 'IsInternational']], on='WarID', how='left')

result = join_2[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

for col in ['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']:
    if result[col].dtype != 'int64':
        result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)