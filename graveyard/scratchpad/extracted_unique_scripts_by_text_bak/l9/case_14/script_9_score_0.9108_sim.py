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

df = s2.merge(s3, on="Id", suffixes=('_x_3', '_y_4'))
df = df.merge(s4, on="Id").rename(columns={"SalePrice": "SalePrice_x_5"})
df = df.merge(s5, on="Id").rename(columns={"SalePrice": "SalePrice_y_6"})
df = df.merge(s6, on="Id").rename(columns={"SalePrice": "SalePrice_x_7"})
df = df.merge(s7, on="Id").rename(columns={"SalePrice": "SalePrice_y_8"})
df = df.merge(s8, on="Id").rename(columns={"SalePrice": "SalePrice_x_9"})
df = df.merge(s9, on="Id").rename(columns={"SalePrice": "SalePrice_y_10"})
df = df.merge(s0, on="Id").rename(columns={"SalePrice": "SalePrice_x"})
df = df.merge(s1, on="Id").rename(columns={"SalePrice": "SalePrice_y"})

df = df[['Id', 'SalePrice_x', 'SalePrice_y', 'SalePrice_x_3', 'SalePrice_y_4', 'SalePrice_x_5', 'SalePrice_y_6', 'SalePrice_x_7', 'SalePrice_y_8', 'SalePrice_x_9', 'SalePrice_y_10']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_14/target_multisource_mcts.csv", index=False)