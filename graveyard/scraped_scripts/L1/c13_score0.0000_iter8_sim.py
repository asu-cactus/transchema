import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_13/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby(['sex', 'smoker'], as_index=False)['tip_pct'].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)