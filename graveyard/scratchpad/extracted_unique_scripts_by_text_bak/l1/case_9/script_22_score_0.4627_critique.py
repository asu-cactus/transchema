import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

df_grouped = df0.groupby(["zipcode", "AGI_STUB"], as_index=False)[["N1", "A00100"]].sum()

df_grouped["zipcode"] = df_grouped["zipcode"].astype(int)
df_grouped["AGI_STUB"] = df_grouped["AGI_STUB"].astype(int)
df_grouped["N1"] = df_grouped["N1"].astype(int)
df_grouped["A00100"] = df_grouped["A00100"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)