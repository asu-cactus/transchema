import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_48/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_48/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
result = pd.concat(dfs, ignore_index=True)
result = result.drop_duplicates(subset=['sub_grade'])
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_48/target_multisource_mcts.csv", index=False)