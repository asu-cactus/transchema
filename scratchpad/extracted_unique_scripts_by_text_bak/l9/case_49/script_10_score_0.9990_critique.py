import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_49/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_49/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Union all source tables vertically
result = pd.concat(dfs, ignore_index=True)

# Ensure emp_title is integer type as target schema
result['emp_title'] = result['emp_title'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_49/target_multisource_mcts.csv", index=False)