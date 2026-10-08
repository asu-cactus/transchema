import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_1.csv", index_col=0)

# Inner join on 'fname' to keep only 'fname's present in Source1
df_joined = pd.merge(df1[['fname']], df0[['fname', 'Slice n°']], on='fname', how='inner')

# Group by 'fname' and count the number of rows from Source0 (count of 'Slice n°')
result = df_joined.groupby('fname', as_index=False).agg(row_count=('Slice n°', 'count'))

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_49/target_multisource_mcts.csv", index=False)