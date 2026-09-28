import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_76/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={"Description": "Description_x"})
df1_renamed = df1.rename(columns={"Description": "Description_y"})

merged = pd.merge(df0_renamed, df1_renamed, on="Code", how="inner")

grouped = merged.groupby(["Code", "Description_x", "Description_y"], as_index=False).agg({"Rank": "max"})

grouped = grouped.astype({"Code": "int64", "Rank": "int64", "Description_x": "string", "Description_y": "string"})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_76/target_multisource_mcts.csv", index=False)