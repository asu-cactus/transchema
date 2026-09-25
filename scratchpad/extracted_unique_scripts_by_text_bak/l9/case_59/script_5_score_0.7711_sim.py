import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_59/training_16.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)
result = union_df.groupby('country', as_index=False)['cpi'].mean()
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_59/target_multisource_mcts.csv", index=False)