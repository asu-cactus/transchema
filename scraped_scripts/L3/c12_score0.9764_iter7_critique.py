import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_12/training_0.csv", index_col=0)

# Group by SN, aggregate Price by sum, count by number of rows per SN
df_grouped = df0.groupby('SN', as_index=False).agg({'Price': 'sum', 'Purchase ID': 'count'})

# Rename columns to match target schema
df_grouped.rename(columns={'Purchase ID': 'count'}, inplace=True)

# Ensure correct types
df_grouped['SN'] = df_grouped['SN'].astype(str)
df_grouped['Price'] = df_grouped['Price'].astype(float)
df_grouped['count'] = df_grouped['count'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_12/target_multisource_mcts.csv", index=False)