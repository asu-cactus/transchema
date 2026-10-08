import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_1.csv", index_col=0)
# ... read all source tables

df_all = pd.concat([df0, df1], ignore_index=True)
result = df_all.groupby("Source Zipcode", as_index=False)["Counts"].sum()
result["Source Zipcode"] = result["Source Zipcode"].astype(int)
result["Counts"] = result["Counts"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)