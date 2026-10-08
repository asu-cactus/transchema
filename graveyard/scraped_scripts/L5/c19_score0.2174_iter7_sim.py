import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_19/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_19/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all['HD01_VD01'] = pd.to_numeric(df_all['HD01_VD01'], errors='coerce')
df_all['HD02_VD01'] = pd.to_numeric(df_all['HD02_VD01'], errors='coerce')
df_all['Year'] = pd.to_numeric(df_all['Year'], errors='coerce')

grouped = df_all.groupby(
    ['GEO.display-label', 'GEO.id', 'GEO.id2', 'Year'], dropna=False, as_index=False
).agg({
    'HD01_VD01': 'min',
    'HD02_VD01': 'min'
})

grouped['GEO.id'] = pd.to_numeric(grouped['GEO.id'], errors='coerce', downcast='integer')
grouped['GEO.id2'] = pd.to_numeric(grouped['GEO.id2'], errors='coerce', downcast='integer')
grouped['HD01_VD01'] = grouped['HD01_VD01'].astype('Int64')
grouped['HD02_VD01'] = grouped['HD02_VD01'].astype('Int64')
grouped['Year'] = grouped['Year'].astype('Int64')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_19/target_multisource_mcts.csv", index=False)