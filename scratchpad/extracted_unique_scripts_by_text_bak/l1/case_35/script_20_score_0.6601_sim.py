import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)

agg = df0.groupby("Source Zipcode")["Counts"].agg(["min", "max"]).reset_index()
agg["Counts"] = agg[["min", "max"]].max(axis=1)
result = agg[["Source Zipcode", "Counts"]].copy()
result["Source Zipcode"] = result["Source Zipcode"].astype(int)
result["Counts"] = result["Counts"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)