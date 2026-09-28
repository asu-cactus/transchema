import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

df_result = df0[['Product', 'Price']].copy()
df_result['Product'] = df_result['Product'].astype(str)
df_result['Price'] = df_result['Price'].astype(float)

df_grouped = df_result.groupby('Product', as_index=False).agg({'Price': 'mean'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)