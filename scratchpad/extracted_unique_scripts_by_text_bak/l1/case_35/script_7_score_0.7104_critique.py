import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)
df0["Source Zipcode"] = df0["Source Zipcode"].astype(int)
result = df0.groupby("Source Zipcode", as_index=False)["Counts"].sum()
result["Counts"] = result["Counts"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)