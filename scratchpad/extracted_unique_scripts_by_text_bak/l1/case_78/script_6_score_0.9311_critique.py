import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

grouped = df0.groupby("Product", as_index=False)["Price"].mean()

grouped["Product"] = grouped["Product"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)