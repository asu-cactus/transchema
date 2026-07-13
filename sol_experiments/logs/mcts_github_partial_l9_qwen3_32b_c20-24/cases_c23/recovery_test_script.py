import pandas as pd

source_paths = [
    "autopipeline-benchmarks/github-pipelines/length9_23/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_23/test_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_23/test_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_23/test_8.csv"
]

dfs = []
for path in source_paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df[["MONTHS_AGE"]])

combined = pd.concat(dfs, ignore_index=True)
result = combined.groupby("MONTHS_AGE").first().reset_index()
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts_recovery_test_val.csv", index=False)