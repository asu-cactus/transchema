import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_37/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_37/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('0', as_index=False).size().rename(columns={'size': '0'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_37/target_multisource_mcts.csv", index=False)