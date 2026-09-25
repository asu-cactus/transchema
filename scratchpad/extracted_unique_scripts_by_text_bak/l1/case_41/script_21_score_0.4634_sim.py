import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

df = df0.copy()

df_unpivot = df.melt(id_vars=['zipcode', 'AGI_STUB'], value_vars=['N1', 'A00100'], var_name='variable', value_name='value')

df_pivot = df_unpivot.pivot_table(index=['zipcode', 'AGI_STUB'], columns='variable', values='value', aggfunc='sum').reset_index()

df_pivot = df_pivot[['zipcode', 'AGI_STUB', 'N1', 'A00100']]

df_pivot['zipcode'] = df_pivot['zipcode'].astype('Int64')
df_pivot['AGI_STUB'] = df_pivot['AGI_STUB'].astype('Int64')
df_pivot['N1'] = df_pivot['N1'].astype('Int64')
df_pivot['A00100'] = df_pivot['A00100'].astype('Int64')

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)