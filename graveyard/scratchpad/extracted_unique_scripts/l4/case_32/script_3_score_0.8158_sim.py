import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)

join_32_3_2 = pd.merge(s3, s2, on="County", how="outer")
join_32_3_2_0 = pd.merge(join_32_3_2, s0, on="County", how="outer", suffixes=('_x', '_y'))
final_join = pd.merge(join_32_3_2_0, s4, on="County", how="outer", suffixes=('', '_y'))

final_join = final_join.rename(columns={"r1403_x": "r1403_x", "r1403_y": "r1403_y"})

# After merges, columns from s0 and s4 both have 'r1403' columns, one is renamed to r1403_x, the other to r1403_y
# The join_32_3_2_0 merge used suffixes _x and _y, so s0's r1403 became r1403_y, s4's r1403 remains r1403 (renamed to r1403_y in next merge)
# To avoid confusion, rename columns explicitly:
final_join = final_join.rename(columns={"r1403": "r1403_y", "r1403_y": "r1403_x"})

# Select and reorder columns to match target schema
result = final_join[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv")