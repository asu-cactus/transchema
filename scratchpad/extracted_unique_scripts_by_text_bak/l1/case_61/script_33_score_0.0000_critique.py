import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_9.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables (concatenate)
df_union = pd.concat(dfs, ignore_index=True)

# Group by the leftmost non-float columns in target schema
group_by_cols = ["provider_id", "provider_name", "provider_zip_code"]

# Aggregate float columns by mean
agg_cols = ["average_covered_charges", "average_total_payments", "average_medicare_payments"]

df_result = df_union.groupby(group_by_cols, as_index=False)[agg_cols].mean()

# Ensure correct dtypes as per target schema
df_result["provider_id"] = df_result["provider_id"].astype(int)
df_result["provider_zip_code"] = df_result["provider_zip_code"].astype(int)
df_result["provider_name"] = df_result["provider_name"].astype(str)
df_result["average_covered_charges"] = df_result["average_covered_charges"].astype(float)
df_result["average_total_payments"] = df_result["average_total_payments"].astype(float)
df_result["average_medicare_payments"] = df_result["average_medicare_payments"].astype(float)

# Reorder columns exactly as target schema
df_result = df_result[
    [
        "provider_id",
        "provider_name",
        "provider_zip_code",
        "average_covered_charges",
        "average_total_payments",
        "average_medicare_payments",
    ]
]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)