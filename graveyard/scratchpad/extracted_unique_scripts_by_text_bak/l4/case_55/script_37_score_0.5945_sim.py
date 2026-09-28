import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_grouped = df_all.groupby(['WarNum', 'WhereFought'], as_index=False).size()

df_grouped = df_grouped.rename(columns={'size': 'Count'})

df_result = df_grouped[['WarNum', 'WhereFought']].copy()
df_result['WarNum'] = df_result['WarNum'].astype(int)
df_result['WhereFought'] = df_result['WhereFought'].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)