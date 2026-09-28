import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

df = pd.merge(src0, src2[['WarID','IsIntervention']], on='WarID', how='left')
df = pd.merge(df, src3[['WarID','IsInternational']], on='WarID', how='left')
df = pd.merge(df, src1[['WarID']], on='WarID', how='left', indicator=True)

df['IsInternational'] = df['IsInternational'].fillna(0).astype(int)
df['IsIntervention'] = df['IsIntervention'].fillna(0).astype(int)
df['WarShortName'] = df['WarShortName'].astype(int, errors='ignore')
df['WarType'] = df['WarType'].astype(int)
df['WarID'] = df['WarID'].astype(int)

df = df[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)