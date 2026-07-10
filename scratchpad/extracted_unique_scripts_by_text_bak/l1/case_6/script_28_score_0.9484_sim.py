import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="provider_id", suffixes=('_left', '_right'))

grouped = joined.groupby("provider_id").agg({
    "provider_name_left": "first",
    "provider_zip_code_left": "first",
    "average_covered_charges_left": "mean",
    "average_total_payments_left": "mean",
    "average_medicare_payments_left": "mean"
}).reset_index()

result = grouped.rename(columns={
    "provider_name_left": "provider_name",
    "provider_zip_code_left": "provider_zip_code",
    "average_covered_charges_left": "average_covered_charges",
    "average_total_payments_left": "average_total_payments",
    "average_medicare_payments_left": "average_medicare_payments"
})

result["provider_id"] = result["provider_id"].astype(int)
result["provider_name"] = result["provider_name"].astype(str)
result["provider_zip_code"] = result["provider_zip_code"].astype(int)
result["average_covered_charges"] = result["average_covered_charges"].astype(float)
result["average_total_payments"] = result["average_total_payments"].astype(float)
result["average_medicare_payments"] = result["average_medicare_payments"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)