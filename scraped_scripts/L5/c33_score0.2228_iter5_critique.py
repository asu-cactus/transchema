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

# Convert columns to appropriate types
df['GEO.id2'] = df['GEO.id2'].astype(str)
df['GEO.id'] = pd.to_numeric(df['GEO.id'], errors='coerce').astype('Int64')
df['GEO.display-label'] = pd.to_numeric(df['GEO.display-label'], errors='coerce').astype('Int64')
df['HD01_VD01'] = pd.to_numeric(df['HD01_VD01'], errors='coerce').fillna(0).astype('Int64')
df['HD02_VD01'] = pd.to_numeric(df['HD02_VD01'], errors='coerce').fillna(0).astype('Int64')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

# Group by the leftmost columns that form the key in the target schema
group_cols = ['GEO.id2', 'GEO.id', 'GEO.display-label', 'Year']

agg_dict = {
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum'
}

df_grouped = df.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['GEO.id2', 'GEO.id', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_33/target_multisource_mcts.csv", index=False)