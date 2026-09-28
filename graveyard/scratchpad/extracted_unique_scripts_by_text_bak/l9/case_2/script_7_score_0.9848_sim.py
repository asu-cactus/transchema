import pandas as pd

paths_group_0 = [
    "autopipeline-benchmarks/github-pipelines/length9_2/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_10.csv"
]

paths_group_1 = [
    "autopipeline-benchmarks/github-pipelines/length9_2/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_9.csv"
]

dfs_group_0 = [pd.read_csv(p, index_col=0) for p in paths_group_0]
dfs_group_1 = [pd.read_csv(p, index_col=0) for p in paths_group_1]

union_0 = pd.concat(dfs_group_0, ignore_index=True)
union_1 = pd.concat(dfs_group_1, ignore_index=True)

final_df = pd.concat([union_0, union_1], ignore_index=True)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_2/target_multisource_mcts.csv", index=False)