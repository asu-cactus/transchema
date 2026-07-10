import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_85/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_85/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

# Ensure column types match target schema
df_all = df_all.astype({
    "admit": "int64",
    "gre": "int64",
    "gpa": "float64",
    "prestige": "int64"
})

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_85/target_multisource_mcts.csv", index=False)