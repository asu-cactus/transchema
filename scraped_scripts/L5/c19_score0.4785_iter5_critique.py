import pandas as pd
import re

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_19/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

# Extract integer GEO.id from GEO.id string, e.g. "8600000US43529" -> 43529
def extract_geo_id(geo_id_str):
    if pd.isna(geo_id_str):
        return 0
    match = re.search(r'(\d+)$', str(geo_id_str))
    if match:
        return int(match.group(1))
    else:
        return 0

df_all['GEO.id'] = df_all['GEO.id'].apply(extract_geo_id)

df_all['GEO.id2'] = pd.to_numeric(df_all['GEO.id2'], errors='coerce').fillna(0).astype(int)
df_all['Year'] = pd.to_numeric(df_all['Year'], errors='coerce').fillna(0).astype(int)
df_all['HD01_VD01'] = pd.to_numeric(df_all['HD01_VD01'], errors='coerce').fillna(0).astype(int)
df_all['HD02_VD01'] = pd.to_numeric(df_all['HD02_VD01'], errors='coerce').fillna(0).astype(int)
df_all['GEO.display-label'] = df_all['GEO.display-label'].astype(str)

grouped = df_all.groupby(
    ['GEO.display-label', 'GEO.id', 'GEO.id2', 'Year'], dropna=False, as_index=False
).agg({
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum'
})

# Ensure types match target schema exactly
grouped = grouped.astype({
    'GEO.display-label': str,
    'GEO.id': int,
    'GEO.id2': int,
    'Year': int,
    'HD01_VD01': int,
    'HD02_VD01': int
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_19/target_multisource_mcts.csv", index=False)