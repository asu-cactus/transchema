import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

df_all = df_all[df_all['age_grp'].notna()]

agg = df_all.groupby('age_grp').agg(
    Count=('Count', 'count'),
    Rate=('Rate', 'mean')
).reset_index()

agg['Count'] = agg['Count'].astype(float)
agg['Notes'] = pd.NA
agg['Statistics'] = pd.NA

agg = agg[['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)