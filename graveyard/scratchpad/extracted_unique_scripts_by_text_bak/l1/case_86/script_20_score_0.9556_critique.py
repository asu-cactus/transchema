import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

# Clean neighbourhood strings by stripping whitespace
df0['neighbourhood'] = df0['neighbourhood'].str.strip()

# Project relevant columns
df_proj = df0[['neighbourhood', 'id']]

# Group by neighbourhood and count listings (id)
df_grouped = df_proj.groupby('neighbourhood', as_index=False).agg({'id': 'count'})

# Rename count to price_24
df_grouped = df_grouped.rename(columns={'id': 'price_24'})

# Cast price_24 to int
df_grouped['price_24'] = df_grouped['price_24'].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)