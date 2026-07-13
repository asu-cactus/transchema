import pandas as pd

# Load source data
source1_87_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/test_0.csv", index_col=0)

# Perform GROUP BY aggregation
result = source1_87_0.groupby("condition", as_index=False).agg({"click": "mean"})

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts_recovery_test_val.csv", index=False)