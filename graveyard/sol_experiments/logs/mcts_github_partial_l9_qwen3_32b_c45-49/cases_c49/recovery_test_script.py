import pandas as pd

dfs = [
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_0.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_1.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_2.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_3.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_4.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_5.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_6.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_7.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_8.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_9.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_10.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_11.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_12.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_13.csv", index_col=0),
    pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_49/test_14.csv", index_col=0),
]

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts_recovery_test_val.csv")