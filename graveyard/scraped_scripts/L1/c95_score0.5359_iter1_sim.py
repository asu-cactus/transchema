import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
df_target = df_union[['customer_id', 'date']].copy()
df_target['customer_id'] = df_target['customer_id'].astype(int)
df_target['date'] = df_target['date'].astype(str)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)