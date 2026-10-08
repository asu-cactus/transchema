import pandas as pd

source_df = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length1_95/test_0.csv",
    index_col=0
)

# Perform GROUP_BY on customer_id and select first row per group
result_df = source_df.groupby("customer_id").first().reset_index()[["customer_id", "date"]]

# Save to target CSV
result_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts_recovery_test_val.csv", index=False)