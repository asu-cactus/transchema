import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv", index_col=0)

join_01 = pd.merge(df0, df1, on=['WarNum', 'WhereFought'], how='inner', suffixes=('_0', '_1'))
join_012 = pd.merge(join_01[['WarNum', 'WhereFought']], df2, on=['WarNum', 'WhereFought'], how='inner')
join_0123 = pd.merge(join_012, df3, on=['WarNum', 'WhereFought'], how='inner')

result = join_0123[['WarNum', 'WhereFought']].copy()
result['WarNum'] = result['WarNum'].astype(int)
result['WhereFought'] = result['WhereFought'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)