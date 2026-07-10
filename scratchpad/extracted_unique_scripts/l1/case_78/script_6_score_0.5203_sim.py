import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="Product")

result = df_joined[["Product", "Price_x"]].rename(columns={"Price_x": "Price"})
result["Price"] = result["Price"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)