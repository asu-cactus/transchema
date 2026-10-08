import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=["zipcode", "AGI_STUB"], value_vars=["N1", "A00100"], var_name="variable", value_name="value")

df_grouped = df_unpivot.groupby(["zipcode", "AGI_STUB", "variable"], as_index=False).sum()

df_pivot = df_grouped.pivot(index=["zipcode", "AGI_STUB"], columns="variable", values="value").reset_index()

df_pivot["zipcode"] = df_pivot["zipcode"].astype(int)
df_pivot["AGI_STUB"] = df_pivot["AGI_STUB"].astype(int)
df_pivot["N1"] = df_pivot["N1"].astype(int)
df_pivot["A00100"] = df_pivot["A00100"].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)