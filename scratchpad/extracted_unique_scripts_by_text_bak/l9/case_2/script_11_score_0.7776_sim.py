import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_2/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_2/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

union_df = pd.concat(dfs, ignore_index=True)

result = union_df.groupby('0', as_index=False).size().rename(columns={'size': '0'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_2/target_multisource_mcts.csv", index=False)