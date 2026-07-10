import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)

# Drop rows with missing provider_id or provider_name (essential keys)
df0 = df0.dropna(subset=["provider_id", "provider_name"])

# Group by provider_id
agg_df = df0.groupby("provider_id").agg({
    "provider_name": "first",
    "provider_zip_code": "first",
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
}).reset_index()

# Convert types to match target schema
agg_df["provider_id"] = agg_df["provider_id"].astype(int)

# provider_zip_code may be string with leading zeros, convert to int safely
# Some zip codes might be missing or malformed, so convert with errors='coerce' and drop NaNs
agg_df["provider_zip_code"] = pd.to_numeric(agg_df["provider_zip_code"], errors='coerce')
agg_df = agg_df.dropna(subset=["provider_zip_code"])
agg_df["provider_zip_code"] = agg_df["provider_zip_code"].astype(int)

agg_df["provider_name"] = agg_df["provider_name"].astype(str)
agg_df["average_covered_charges"] = agg_df["average_covered_charges"].astype(float)
agg_df["average_total_payments"] = agg_df["average_total_payments"].astype(float)
agg_df["average_medicare_payments"] = agg_df["average_medicare_payments"].astype(float)

# Reorder columns to match target schema
agg_df = agg_df[[
    "provider_id",
    "provider_name",
    "provider_zip_code",
    "average_covered_charges",
    "average_total_payments",
    "average_medicare_payments"
]]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)