import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="neighbourhood", suffixes=('', '_dup'))

grouped = joined.groupby("neighbourhood", as_index=False)["price"].sum()

grouped.rename(columns={"price": "price_24"}, inplace=True)
grouped["price_24"] = grouped["price_24"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)