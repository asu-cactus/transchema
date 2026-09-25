import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_81/training_0.csv", index_col=0)

agg = df0.groupby(["provider_zip_code", "provider_id"]).agg({
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
}).reset_index()

agg["provider_zip_code"] = agg["provider_zip_code"].astype(int)
agg["provider_id"] = agg["provider_id"].astype(float)
agg["average_covered_charges"] = agg["average_covered_charges"].astype(float)
agg["average_total_payments"] = agg["average_total_payments"].astype(float)
agg["average_medicare_payments"] = agg["average_medicare_payments"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_81/target_multisource_mcts.csv", index=False)