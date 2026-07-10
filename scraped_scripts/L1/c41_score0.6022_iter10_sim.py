import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv", index_col=0)
df_unpivot = df.melt(id_vars=['zipcode'], value_vars=['N1', 'A00100'], var_name='AGI_STUB', value_name='Value')
df_unpivot['AGI_STUB'] = df_unpivot['AGI_STUB'].map({'N1': 21, 'A00100': 21})  # From target examples AGI_STUB=21 for these columns
df_pivot = df_unpivot.pivot_table(index=['zipcode', 'AGI_STUB'], columns='AGI_STUB', values='Value', aggfunc='first').reset_index()
# The pivot_table columns are the unique AGI_STUB values, but here only 21, so columns will be [zipcode, AGI_STUB, 21]
# We want columns: zipcode, AGI_STUB, N1, A00100
# So instead of pivoting on AGI_STUB, we should pivot on variable name to get N1 and A00100 as columns

# Correct approach: after unpivot, AGI_STUB column contains 'N1' or 'A00100' as string, but target expects AGI_STUB as integer 21
# So we should keep AGI_STUB as integer 21, and pivot on variable name to get N1 and A00100 columns

# Let's redo unpivot with var_name='variable' and keep AGI_STUB as is, then pivot on 'variable'

df_unpivot = df.melt(id_vars=['zipcode', 'AGI_STUB'], value_vars=['N1', 'A00100'], var_name='variable', value_name='Value')
df_pivot = df_unpivot.pivot_table(index=['zipcode', 'AGI_STUB'], columns='variable', values='Value', aggfunc='first').reset_index()
df_pivot.columns.name = None

# Ensure columns are in target schema order and types
df_pivot = df_pivot[['zipcode', 'AGI_STUB', 'N1', 'A00100']]
df_pivot = df_pivot.astype({'zipcode': 'int64', 'AGI_STUB': 'int64', 'N1': 'int64', 'A00100': 'int64'})

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)