import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_47/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_47/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)

# Output exactly the unioned data with the same column name 'int_rate'
union_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_47/target_multisource_mcts.csv", index=False)