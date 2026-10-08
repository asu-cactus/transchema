import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_61/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all['start'] = df_all['start'].astype(str)
df_all['betterliving'] = df_all['betterliving'].astype(int)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_61/target_multisource_mcts.csv", index=False)