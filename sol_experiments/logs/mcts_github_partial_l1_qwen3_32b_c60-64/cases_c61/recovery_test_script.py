import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/test_0.csv", index_col=0)
grouped = df.groupby(
    ["provider_id", "provider_name", "provider_zip_code"],
    as_index=False
).agg({
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
})
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts_recovery_test_val.csv", index=False)