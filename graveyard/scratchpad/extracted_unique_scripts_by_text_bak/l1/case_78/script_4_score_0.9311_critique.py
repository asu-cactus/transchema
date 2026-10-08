import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

df_target = df0.groupby('Product', as_index=False).agg({'Price': 'mean'})

df_target['Product'] = df_target['Product'].astype(str)
df_target['Price'] = df_target['Price'].astype(float)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)