import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)
df_unpivot = df.melt(id_vars=['neighbourhood'], value_vars=['price'], var_name='price_24', value_name='price_24')
df_grouped = df_unpivot.groupby('neighbourhood', as_index=False)['price_24'].sum()
df_grouped['price_24'] = df_grouped['price_24'].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)