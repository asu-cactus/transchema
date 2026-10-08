import pandas as pd

source_files = [
    f"autopipeline-benchmarks/github-pipelines/length9_41/training_{i}.csv"
    for i in range(222)
]

dfs = [pd.read_csv(f, index_col=0) for f in source_files]
result = pd.concat(dfs, ignore_index=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_41/target_multisource_mcts.csv", index=False)