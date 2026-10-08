import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_19/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types matching target schema
df['GEO.display-label'] = df['GEO.display-label'].astype(str)
df['GEO.id'] = pd.to_numeric(df['GEO.id'], errors='coerce').astype('Int64')
df['GEO.id2'] = pd.to_numeric(df['GEO.id2'], errors='coerce').astype('Int64')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').fillna(0).astype('Int64')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').fillna(0).astype('Int64')

# Group by the key columns and aggregate sums for the numeric columns
result = df.groupby(
    ['GEO.display-label', 'GEO.id', 'GEO.id2', 'Year'], dropna=False, as_index=False
).agg({
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum'
})

# Ensure column order matches target schema
result = result[['GEO.display-label', 'GEO.id', 'GEO.id2', 'HD01_VD01', 'HD02_VD01', 'Year']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_19/target_multisource_mcts.csv", index=False)