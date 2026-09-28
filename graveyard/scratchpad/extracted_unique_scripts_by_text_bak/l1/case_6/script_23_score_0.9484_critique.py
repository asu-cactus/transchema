import pandas as pd

# Read the single source table (only one source given)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)

# If there were multiple source tables, we would read and union them here.
# Since only one source is given, union is trivial.

# Group by provider_id and aggregate accordingly
agg = df0.groupby("provider_id").agg({
    "provider_name": "first",
    "provider_zip_code": "first",
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
}).reset_index()

# Cast columns to target schema types
agg["provider_id"] = agg["provider_id"].astype(int)
agg["provider_name"] = agg["provider_name"].astype(str)
agg["provider_zip_code"] = agg["provider_zip_code"].astype(int)
agg["average_covered_charges"] = agg["average_covered_charges"].astype(float)
agg["average_total_payments"] = agg["average_total_payments"].astype(float)
agg["average_medicare_payments"] = agg["average_medicare_payments"].astype(float)

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)