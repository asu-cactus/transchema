import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

joined = pd.merge(df, df, on="provider_id", suffixes=('_left', '_right'))

agg = joined.groupby("provider_id").agg({
    "provider_name_left": "first",
    "provider_zip_code_left": "first",
    "average_covered_charges_left": "mean",
    "average_total_payments_left": "mean",
    "average_medicare_payments_left": "mean"
}).reset_index()

agg = agg.rename(columns={
    "provider_name_left": "provider_name",
    "provider_zip_code_left": "provider_zip_code",
    "average_covered_charges_left": "average_covered_charges",
    "average_total_payments_left": "average_total_payments",
    "average_medicare_payments_left": "average_medicare_payments"
})

agg["provider_id"] = agg["provider_id"].astype(int)
agg["provider_zip_code"] = agg["provider_zip_code"].astype(int)
agg["provider_name"] = agg["provider_name"].astype(str)
agg["average_covered_charges"] = agg["average_covered_charges"].astype(float)
agg["average_total_payments"] = agg["average_total_payments"].astype(float)
agg["average_medicare_payments"] = agg["average_medicare_payments"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)