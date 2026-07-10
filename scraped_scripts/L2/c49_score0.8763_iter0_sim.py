import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_1.csv", index_col=0)

df0_sub = df0[['fname']]
df1_sub = df1[['fname']]

df_union = pd.concat([df0_sub, df1_sub], ignore_index=True)

result = df_union.groupby('fname', as_index=False).size()
result.columns = ['fname', 'row_count']
result['row_count'] = result['row_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_49/target_multisource_mcts.csv", index=False)