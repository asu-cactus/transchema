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

df_result = df_all[['Batsman on strike', 'overs', 'runs scored', 'extras']].copy()
df_result['Batsman on strike'] = df_result['Batsman on strike'].astype(str)
df_result['overs'] = pd.to_numeric(df_result['overs'], errors='coerce')
df_result['runs scored'] = pd.to_numeric(df_result['runs scored'], errors='coerce').fillna(0).astype(int)
df_result['extras'] = pd.to_numeric(df_result['extras'], errors='coerce').fillna(0).astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)