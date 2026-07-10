import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

# Convert columns to proper types
df_all['GEO.id'] = df_all['GEO.id'].astype(str)
df_all['GEO.id2'] = pd.to_numeric(df_all['GEO.id2'], errors='coerce').astype('Int64')
df_all['Year'] = pd.to_numeric(df_all['Year'], errors='coerce').astype('Int64')
df_all['HD01_VD01'] = pd.to_numeric(df_all['HD01_VD01'], errors='coerce').fillna(0).astype(int)
df_all['HD02_VD01'] = pd.to_numeric(df_all['HD02_VD01'], errors='coerce').fillna(0).astype(int)

# Group by key columns and aggregate value columns
df_grouped = df_all.groupby(['GEO.id', 'GEO.id2', 'Year'], dropna=False, as_index=False).agg({
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum'
})

# Add constant column GEO.display-label = 5 (as per target examples)
df_grouped['GEO.display-label'] = 5

# Reorder columns to match target schema
df_grouped = df_grouped[['GEO.id', 'GEO.id2', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

df_grouped.to_csv(
    "autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv",
    index=False
)