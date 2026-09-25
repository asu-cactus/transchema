import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_64/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_result = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes as per target schema
union_result['admit'] = union_result['admit'].astype(int)
union_result['gre'] = union_result['gre'].astype(int)
union_result['gpa'] = union_result['gpa'].astype(float)
union_result['prestige'] = union_result['prestige'].astype(int)

union_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_64/target_multisource_mcts.csv", index=False)