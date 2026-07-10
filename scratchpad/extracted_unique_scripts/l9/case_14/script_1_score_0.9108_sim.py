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

grouped = []
for df in dfs:
    g = df.groupby("Id", as_index=False).agg({"SalePrice": "mean"})
    grouped.append(g)

result = grouped[0].rename(columns={"SalePrice": "SalePrice_x"})
result = result.merge(grouped[1].rename(columns={"SalePrice": "SalePrice_y"}), on="Id", how="inner")
result = result.merge(grouped[2].rename(columns={"SalePrice": "SalePrice_x_3"}), on="Id", how="inner")
result = result.merge(grouped[3].rename(columns={"SalePrice": "SalePrice_y_4"}), on="Id", how="inner")
result = result.merge(grouped[4].rename(columns={"SalePrice": "SalePrice_x_5"}), on="Id", how="inner")
result = result.merge(grouped[5].rename(columns={"SalePrice": "SalePrice_y_6"}), on="Id", how="inner")
result = result.merge(grouped[6].rename(columns={"SalePrice": "SalePrice_x_7"}), on="Id", how="inner")
result = result.merge(grouped[7].rename(columns={"SalePrice": "SalePrice_y_8"}), on="Id", how="inner")
result = result.merge(grouped[8].rename(columns={"SalePrice": "SalePrice_x_9"}), on="Id", how="inner")
result = result.merge(grouped[9].rename(columns={"SalePrice": "SalePrice_y_10"}), on="Id", how="inner")

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_14/target_multisource_mcts.csv", index=False)