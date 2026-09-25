import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_union = pd.concat(dfs, ignore_index=True)
df_target = df_union[['fac_type', 'capacity']].copy()
df_target['fac_type'] = df_target['fac_type'].astype(str)
df_target['capacity'] = pd.to_numeric(df_target['capacity'], errors='coerce').fillna(0).astype(int)
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)