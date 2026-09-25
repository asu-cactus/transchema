import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_65/training_1.csv", index_col=0)

# Count rows per fname in Source0
df0_counts = df0.groupby('fname').size().reset_index(name='row_count_0')

# Count rows per fname in Source1
df1_counts = df1.groupby('fname').size().reset_index(name='row_count_1')

# Join on fname to combine counts from both sources
df_joined = pd.merge(df0_counts, df1_counts, on='fname', how='inner')

# Sum counts from both sources to get final row_count
df_joined['row_count'] = df_joined['row_count_0'] + df_joined['row_count_1']

# Select only required columns with correct names
df_final = df_joined[['fname', 'row_count']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length2_65/target_multisource_mcts.csv", index=False)