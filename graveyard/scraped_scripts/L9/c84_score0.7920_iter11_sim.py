import pandas as pd

paths_union = [
    "autopipeline-benchmarks/github-pipelines/length9_84/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_9.csv"
]

dfs_union = [pd.read_csv(p, index_col=0) for p in paths_union]
union_result = pd.concat(dfs_union, ignore_index=True)

df_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_84/training_8.csv", index_col=0)

merged = pd.merge(df_8, union_result, on=['admit', 'gre', 'gpa', 'prestige'], how='inner')

merged.to_csv("autopipeline-benchmarks/github-pipelines/length9_84/target_multisource_mcts.csv", index=False)