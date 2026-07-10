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

result = union_df.groupby('int_rate', as_index=False).size()
result.columns = ['int_rate', 'count']

result = result[['int_rate']]  # Target schema only requires 'int_rate' column

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_47/target_multisource_mcts.csv", index=False)