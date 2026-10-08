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

# The target schema is ['0'] with integer type, so ensure dtype is int
df_all = df_all.astype({'0': int})

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_37/target_multisource_mcts.csv", index=False)