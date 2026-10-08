import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

grouped = df0.groupby(
    ["provider_id", "provider_name", "provider_zip_code"], as_index=False
).agg({
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
})

grouped["provider_id"] = grouped["provider_id"].astype(int)
grouped["provider_zip_code"] = grouped["provider_zip_code"].astype(int)
grouped["provider_name"] = grouped["provider_name"].astype(str)
grouped["average_covered_charges"] = grouped["average_covered_charges"].astype(float)
grouped["average_total_payments"] = grouped["average_total_payments"].astype(float)
grouped["average_medicare_payments"] = grouped["average_medicare_payments"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)