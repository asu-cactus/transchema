import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)

agg = df0.groupby("Source Zipcode")["Counts"].sum().reset_index()

agg["Source Zipcode"] = agg["Source Zipcode"].astype(int)
agg["Counts"] = agg["Counts"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)