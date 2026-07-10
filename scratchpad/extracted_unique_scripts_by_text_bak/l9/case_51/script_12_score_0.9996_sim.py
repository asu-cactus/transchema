import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_51/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_51/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_all['title'] = df_all['title'].astype(int)
df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_51/target_multisource_mcts.csv", index=False)