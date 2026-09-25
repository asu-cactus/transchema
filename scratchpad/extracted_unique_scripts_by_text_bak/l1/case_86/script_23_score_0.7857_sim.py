import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

df_union = df0.copy()

df_pivot = df_union.groupby('neighbourhood', as_index=False)['price'].sum()
df_pivot.rename(columns={'price': 'price_24', 'neighbourhood': 'neighbourhood'}, inplace=True)
df_pivot['price_24'] = df_pivot['price_24'].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)