import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)

union_df = pd.concat([df0, df4], ignore_index=True)
union_df = union_df.rename(columns={"r1403": "r1403_x"})
union_df["r1403_y"] = union_df["r1403_x"]

join_1 = pd.merge(union_df, df2, on="County", how="outer")
join_2 = pd.merge(join_1, df3, on="County", how="outer")
final_df = pd.merge(join_2, df1, on="County", how="outer")

final_df = final_df[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

final_df = final_df.groupby(["County", "r1401", "r1402", "r1403_x", "r1403_y"], as_index=False).size()

final_df = final_df.drop(columns=["size"])

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)