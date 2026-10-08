import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_84/training_4.csv", index_col=0)

agg_df0 = df0.groupby(['age_grp', 'Statistics'], dropna=False).agg({
    'Rate': 'sum',
    'Count': 'min'
}).reset_index()

union_df = pd.concat([agg_df0, df1, df2, df3, df4], ignore_index=True, sort=False)

cols = ['age_grp', 'Count', 'Notes', 'Rate', 'Statistics']
result = union_df[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts.csv", index=False)