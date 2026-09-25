import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_grouped = df_all.groupby(['WhereFought', 'WarNum'], as_index=False).size()
df_grouped.columns = ['WhereFought', 'WarNum', 'Count']

df_result = df_grouped[['WhereFought', 'WarNum']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)