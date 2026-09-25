import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_64/training_0.csv", index_col=0)

df_join = pd.merge(df0, df0, on="customer_id", suffixes=('_x', '_y'))

df_join['avg_amount_spent'] = (df_join['amount_x'] + df_join['amount_y']) / 2
df_join = df_join[['customer_id', 'amount_x', 'amount_y', 'avg_amount_spent']]

df_join['amount_x'] = df_join['amount_x'].astype(int)
df_join['amount_y'] = df_join['amount_y'].astype(float)
df_join['avg_amount_spent'] = df_join['avg_amount_spent'].astype(float)

df_join.to_csv("autopipeline-benchmarks/github-pipelines/length3_64/target_multisource_mcts.csv", index=False)