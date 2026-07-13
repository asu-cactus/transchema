import pandas as pd

dfs = [
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_0.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_1.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_2.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_3.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_4.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_5.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_6.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_7.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_8.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_94/test_9.csv", index_col=0)
]

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv("autopipeline-benchmarks/github-pipelines/length9_94/target_multisource_mcts_recovery_test_val.csv")