import pandas as pd

paths_union = [
    "autopipeline-benchmarks/github-pipelines/length9_99/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_99/training_9.csv"
]

dfs_union = [pd.read_csv(p, index_col=0) for p in paths_union]
union_result = pd.concat(dfs_union, ignore_index=True)

source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_99/training_4.csv", index_col=0)

merged = pd.merge(
    source4,
    union_result,
    on=["admit", "gre", "gpa", "prestige"],
    how="inner"
)

Target9_99 = merged[["admit", "gre", "gpa", "prestige"]]

Target9_99.to_csv("autopipeline-benchmarks/github-pipelines/length9_99/target_multisource_mcts.csv", index=False)