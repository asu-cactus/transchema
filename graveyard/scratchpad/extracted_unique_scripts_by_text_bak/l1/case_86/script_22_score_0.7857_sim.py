import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)
df_proj = df0[['neighbourhood', 'price']]
df_grouped = df_proj.groupby('neighbourhood', as_index=False).agg({'price': 'sum'})
df_grouped = df_grouped.rename(columns={'price': 'price_24'})
df_grouped['price_24'] = df_grouped['price_24'].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)