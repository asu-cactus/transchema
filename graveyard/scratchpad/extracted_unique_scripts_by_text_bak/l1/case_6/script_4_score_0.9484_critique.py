import pandas as pd

# List all source files (assuming 6 source files as per naming pattern)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_5.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by provider_id and aggregate
grouped = df_all.groupby("provider_id").agg({
    "provider_name": "first",
    "provider_zip_code": "first",
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
}).reset_index()

# Cast columns to target schema types
grouped["provider_id"] = grouped["provider_id"].astype(int)
grouped["provider_name"] = grouped["provider_name"].astype(str)
grouped["provider_zip_code"] = grouped["provider_zip_code"].astype(int)
grouped["average_covered_charges"] = grouped["average_covered_charges"].astype(float)
grouped["average_total_payments"] = grouped["average_total_payments"].astype(float)
grouped["average_medicare_payments"] = grouped["average_medicare_payments"].astype(float)

# Reorder columns exactly as target schema
grouped = grouped[
    [
        "provider_id",
        "provider_name",
        "provider_zip_code",
        "average_covered_charges",
        "average_total_payments",
        "average_medicare_payments"
    ]
]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)