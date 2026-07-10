import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="CUSTOMERNAME", suffixes=('_left', '_right'))

unioned = pd.concat([df0, df0], ignore_index=True)

result = unioned[["CUSTOMERNAME", "ORDERNUMBER", "QUANTITYORDERED"]].copy()

result["ORDERNUMBER"] = pd.to_numeric(result["ORDERNUMBER"], errors='coerce').fillna(0).astype(int)
result["QUANTITYORDERED"] = pd.to_numeric(result["QUANTITYORDERED"], errors='coerce').fillna(0).astype(int)
result["CUSTOMERNAME"] = result["CUSTOMERNAME"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)