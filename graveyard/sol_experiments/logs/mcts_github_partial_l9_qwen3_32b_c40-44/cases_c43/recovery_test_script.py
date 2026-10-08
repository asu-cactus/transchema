import pandas as pd
from pandas import DataFrame, concat
from functools import reduce

# Read all source files
sources = [f"Source9_43_{i}" for i in range(222)]
dfs = [pd.read_csv(f"autopipeline-benchmarks/github-pipelines/length9_43/training_{i}.csv", index_col=0) for i in range(222)]

# Perform UNION on all sources
union_df = reduce(lambda left, right: pd.concat([left, right], ignore_index=True), dfs)

# Write the result to the target file
union_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_43/target_multisource_mcts_recovery_test_val.csv", index=False)