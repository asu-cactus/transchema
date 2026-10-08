import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

df0['neighbourhood'] = df0['neighbourhood'].str.strip()

df_grouped = df0.groupby('neighbourhood', as_index=False)['price'].sum()
df_grouped.rename(columns={'price': 'price_24'}, inplace=True)
df_grouped['price_24'] = df_grouped['price_24'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)