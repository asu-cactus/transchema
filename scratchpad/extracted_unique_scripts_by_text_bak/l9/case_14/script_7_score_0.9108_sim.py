import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_9.csv", index_col=0)

df = s0.merge(s1, on="Id", suffixes=("_x", "_y"))
df = df.merge(s2.rename(columns={"SalePrice": "SalePrice_x_3"}), on="Id")
df = df.merge(s3.rename(columns={"SalePrice": "SalePrice_y_4"}), on="Id")
df = df.merge(s4.rename(columns={"SalePrice": "SalePrice_x_5"}), on="Id")
df = df.merge(s5.rename(columns={"SalePrice": "SalePrice_y_6"}), on="Id")
df = df.merge(s6.rename(columns={"SalePrice": "SalePrice_x_7"}), on="Id")
df = df.merge(s7.rename(columns={"SalePrice": "SalePrice_y_8"}), on="Id")
df = df.merge(s8.rename(columns={"SalePrice": "SalePrice_x_9"}), on="Id")
df = df.merge(s9.rename(columns={"SalePrice": "SalePrice_y_10"}), on="Id")

df = df[[
    "Id",
    "SalePrice_x",
    "SalePrice_y",
    "SalePrice_x_3",
    "SalePrice_y_4",
    "SalePrice_x_5",
    "SalePrice_y_6",
    "SalePrice_x_7",
    "SalePrice_y_8",
    "SalePrice_x_9",
    "SalePrice_y_10"
]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_14/target_multisource_mcts.csv")