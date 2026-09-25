import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, left_on="ORDERNUMBER", right_on="ORDERNUMBER")

result = df_joined[["CUSTOMERNAME_x", "ORDERNUMBER", "QUANTITYORDERED_x"]].copy()
result.columns = ["CUSTOMERNAME", "ORDERNUMBER", "QUANTITYORDERED"]

result["ORDERNUMBER"] = pd.to_numeric(result["ORDERNUMBER"], errors='coerce').astype('Int64')
result["QUANTITYORDERED"] = pd.to_numeric(result["QUANTITYORDERED"], errors='coerce').astype('Int64')
result["CUSTOMERNAME"] = result["CUSTOMERNAME"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)