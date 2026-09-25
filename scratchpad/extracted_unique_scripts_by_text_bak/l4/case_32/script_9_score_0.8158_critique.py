import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)

# Join s3 and s2 on County
join_32_3_2 = pd.merge(s3, s2, on="County", how="outer")

# Join the above with s0 (r1403) on County
join_32_3_2_0 = pd.merge(join_32_3_2, s0, on="County", how="outer", suffixes=('', '_s0'))

# Join the above with s4 (r1403) on County
join_all_r = pd.merge(join_32_3_2_0, s4, on="County", how="outer", suffixes=('', '_s4'))

# Join with s1 (County only) to ensure all counties are included
final_join = pd.merge(join_all_r, s1, on="County", how="outer")

# Rename r1403 columns to match target schema
# s0's r1403 is currently 'r1403_s0' after merge suffix, s4's r1403 is 'r1403'
final_join = final_join.rename(columns={"r1403": "r1403_x", "r1403_s0": "r1403_y"})

# Select and reorder columns exactly as target schema
result = final_join[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)