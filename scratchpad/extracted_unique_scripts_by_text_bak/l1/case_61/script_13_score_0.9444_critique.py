import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

agg_df = df.groupby("provider_id", as_index=False).agg({
    "provider_name": "first",
    "provider_zip_code": "first",
    "average_covered_charges": "mean",
    "average_total_payments": "mean",
    "average_medicare_payments": "mean"
})

agg_df["provider_id"] = agg_df["provider_id"].astype(int)
agg_df["provider_zip_code"] = agg_df["provider_zip_code"].astype(int)
agg_df["provider_name"] = agg_df["provider_name"].astype(str)
agg_df["average_covered_charges"] = agg_df["average_covered_charges"].astype(float)
agg_df["average_total_payments"] = agg_df["average_total_payments"].astype(float)
agg_df["average_medicare_payments"] = agg_df["average_medicare_payments"].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)