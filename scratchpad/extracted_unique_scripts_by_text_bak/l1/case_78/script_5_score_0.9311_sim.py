import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="Product")

grouped = joined.groupby("Product", as_index=False)["Price_x"].mean()
grouped.rename(columns={"Price_x": "Price"}, inplace=True)
grouped["Product"] = grouped["Product"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)