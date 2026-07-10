import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_5/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_all['code'] = df_all['code'].astype(int)
df_all['name'] = df_all['name'].astype(str)
df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_5/target_multisource_mcts.csv", index=False)