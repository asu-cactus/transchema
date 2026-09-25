import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types matching target schema
df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = pd.to_numeric(df['GEO.id2'], errors='coerce').astype('Int64')
df['GEO.display-label'] = pd.to_numeric(df['GEO.display-label'], errors='coerce').astype('Int64')
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').astype('Int64')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').astype('Int64')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

# Drop rows with any NaN in key columns to ensure clean grouping
df = df.dropna(subset=['GEO.id', 'GEO.id2', 'GEO.display-label', 'Year'])

# Group by key columns and sum the numeric columns
group_cols = ['GEO.id', 'GEO.id2', 'GEO.display-label', 'Year']
agg_cols = ['HD01_VD01', 'HD02_VD01']

df = df.groupby(group_cols, as_index=False)[agg_cols].sum()

# Ensure all columns have correct types after aggregation
df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = df['GEO.id2'].astype('Int64')
df['GEO.display-label'] = df['GEO.display-label'].astype('Int64')
df['HD01_VD01'] = df['HD01_VD01'].astype('Int64')
df['HD02_VD01'] = df['HD02_VD01'].astype('Int64')
df['Year'] = df['Year'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv", index=False)