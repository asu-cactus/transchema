import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_33/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_33/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert numeric columns, coercing errors to NaN
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

# GEO.id and GEO.display-label are strings in source, convert to numeric for aggregation
df['GEO.id'] = pd.to_numeric(df['GEO.id'], errors='coerce')
df['GEO.display-label'] = pd.to_numeric(df['GEO.display-label'], errors='coerce')

# GEO.id2 is string, keep as string
df['GEO.id2'] = df['GEO.id2'].astype(str)

# Group by GEO.id2, aggregate as per plan
grouped = df.groupby('GEO.id2', dropna=False, as_index=False).agg({
    'GEO.id': 'max',
    'GEO.display-label': 'max',
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum',
    'Year': 'max'
})

# Fill NaNs with 0 for numeric columns and convert to int
grouped['GEO.id'] = grouped['GEO.id'].fillna(0).astype(int)
grouped['GEO.display-label'] = grouped['GEO.display-label'].fillna(0).astype(int)
grouped['HD01_VD01'] = grouped['HD01_VD01'].fillna(0).astype(int)
grouped['HD02_VD01'] = grouped['HD02_VD01'].fillna(0).astype(int)
grouped['Year'] = grouped['Year'].fillna(0).astype(int)

# Reorder columns to match target schema
grouped = grouped[['GEO.id2', 'GEO.id', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_33/target_multisource_mcts.csv", index=False)