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

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    df = df.groupby("Id", as_index=False).agg({"SalePrice": "mean"})
    df = df.rename(columns={"SalePrice": f"SalePrice_{['x','y','x_3','y_4','x_5','y_6','x_7','y_8','x_9','y_10'][i]}"})
    dfs.append(df)

from functools import reduce
target_df = reduce(lambda left, right: pd.merge(left, right, on="Id", how="outer"), dfs)

target_df = target_df.astype({
    "Id": "int64",
    "SalePrice_x": "float64",
    "SalePrice_y": "float64",
    "SalePrice_x_3": "float64",
    "SalePrice_y_4": "float64",
    "SalePrice_x_5": "float64",
    "SalePrice_y_6": "float64",
    "SalePrice_x_7": "float64",
    "SalePrice_y_8": "float64",
    "SalePrice_x_9": "float64",
    "SalePrice_y_10": "float64",
})

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_14/target_multisource_mcts.csv", index=False)