import pandas as pd

source_paths = [
    "autopipeline-benchmarks/github-pipelines/length9_88/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/test_9.csv"
]

dfs = []
for path in source_paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_88/target_multisource_mcts_recovery_test_val.csv")