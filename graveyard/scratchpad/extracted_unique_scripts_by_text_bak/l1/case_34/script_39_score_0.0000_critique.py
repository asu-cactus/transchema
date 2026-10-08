import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_34/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_34/training_2.csv', index_col=0)

# Rename columns to a common name
df0 = df0.rename(columns={'J_CALL': 'V_GENE'})
df1 = df1.rename(columns={'J_CALL': 'V_GENE'})
df2 = df2.rename(columns={'J_CALL': 'V_GENE'})

# Join on the index (row number) to align rows
df_joined = df0.join(df1, lsuffix='_0', rsuffix='_1').join(df2, rsuffix='_2')

# Since target schema has only one column V_GENE, and examples match df0's V_GENE,
# we output df0's V_GENE column as the final result.
df_result = df0[['V_GENE']]

df_result.to_csv('autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv', index=False)