import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)
df = df0[['neighbourhood', 'price']].copy()
df_agg = df.groupby('neighbourhood', as_index=False).mean()
df_agg.rename(columns={'price': 'price_24'}, inplace=True)
df_agg['price_24'] = df_agg['price_24'].astype(int)
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)