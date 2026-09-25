import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

join_0_1 = pd.merge(s1, s0[['WarID']], on='WarID', how='inner')

union_1 = pd.concat([s0, s2], ignore_index=True, sort=False)
union_2 = pd.concat([union_1, s1], ignore_index=True, sort=False)
union_3 = pd.concat([union_2, s3], ignore_index=True, sort=False)

def to_int_or_zero(x):
    try:
        return int(x)
    except:
        return 0

df = union_3.copy()

df['IsIntervention'] = df['IsIntervention'].fillna(0).astype(int)
df['IsInternational'] = df['IsInternational'].fillna(0).astype(int)

df = df[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

df['WarShortName'] = pd.to_numeric(df['WarShortName'], errors='coerce').fillna(0).astype(int)
df['WarType'] = pd.to_numeric(df['WarType'], errors='coerce').fillna(0).astype(int)
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)