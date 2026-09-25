import pandas as pd
from functools import reduce

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

# Corresponding target column names for SalePrice columns in order of sources
target_saleprice_cols = [
    "SalePrice_x",
    "SalePrice_y",
    "SalePrice_x_3",
    "SalePrice_y_4",
    "SalePrice_x_5",
    "SalePrice_y_6",
    "SalePrice_x_7",
    "SalePrice_y_8",
    "SalePrice_x_9",
    "SalePrice_y_10",
]

dfs = []
for i, path in enumerate(paths):
    # Read CSV with index_col=0 to ignore the first index column
    df = pd.read_csv(path, index_col=0)
    # No groupby needed since Id is unique in each source
    # Rename SalePrice column to target column name
    df = df.rename(columns={"SalePrice": target_saleprice_cols[i]})
    dfs.append(df)

# Perform successive inner joins on 'Id' to keep only common Ids
target_df = reduce(lambda left, right: pd.merge(left, right, on="Id", how="inner"), dfs)

# Ensure correct dtypes
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