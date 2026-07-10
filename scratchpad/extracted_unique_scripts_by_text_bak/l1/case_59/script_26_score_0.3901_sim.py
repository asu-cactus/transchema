import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="PRODUCTLINE")

result = df_joined[["PRODUCTLINE", "SALES_x"]].copy()
result.columns = ["PRODUCTLINE", "SALES"]
result["PRODUCTLINE"] = result["PRODUCTLINE"].astype(str)
result["SALES"] = pd.to_numeric(result["SALES"], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)