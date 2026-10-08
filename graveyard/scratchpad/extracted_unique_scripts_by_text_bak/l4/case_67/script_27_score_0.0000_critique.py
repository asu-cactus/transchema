import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_67/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_67/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_67/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types
df_all['Batsman on strike'] = df_all['Batsman on strike'].astype(str)
df_all['runs scored'] = pd.to_numeric(df_all['runs scored'], errors='coerce').fillna(0).astype(int)
df_all['extras'] = pd.to_numeric(df_all['extras'], errors='coerce').fillna(0).astype(int)
df_all['overs'] = pd.to_numeric(df_all['overs'], errors='coerce')

# Group by 'Batsman on strike' and aggregate sum of runs scored and extras
df_grouped = df_all.groupby('Batsman on strike', as_index=False).agg({
    'overs': 'sum',  # overs is float, but target examples show overs aggregated (sum)
    'runs scored': 'sum',
    'extras': 'sum'
})

# Ensure column order matches target schema
df_result = df_grouped[['Batsman on strike', 'overs', 'runs scored', 'extras']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)