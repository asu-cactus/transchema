import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

df_grouped = df0.groupby(['zipcode', 'AGI_STUB'], as_index=False).agg({'N1': 'sum', 'A00100': 'sum'})

df_grouped['zipcode'] = df_grouped['zipcode'].astype('Int64')
df_grouped['AGI_STUB'] = df_grouped['AGI_STUB'].astype('Int64')
df_grouped['N1'] = df_grouped['N1'].astype('Int64')
df_grouped['A00100'] = df_grouped['A00100'].astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)