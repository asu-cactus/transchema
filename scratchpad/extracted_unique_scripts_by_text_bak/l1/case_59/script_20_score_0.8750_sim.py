import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="PRODUCTLINE")

result = joined.groupby("PRODUCTLINE", as_index=False)["SALES_x"].sum()
result.columns = ["PRODUCTLINE", "SALES"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)