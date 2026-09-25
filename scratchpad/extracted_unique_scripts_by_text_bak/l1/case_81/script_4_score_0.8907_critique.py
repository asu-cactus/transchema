import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

# Convert provider_zip_code and provider_id to int for grouping keys
df0["provider_zip_code"] = df0["provider_zip_code"].astype(int)
df0["provider_id"] = df0["provider_id"].astype(int)

grouped = df0.groupby(["provider_zip_code", "provider_id"]).agg({
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
}).reset_index()

# Ensure types match target schema
grouped["provider_zip_code"] = grouped["provider_zip_code"].astype(int)
grouped["provider_id"] = grouped["provider_id"].astype(float)  # target has float for provider_id
grouped["average_covered_charges"] = grouped["average_covered_charges"].astype(float)
grouped["average_total_payments"] = grouped["average_total_payments"].astype(float)
grouped["average_medicare_payments"] = grouped["average_medicare_payments"].astype(float)

# Reorder columns as per target schema
grouped = grouped[["provider_zip_code", "provider_id", "average_covered_charges", "average_total_payments", "average_medicare_payments"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)