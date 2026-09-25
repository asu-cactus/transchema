import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)
union_result = pd.concat([s0, s4], ignore_index=True)

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
join_result_1 = pd.merge(union_result, s3, on="County", how="outer")

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s2, on="County", how="outer")

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
final_df = pd.merge(join_result_2, s1, on="County", how="outer")

final_df = final_df.rename(columns={"r1403": "r1403_x"})
final_df["r1403_y"] = final_df["r1403_x"]

final_df = final_df[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)