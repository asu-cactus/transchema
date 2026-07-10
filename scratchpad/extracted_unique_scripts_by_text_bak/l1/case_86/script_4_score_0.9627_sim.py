import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

df_union = df0.copy()

df_grouped = df_union.groupby("neighbourhood", as_index=False)["price"].mean()
df_grouped["price_24"] = df_grouped["price"].round().astype(int)
result = df_grouped[["neighbourhood", "price_24"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)