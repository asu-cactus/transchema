import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)

id_cols = ['zipcode', 'AGI_STUB', 'N1']
value_cols = [col for col in df.columns if col.startswith('A') and col[1:].isdigit()]

df_unpivot = df.melt(id_vars=id_cols, value_vars=value_cols, var_name='variable', value_name='value')

df_grouped = df_unpivot.groupby(['zipcode', 'AGI_STUB', 'N1', 'variable'], as_index=False)['value'].sum()

df_pivot = df_grouped.pivot_table(index=['zipcode', 'AGI_STUB', 'N1'], columns='variable', values='value', fill_value=0).reset_index()

df_pivot.columns.name = None

df_result = df_pivot.rename(columns={'A00100': 'A00100'})

df_result = df_result[['zipcode', 'AGI_STUB', 'N1', 'A00100']]

df_result = df_result.astype({'zipcode': int, 'AGI_STUB': int, 'N1': int, 'A00100': int})

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)