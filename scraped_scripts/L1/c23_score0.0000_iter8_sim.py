import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_23/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_23/training_2.csv', index_col=0)

df_all = pd.concat([df0, df1, df2], ignore_index=True)
df_all = df_all[['customer_id', 'amount']]
df_all['customer_id'] = df_all['customer_id'].astype(int)
df_all['amount'] = df_all['amount'].astype(float)

df_all.to_csv('autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv', index=False)