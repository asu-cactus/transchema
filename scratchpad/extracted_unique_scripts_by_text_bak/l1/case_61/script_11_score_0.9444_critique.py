import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

agg = df.groupby("provider_id").agg({
    "provider_name": "first",
    "provider_zip_code": "first",
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
}).reset_index()

agg["provider_id"] = agg["provider_id"].astype(int)
agg["provider_zip_code"] = agg["provider_zip_code"].astype(int)
agg["provider_name"] = agg["provider_name"].astype(str)
agg["average_covered_charges"] = agg["average_covered_charges"].astype(float)
agg["average_total_payments"] = agg["average_total_payments"].astype(float)
agg["average_medicare_payments"] = agg["average_medicare_payments"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)