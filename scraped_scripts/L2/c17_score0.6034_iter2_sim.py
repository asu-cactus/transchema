import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

agg_df1 = df1.groupby("state", as_index=False).agg({
    "Broadband Initiative": "sum",
    "Federal": "sum",
    "Percent": "mean"
})

merged = pd.merge(agg_df1, df0[["state", "population"]], on="state", how="left")

# population is integer, convert if needed
merged["population"] = merged["population"].astype("Int64")

merged = merged[["Broadband Initiative", "Federal", "Percent", "state", "population"]]

merged.to_csv(target_path, index=False)