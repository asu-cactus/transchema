import pandas as pd

def load_source(file_path):
    return pd.read_csv(file_path, index_col=0)

sources = [
    "autopipeline-benchmarks/github-pipelines/length9_17/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/test_11.csv"
]

result = pd.concat([load_source(fp) for fp in sources], ignore_index=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_17/target_multisource_mcts_recovery_test_val.csv", index=False)