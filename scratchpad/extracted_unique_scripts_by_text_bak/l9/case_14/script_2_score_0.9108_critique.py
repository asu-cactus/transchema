import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_14/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_14/training_9.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Rename SalePrice columns to match target schema
dfs[0] = dfs[0].rename(columns={"SalePrice": "SalePrice_x"})
dfs[1] = dfs[1].rename(columns={"SalePrice": "SalePrice_y"})
dfs[2] = dfs[2].rename(columns={"SalePrice": "SalePrice_x_3"})
dfs[3] = dfs[3].rename(columns={"SalePrice": "SalePrice_y_4"})
dfs[4] = dfs[4].rename(columns={"SalePrice": "SalePrice_x_5"})
dfs[5] = dfs[5].rename(columns={"SalePrice": "SalePrice_y_6"})
dfs[6] = dfs[6].rename(columns={"SalePrice": "SalePrice_x_7"})
dfs[7] = dfs[7].rename(columns={"SalePrice": "SalePrice_y_8"})
dfs[8] = dfs[8].rename(columns={"SalePrice": "SalePrice_x_9"})
dfs[9] = dfs[9].rename(columns={"SalePrice": "SalePrice_y_10"})

# Start joining from first two tables
result = dfs[0].merge(dfs[1], on="Id", how="inner")

# Iteratively join the rest on Id
for df in dfs[2:]:
    result = result.merge(df, on="Id", how="inner")

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_14/target_multisource_mcts.csv", index=False)