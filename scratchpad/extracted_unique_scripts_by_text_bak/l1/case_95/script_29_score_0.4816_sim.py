import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

df_union = pd.concat([df0[['customer_id', 'date']], df0[['customer_id', 'date']]], ignore_index=True)

df_union['customer_id'] = df_union['customer_id'].astype(int)
df_union['date'] = df_union['date'].astype(str)

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)