import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

# Aggregate Source2_17_0 by state summing population
agg_df0 = df0.groupby("state", as_index=False).agg({
    "population": "sum"
})

# Aggregate Source2_17_1 by state summing Broadband Initiative and Federal, averaging Percent
agg_df1 = df1.groupby("state", as_index=False).agg({
    "Broadband Initiative": "sum",
    "Federal": "sum",
    "Percent": "mean"
})

# Join aggregated tables on state
merged = pd.merge(agg_df1, agg_df0, on="state", how="inner")

# Ensure population is integer type
merged["population"] = merged["population"].astype("Int64")

# Reorder columns to match target schema
merged = merged[["Broadband Initiative", "Federal", "Percent", "state", "population"]]

merged.to_csv(target_path, index=False)