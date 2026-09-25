import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)

df_union = df0[['Source Zipcode', 'Counts']]

df_grouped = df_union.groupby('Source Zipcode', as_index=False)['Counts'].sum()

df_grouped['Source Zipcode'] = df_grouped['Source Zipcode'].astype(int)
df_grouped['Counts'] = df_grouped['Counts'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)