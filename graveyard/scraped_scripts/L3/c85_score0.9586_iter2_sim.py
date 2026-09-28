import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_3.csv", index_col=0)

df0_renamed = df0.rename(columns={"m1403": "value"})
df1_renamed = df1.rename(columns={"m1402": "value"})
df2_renamed = df2.rename(columns={"m1401": "value"})

df0_renamed["m"] = "m1403"
df1_renamed["m"] = "m1402"
df2_renamed["m"] = "m1401"

union_df = pd.concat([df0_renamed, df1_renamed, df2_renamed], ignore_index=True)

pivot_df = union_df.pivot_table(index="County", columns="m", values="value", aggfunc='first').reset_index()

result = pd.merge(df3, pivot_df, on="County", how="inner")

result = result[["County", "m1401", "m1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)